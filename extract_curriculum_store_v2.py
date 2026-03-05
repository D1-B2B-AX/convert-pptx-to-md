import os
import re
import json
from pptx import Presentation
from dotenv import load_dotenv
from utils.pptx_parser import (
    generate_doc_id, group_slides_into_courses, strip_code_fences
)
from llm_client import generate as llm_generate

load_dotenv()

SOURCE_DIR = './input'
OUTPUT_DIR = './output/curriculum_store'
SKILL_CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'archetypes', 'skills_catalog_v3.jsonl')


def load_skill_catalog():
    """스킬 카탈로그 JSONL을 읽어 프롬프트용 텍스트로 변환합니다."""
    entries = []
    with open(SKILL_CATALOG_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            entries.append(obj)

    # 도메인별로 그룹핑
    domains = {}
    for e in entries:
        key = f"{e['domain_name']} ({e['domain_code']})"
        domains.setdefault(key, []).append(e)

    lines = ["## 스킬 카탈로그"]
    for domain, skills in sorted(domains.items()):
        lines.append(f"\n### {domain}")
        lines.append("| ID | name | level | family |")
        lines.append("|---|---|---|---|")
        for s in skills:
            family = f"{s['family_name']} ({s['domain_code']}-{s['family_code']})"
            lines.append(f"| {s['id']} | {s['name']} | {s['level']} | {family} |")

    return '\n'.join(lines)


def generate_curriculum_store_markdown(filename, course_idx, overview_text, curriculum_text):
    """GPT-4o로 테이블 포맷 보존 Markdown을 생성합니다."""
    if len(curriculum_text) < 50:
        return None, None

    skill_catalog = load_skill_catalog()

    prompt = f"""당신은 B2B 교육 제안서에서 커리큘럼을 추출하여 RAG 검색에 최적화된 Markdown으로 변환하는 전문가입니다.

[Input]
- File: {filename}
- Course Index: {course_idx}
- Overview: {overview_text[:5000]}
- Curriculum: {curriculum_text[:25000]}

[스킬 카탈로그 - SKILL_ID 매칭 참조용]
{skill_catalog}

[SKILL_ID 매칭 지침]
- 위 스킬 카탈로그에서 이 과정의 핵심 스킬 1~3개를 선택하십시오.
- skillId 필드에 하이픈을 제거한 형식으로 기입하십시오 (예: G-T001 → GT001, DA-A003 → DAA003).
- 복수 스킬은 공백 없이 쉼표로 구분하십시오 (예: GT001,GM002).
- skillCategory는 선택한 skillId의 카테고리 접두사입니다 (예: GT, GM, DA, DAA 등). 하이픈 제거.
- domain은 G(GenAI), D(MLDL), DA(Data Analytics & BI) 코드로 기입하십시오.

[Task]
위 Raw Text를 분석하여 아래 포맷에 정확히 맞는 Markdown을 출력하십시오.

[Critical Rules]
1. 절대로 ```markdown 코드 블록으로 감싸지 마십시오. 순수 Markdown 텍스트만 출력하십시오.
2. 없는 정보를 지어내지 마십시오. 추출할 수 없는 필드는 "정보 없음"으로 적으십시오.
3. 강사 약력, 회사 홍보, 레퍼런스(유사 사례) 등 커리큘럼과 무관한 내용은 제거하십시오.
4. 유효한 커리큘럼 정보가 없으면 오직 NO_DATA 라고만 출력하십시오.
5. **가장 중요: 커리큘럼 테이블 구조를 원본 그대로 보존하십시오. 모듈별 개조식 bullet list로 변환하지 마십시오.**
6. 원본에 Markdown 테이블(| | |)이 있으면 그대로 유지하고, 원본이 표 형태가 아니더라도 시수/모듈/내용이 구조화되어 있으면 Markdown 테이블로 정리하십시오.

[Output Format - 반드시 이 구조를 따르십시오]

# [COURSE] {{과정명}}
domain: {{G / D / DA 중 택 1 — G=GenAI, D=MLDL, DA=Data Analytics & BI}}
skillCategory: {{하이픈 제거 형식. GT, GM, GR, GA, GC, DT, DM, DA, DC, DAT, DAM, DAA, DAC 중 택 1}}
skillId: {{스킬 카탈로그에서 핵심 스킬 1~3개, 하이픈 제거, 쉼표 구분. 예: GT001,GM002}}
level: {{basic / intermediate / advanced 중 택 1}}
industry: {{제조 / 금융 / IT / 유통 / 의료 / 교육 / 공공 / 에너지 / 건설 / 미디어 / 기타 중 택 1}}
targetRole: {{임원 / 중간관리자 / 실무자 / 신입사원 / 개발자 / 데이터분석가 / 전사 중 택 1}}
duration: {{총 교육 시수 - 숫자만. 예: 8, 16, 24}}
educationFormat: {{강의형 / 실습형 / 프로젝트형 / 혼합형 / 워크숍형 중 택 1}}
toolsUsed: {{주요 도구 3개 이내, 공백 없이 쉼표 구분. 예: ChatGPT,Python,LangChain}}

## 교육 개요
{{교육의 배경, 목적, 학습 목표를 2~4문장으로 요약}}

## 커리큘럼

{{커리큘럼 테이블을 원본 구조 그대로 보존하여 출력. 아래는 예시 형태:}}

| 회차 | 모듈 | 시수 | 주요 내용 |
|------|------|------|-----------|
| 1일차 | 모듈명 | 2H | 핵심 학습 내용 요약 |

{{회차가 여러 개이면 회차별로 테이블을 분리하거나, 하나의 테이블에 회차 컬럼으로 구분}}

## DAY_FLOW
{{각 회차별 학습 흐름을 1줄로 요약. 예:}}
- 1일차: 기초 개념 이해 → 도구 실습
- 2일차: 심화 응용 → 팀 프로젝트
- 3일차: 실전 프로젝트 → 발표 및 피드백

## PROGRESSION
{{과정 전체의 난이도 흐름을 1~2문장으로 설명. 예: "기초 개념에서 시작하여 점진적으로 실전 프로젝트까지 진행하는 상향식 구조"}}

## DESIGN_RATIONALE
{{이 커리큘럼이 왜 이렇게 설계되었는지, 교육 설계 의도를 2~3문장으로 설명. 예: "LLM 기초를 먼저 다루어 전사 공통 역량을 확보한 뒤, 부서별 맞춤 실습으로 즉시 업무 적용이 가능하도록 설계"}}
"""

    try:
        result = llm_generate(prompt)

        if "NO_DATA" in result:
            return None, None
        if len(result) < 50:
            return None, None

        result = strip_code_fences(result)

        # metadata 추출 (헤더 필드에서 파싱)
        metadata = {}
        field_patterns = {
            "domain": r'^domain:[ \t]*(.+)$',
            "skillCategory": r'^skillCategory:[ \t]*(.+)$',
            "skillId": r'^skillId:[ \t]*(.+)$',
            "level": r'^level:[ \t]*(.+)$',
            "industry": r'^industry:[ \t]*(.+)$',
            "targetRole": r'^targetRole:[ \t]*(.+)$',
            "duration": r'^duration:[ \t]*(.+)$',
            "educationFormat": r'^educationFormat:[ \t]*(.+)$',
            "toolsUsed": r'^toolsUsed:[ \t]*(.+)$',
        }
        for key, pattern in field_patterns.items():
            match = re.search(pattern, result, re.MULTILINE)
            if match:
                metadata[key] = match.group(1).strip()

        return result, metadata

    except Exception as e:
        print(f"  ❌ LLM Error: {e}")
        return None, None


def save_curriculum_store(filename, course_idx, md_content, metadata):
    """curriculum.md + metadata.json을 저장합니다."""
    doc_id = generate_doc_id(filename, course_idx)
    safe_id = re.sub(r'[^a-zA-Z0-9가-힣_]', '_', doc_id.replace('CURR::', ''))
    course_dir = os.path.join(OUTPUT_DIR, safe_id)
    os.makedirs(course_dir, exist_ok=True)

    md_path = os.path.join(course_dir, 'curriculum.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    meta_path = os.path.join(course_dir, 'metadata.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"    ✅ curriculum.md + metadata.json 저장 완료 ({safe_id}/)")


def process_curriculum_store(source_dir=None):
    """커리큘럼 스토어 메인 파이프라인."""
    src = source_dir or SOURCE_DIR
    if not os.path.exists(src):
        print(f"❌ 원본 폴더를 찾을 수 없습니다: {src}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = [f for f in os.listdir(src) if f.endswith('.pptx')]
    print(f"🚀 총 {len(files)}개의 제안서 -> [커리큘럼 스토어] 변환 시작...\n")

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

                md_content, metadata = generate_curriculum_store_markdown(
                    file, idx + 1, full_overview, full_curriculum
                )

                if md_content and metadata:
                    save_curriculum_store(file, idx + 1, md_content, metadata)
                else:
                    print(f"    🚫 [Drop] 과정 {idx+1}: 정보 부족")

        except Exception as e:
            print(f"  ❌ 파일 처리 중 에러 발생: {file} -> {e}")

    print(f"\n🎉 [커리큘럼 스토어] 변환 완료! '{OUTPUT_DIR}' 폴더를 확인하세요.")


if __name__ == "__main__":
    process_curriculum_store()
