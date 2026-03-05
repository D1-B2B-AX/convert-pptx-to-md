import os
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from pptx import Presentation
from dotenv import load_dotenv

from utils.pptx_parser import (
    generate_doc_id, group_slides_into_courses, strip_code_fences
)
from extract_curriculum_store_v2 import generate_curriculum_store_markdown

load_dotenv()

app = FastAPI(title="Curriculum Store API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    if not file.filename.endswith('.pptx'):
        raise HTTPException(400, "Only .pptx files are supported")

    content = await file.read()
    try:
        prs = Presentation(BytesIO(content))
    except Exception as e:
        raise HTTPException(400, f"Failed to parse PPTX: {e}")

    courses = group_slides_into_courses(prs)
    if not courses:
        return {"source_file": file.filename, "courses": []}

    results = []
    for idx, course in enumerate(courses):
        full_overview = "\n\n".join(course['overview'])
        full_curriculum = "\n\n".join(course['curriculum'])
        doc_id = generate_doc_id(file.filename, idx + 1)

        course_result = {
            "doc_id": doc_id,
            "curriculum_store": None,
        }

        # Curriculum store
        md_content, metadata = generate_curriculum_store_markdown(
            file.filename, idx + 1, full_overview, full_curriculum
        )
        if md_content and metadata:
            course_result["curriculum_store"] = {
                "content": md_content,
                "metadata": metadata,
            }

        results.append(course_result)

    return {"source_file": file.filename, "courses": results}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
