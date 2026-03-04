import os
import re
import json
from pptx import Presentation
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.pptx_parser import (
    generate_doc_id, group_slides_into_courses, strip_code_fences
)

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"

SOURCE_DIR = './input'
OUTPUT_DIR = './output/module_store'
SKILL_CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'skill_catalog_260226_v1.md')


def load_skill_catalog():
    """스킬 카탈로그 파일을 읽어 반환합니다."""
    with open(SKILL_CATALOG_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def generate_module_store_json(filename, course_idx, overview_text, curriculum_text):
    """Gemini에 JSON 스키마를 전달하여 모듈별 구조화 데이터를 반환받습니다."""
    if len(curriculum_text) < 50:
        return None

    doc_id = generate_doc_id(filename, course_idx)
    skill_catalog = load_skill_catalog()

    prompt = f"""당신은 B2B 교육 제안서에서 커리큘럼을 분석하여 모듈별 구조화된 JSON으로 변환하는 전문가입니다.

[Input]
- File: {filename}
- Course Index: {course_idx}
- DOC_ID: {doc_id}
- Overview: {overview_text[:5000]}
- Curriculum: {curriculum_text[:25000]}

[스킬 카탈로그 - SKILL_ID 매칭 참조용]
{skill_catalog}

[SKILL_ID 매칭 지침]
- 과정 전체 수준: 위 스킬 카탈로그에서 이 과정의 핵심 내용과 가장 가까운 대표 스킬 1개를 선택하십시오.
- 모듈 수준: 각 모듈마다 해당 모듈의 구체적 내용과 가장 일치하는 스킬 ID를 개별적으로 선택하십시오. 모듈마다 서로 다른 skill_id를 가질 수 있습니다.
- skill_id 필드에 해당 스킬의 ID를 정확히 기입하십시오 (예: G-T001, G-R001, D-M003 등).
- skill_category는 선택한 skill_id의 카테고리 접두사입니다 (예: G-T, G-M, D-A 등).
- domain은 skill_id가 G-로 시작하면 GenAI, D-로 시작하면 MLDL입니다.

[Task]
위 Raw Text를 분석하여 아래 JSON 스키마에 정확히 맞는 JSON을 출력하십시오.

[Critical Rules]
1. 없는 정보를 지어내지 마십시오. 추출할 수 없는 필드는 빈 문자열("")로 적으십시오.
2. 강사 약력, 회사 홍보, 레퍼런스(유사 사례) 등 커리큘럼과 무관한 내용은 제거하십시오.
3. 유효한 커리큘럼 정보가 없으면 오직 {{"no_data": true}} 라고만 출력하십시오.
4. modules 배열의 각 항목은 반드시 회차(day)와 모듈 순번(module_index)을 포함해야 합니다.
5. 실습이 없는 모듈은 practices를 빈 배열([])로 적으십시오.

[JSON Schema]
{{
  "course_name": "과정명",
  "client": "고객사명 (파일명이나 본문에서 추출)",
  "industry": "산업군 (금융/제조/IT/통신/유통/공공/에너지/의료/교육/기타)",
  "target_role": "교육 대상 직무",
  "level": "초급 / 기초 / 중급 / 고급 중 택 1",
  "total_duration": "총 교육 시수 (예: 21H)",
  "total_days": 3,
  "tools_used": "사용되는 AI 도구/기술 (쉼표 구분)",
  "education_format": "특강/데모형 / 이론/개념 전달형 / 실습/툴 마스터형 / 프로젝트/PoC형 / 워크숍/문제 해결형 중 택 1",
  "domain": "GenAI 또는 MLDL (대표 스킬 기준)",
  "skill_category": "대표 스킬의 카테고리 (G-T, G-M, G-R, G-A, G-C, D-T, D-M, D-A, D-C)",
  "skill_id": "과정 전체의 대표 스킬 ID 1개",
  "overview_summary": "교육의 배경, 목적, 학습 목표를 2~4문장으로 요약",
  "roadmap": "과정 전체 흐름을 1~2문장으로 요약",
  "modules": [
    {{
      "day": 1,
      "module_index": 1,
      "module_name": "모듈명",
      "module_summary": "이 모듈이 무엇을 다루는지 1줄 요약",
      "duration": "2H",
      "tools_used": "이 모듈에서 사용하는 도구 (없으면 빈 문자열)",
      "education_format": "이 모듈의 교육 형태 (5가지 중 택 1)",
      "skill_id": "이 모듈의 핵심 내용과 가장 일치하는 스킬 ID 1개",
      "skill_category": "skill_id의 카테고리",
      "domain": "skill_id가 G-이면 GenAI, D-이면 MLDL",
      "objectives": ["학습목표1", "학습목표2"],
      "details": ["핵심 학습 포인트1", "핵심 학습 포인트2"],
      "practices": ["실습 활동1"]
    }}
  ]
}}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json"
            )
        )
        result = response.text.strip()
        parsed = json.loads(result)

        if parsed.get("no_data"):
            return None
        if not parsed.get("modules"):
            return None

        return parsed

    except Exception as e:
        print(f"  ❌ LLM Error: {e}")
        return None


def save_module_store(filename, course_idx, doc_id, parsed):
    """모듈별 개별 파일 + course_overview.md + metadata JSON을 저장합니다."""
    safe_id = re.sub(r'[^a-zA-Z0-9가-힣_]', '_', doc_id.replace('CURR::', ''))
    course_dir = os.path.join(OUTPUT_DIR, safe_id)
    metadata_dir = os.path.join(course_dir, 'metadata')
    os.makedirs(metadata_dir, exist_ok=True)

    course_name = parsed.get('course_name', '정보 없음')
    client_name = parsed.get('client', '정보 없음')
    industry = parsed.get('industry', '기타')
    target_role = parsed.get('target_role', '')
    level = parsed.get('level', '')
    total_duration = parsed.get('total_duration', '')
    total_days = parsed.get('total_days', 0)
    tools_used = parsed.get('tools_used', '')
    education_format = parsed.get('education_format', '')
    domain = parsed.get('domain', '')
    skill_category = parsed.get('skill_category', '')
    skill_id = parsed.get('skill_id', '')
    overview_summary = parsed.get('overview_summary', '')
    roadmap = parsed.get('roadmap', '')

    # --- course_overview.md ---
    overview_lines = [
        f"# {client_name}: {course_name}",
        f"DOC_ID: {doc_id}",
        f"SOURCE_FILE: {filename}",
        f"CLIENT: {client_name}",
        f"INDUSTRY: {industry}",
        f"TARGET_ROLE: {target_role}",
        f"LEVEL: {level}",
        f"DURATION: {total_duration} ({total_days}일)",
        f"TOOLS_USED: {tools_used}",
        f"EDUCATION_FORMAT: {education_format}",
        f"DOMAIN: {domain}",
        f"SKILL_CATEGORY: {skill_category}",
        f"SKILL_ID: {skill_id}",
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

    overview_path = os.path.join(course_dir, 'course_overview.md')
    with open(overview_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(overview_lines))
    print(f"    ✅ {os.path.basename(overview_path)}")

    # --- course_overview metadata ---
    overview_meta = {
        "doc_id": doc_id,
        "source_file": filename,
        "course_name": course_name,
        "client": client_name,
        "industry": industry,
        "target_role": target_role,
        "level": level,
        "total_duration": total_duration,
        "total_days": total_days,
        "tools_used": tools_used,
        "education_format": education_format,
        "domain": domain,
        "skill_category": skill_category,
        "skill_id": skill_id,
    }
    meta_path = os.path.join(metadata_dir, 'course_overview.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(overview_meta, f, ensure_ascii=False, indent=2)

    # --- 모듈별 파일 ---
    for mod in parsed.get('modules', []):
        day = mod.get('day', 0)
        mi = mod.get('module_index', 0)
        module_name = mod.get('module_name', 'unknown')
        module_summary = mod.get('module_summary', '')
        duration = mod.get('duration', '')
        mod_tools_used = mod.get('tools_used', '')
        mod_education_format = mod.get('education_format', '')
        mod_domain = mod.get('domain', '')
        mod_skill_category = mod.get('skill_category', '')
        mod_skill_id = mod.get('skill_id', '')
        objectives = mod.get('objectives', [])
        details = mod.get('details', [])
        practices = mod.get('practices', [])

        # 파일명 생성: d{NN}_m{NN}_{name}.md
        safe_name = re.sub(r'[^a-zA-Z0-9가-힣]', '_', module_name)
        safe_name = re.sub(r'_+', '_', safe_name).strip('_').lower()
        md_filename = f"d{day:02d}_m{mi:02d}_{safe_name}.md"

        # 모듈 내용
        mod_doc_id = f"{doc_id}::m{mi:02d}"
        lines = [
            f"# [MODULE] {module_name}",
            f"DOC_ID: {mod_doc_id}",
            f"SOURCE_FILE: {filename}",
            f"CLIENT: {client_name}",
            f"INDUSTRY: {industry}",
            f"TARGET_ROLE: {target_role if target_role else '정보 없음'}",
            f"LEVEL: {level}",
            f"DURATION: {duration}",
            f"TOOLS_USED: {mod_tools_used if mod_tools_used else '정보 없음'}",
            f"EDUCATION_FORMAT: {mod_education_format}",
            f"DOMAIN: {mod_domain}",
            f"SKILL_CATEGORY: {mod_skill_category}",
            f"SKILL_ID: {mod_skill_id}",
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

        mod_path = os.path.join(course_dir, md_filename)
        with open(mod_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"    ✅ {md_filename}")

        # 모듈 metadata
        mod_meta = {
            "doc_id": f"{doc_id}::m{mi:02d}",
            "source_file": filename,
            "client": client_name,
            "industry": industry,
            "target_role": target_role,
            "level": level,
            "duration": duration,
            "tools_used": mod_tools_used,
            "education_format": mod_education_format,
            "domain": mod_domain,
            "skill_category": mod_skill_category,
            "skill_id": mod_skill_id,
            "module_name": module_name,
            "module_summary": module_summary,
            "day": day,
            "module_index": mi,
        }
        meta_key = f"d{day:02d}_m{mi:02d}"
        mod_meta_path = os.path.join(metadata_dir, f"{meta_key}.json")
        with open(mod_meta_path, 'w', encoding='utf-8') as f:
            json.dump(mod_meta, f, ensure_ascii=False, indent=2)

    return len(parsed.get('modules', []))


def process_module_store(source_dir=None):
    """모듈 스토어 메인 파이프라인."""
    src = source_dir or SOURCE_DIR
    if not os.path.exists(src):
        print(f"❌ 원본 폴더를 찾을 수 없습니다: {src}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = [f for f in os.listdir(src) if f.endswith('.pptx')]
    print(f"🚀 총 {len(files)}개의 제안서 -> [모듈 스토어] 변환 시작 (Gemini)...\n")

    for file in files:
        file_path = os.path.join(src, file)
        print(f"📄 분석 중: {file}")

        try:
            prs = Presentation(file_path)
            courses = group_slides_into_courses(prs)
            print(f"  └─ 잠재 과정 수: {len(courses)}개")

            for idx, course in enumerate(courses):
                full_overview = "\n\n".join(course['overview'])
                full_curriculum = "\n\n".join(course['curriculum'])
                doc_id = generate_doc_id(file, idx + 1)

                parsed = generate_module_store_json(
                    file, idx + 1, full_overview, full_curriculum
                )

                if parsed:
                    count = save_module_store(file, idx + 1, doc_id, parsed)
                    print(f"    📦 과정 {idx+1}: {count}개 모듈 저장 완료")
                else:
                    print(f"    🚫 [Drop] 과정 {idx+1}: 정보 부족")

        except Exception as e:
            print(f"  ❌ 파일 처리 중 에러 발생: {file} -> {e}")

    print(f"\n🎉 [모듈 스토어] 변환 완료! '{OUTPUT_DIR}' 폴더를 확인하세요.")


if __name__ == "__main__":
    process_module_store()
