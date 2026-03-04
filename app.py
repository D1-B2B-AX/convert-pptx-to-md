import os
import re
import json
import tempfile
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from pptx import Presentation
from dotenv import load_dotenv

from utils.pptx_parser import (
    generate_doc_id, group_slides_into_courses, strip_code_fences
)
from extract_curriculum_store_v2 import generate_curriculum_store_markdown
from extract_module_store_v2 import generate_module_store_json

load_dotenv()

app = FastAPI(title="Curriculum Dual Store API")


def build_module_store_files(filename, course_idx, doc_id, parsed):
    """모듈 스토어 파일 목록을 메모리에서 생성하여 반환합니다."""
    files = []

    course_name = parsed.get('courseName', '정보 없음')
    client_name = parsed.get('client', '정보 없음')
    industry = parsed.get('industry', '기타')
    target_role = parsed.get('targetRole', '')
    level = parsed.get('level', '')
    total_duration = parsed.get('totalDuration', '')
    total_days = parsed.get('totalDays', 0)
    tools_used = parsed.get('toolsUsed', '')
    education_format = parsed.get('educationFormat', '')
    domain = parsed.get('domain', '')
    skill_category = parsed.get('skillCategory', '')
    skill_id = parsed.get('skillId', '')
    overview_summary = parsed.get('overviewSummary', '')
    roadmap = parsed.get('roadmap', '')

    # --- course_overview.md ---
    overview_lines = [
        f"# {client_name}: {course_name}",
        f"docId: {doc_id}",
        f"sourceFile: {filename}",
        f"client: {client_name}",
        f"industry: {industry}",
        f"targetRole: {target_role}",
        f"level: {level}",
        f"duration: {total_duration} ({total_days}일)",
        f"toolsUsed: {tools_used}",
        f"educationFormat: {education_format}",
        f"domain: {domain}",
        f"skillCategory: {skill_category}",
        f"skillId: {skill_id}",
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
        mi = mod.get('moduleIndex', 0)
        name = mod.get('moduleName', '')
        dur = mod.get('duration', '')
        overview_lines.append(f"- {day}일차 M{mi:02d}: {name} ({dur})")

    overview_meta = {
        "docId": doc_id,
        "sourceFile": filename,
        "courseName": course_name,
        "client": client_name,
        "industry": industry,
        "targetRole": target_role,
        "level": level,
        "totalDuration": total_duration,
        "totalDays": total_days,
        "toolsUsed": tools_used,
        "educationFormat": education_format,
        "domain": domain,
        "skillCategory": skill_category,
        "skillId": skill_id,
    }
    files.append({
        "filename": "course_overview.md",
        "content": '\n'.join(overview_lines),
        "metadata": overview_meta,
    })

    # --- 모듈별 파일 ---
    for mod in parsed.get('modules', []):
        day = mod.get('day', 0)
        mi = mod.get('moduleIndex', 0)
        module_name = mod.get('moduleName', 'unknown')
        module_summary = mod.get('moduleSummary', '')
        duration = mod.get('duration', '')
        mod_tools_used = mod.get('toolsUsed', '')
        mod_education_format = mod.get('educationFormat', '')
        mod_domain = mod.get('domain', '')
        mod_skill_category = mod.get('skillCategory', '')
        mod_skill_id = mod.get('skillId', '')
        objectives = mod.get('objectives', [])
        details = mod.get('details', [])
        practices = mod.get('practices', [])

        safe_name = re.sub(r'[^a-zA-Z0-9가-힣]', '_', module_name)
        safe_name = re.sub(r'_+', '_', safe_name).strip('_').lower()
        md_filename = f"d{day:02d}_m{mi:02d}_{safe_name}.md"

        mod_doc_id = f"{doc_id}::m{mi:02d}"
        lines = [
            f"# [MODULE] {module_name}",
            f"docId: {mod_doc_id}",
            f"sourceFile: {filename}",
            f"client: {client_name}",
            f"industry: {industry}",
            f"targetRole: {target_role if target_role else '정보 없음'}",
            f"level: {level}",
            f"duration: {duration}",
            f"toolsUsed: {mod_tools_used if mod_tools_used else '정보 없음'}",
            f"educationFormat: {mod_education_format}",
            f"domain: {mod_domain}",
            f"skillCategory: {mod_skill_category}",
            f"skillId: {mod_skill_id}",
            "",
            "## 모듈 요약",
            module_summary,
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
            "docId": mod_doc_id,
            "sourceFile": filename,
            "client": client_name,
            "industry": industry,
            "targetRole": target_role,
            "level": level,
            "duration": duration,
            "toolsUsed": mod_tools_used,
            "educationFormat": mod_education_format,
            "domain": mod_domain,
            "skillCategory": mod_skill_category,
            "skillId": mod_skill_id,
            "moduleName": module_name,
            "moduleSummary": module_summary,
            "day": day,
            "moduleIndex": mi,
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
