import os
import re
import json
import tempfile
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from pptx import Presentation
from openai import OpenAI
from dotenv import load_dotenv

from utils.pptx_parser import (
    generate_doc_id, group_slides_into_courses, strip_code_fences
)
from extract_curriculum_store import generate_curriculum_store_markdown
from extract_module_store import generate_module_store_json

load_dotenv()

app = FastAPI(title="Curriculum Dual Store API")
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def build_module_store_files(filename, course_idx, doc_id, parsed):
    """모듈 스토어 파일 목록을 메모리에서 생성하여 반환합니다."""
    files = []

    course_name = parsed.get('course_name', '정보 없음')
    client_name = parsed.get('client', '정보 없음')
    industry = parsed.get('industry', '기타')
    topic = parsed.get('topic', '')
    target = parsed.get('target', '')
    level = parsed.get('level', '')
    total_duration = parsed.get('total_duration', '')
    total_days = parsed.get('total_days', 0)
    tools = parsed.get('tools', '')
    fmt = parsed.get('format', '')
    overview_summary = parsed.get('overview_summary', '')
    roadmap = parsed.get('roadmap', '')

    # --- course_overview.md ---
    overview_lines = [
        f"# {client_name}: {course_name}",
        f"DOC_ID: {doc_id}",
        f"CLIENT: {client_name}",
        f"INDUSTRY: {industry}",
        f"TOPIC: {topic}",
        f"TARGET: {target}",
        f"LEVEL: {level}",
        f"DURATION: {total_duration} ({total_days}일)",
        f"TOOLS: {tools}",
        f"FORMAT: {fmt}",
        f"SOURCE_FILE: {filename}",
        "",
        "## 교육 개요",
        overview_summary,
        "",
        "## 로드맵",
        roadmap,
        "",
        "## 모듈 목록",
    ]
    for mod in parsed.get('modules', []):
        day = mod.get('day', 0)
        mi = mod.get('module_index', 0)
        name = mod.get('module_name', '')
        dur = mod.get('duration', '')
        overview_lines.append(f"- {day}일차 M{mi:02d}: {name} ({dur})")

    overview_meta = {
        "doc_id": doc_id,
        "doc_type": "course_overview",
        "course_name": course_name,
        "client": client_name,
        "industry": industry,
        "topic": topic,
        "target": target,
        "level": level,
        "total_duration": total_duration,
        "total_days": total_days,
        "tools": tools,
        "format": fmt,
        "source_file": filename,
    }
    files.append({
        "filename": "course_overview.md",
        "content": '\n'.join(overview_lines),
        "metadata": overview_meta,
    })

    # --- 모듈별 파일 ---
    for mod in parsed.get('modules', []):
        day = mod.get('day', 0)
        mi = mod.get('module_index', 0)
        module_name = mod.get('module_name', 'unknown')
        module_summary = mod.get('module_summary', '')
        duration = mod.get('duration', '')
        mod_tools = mod.get('tools', '')
        objectives = mod.get('objectives', [])
        details = mod.get('details', [])
        practices = mod.get('practices', [])

        safe_name = re.sub(r'[^a-zA-Z0-9가-힣]', '_', module_name)
        safe_name = re.sub(r'_+', '_', safe_name).strip('_').lower()
        md_filename = f"d{day:02d}_m{mi:02d}_{safe_name}.md"

        lines = [
            f"# {client_name}: {course_name}",
            f"{day}일차 | {total_duration} | {industry} | {level}",
            "",
            f"## {module_name}",
            f"MODULE_SUMMARY: {module_summary}",
            f"DURATION: {duration}",
            f"TOOLS: {mod_tools if mod_tools else '-'}",
            "",
        ]
        if objectives:
            lines.append("### 학습목표")
            for obj in objectives:
                lines.append(f"- {obj}")
            lines.append("")
        if details:
            lines.append("### 세부내용")
            for det in details:
                lines.append(f"- {det}")
            lines.append("")
        if practices:
            lines.append("### 실습")
            for prac in practices:
                lines.append(f"- {prac}")
            lines.append("")

        mod_meta = {
            "doc_id": f"{doc_id}::m{mi:02d}",
            "doc_type": "module",
            "course_name": course_name,
            "client": client_name,
            "industry": industry,
            "module_name": module_name,
            "module_summary": module_summary,
            "day": day,
            "module_index": mi,
            "duration": duration,
            "tools": mod_tools,
            "level": level,
            "source_file": filename,
        }
        files.append({
            "filename": md_filename,
            "content": '\n'.join(lines),
            "metadata": mod_meta,
        })

    return files


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
            "module_store": [],
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

        # Module store
        parsed = generate_module_store_json(
            file.filename, idx + 1, full_overview, full_curriculum
        )
        if parsed:
            course_result["module_store"] = build_module_store_files(
                file.filename, idx + 1, doc_id, parsed
            )

        results.append(course_result)

    return {"source_file": file.filename, "courses": results}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
