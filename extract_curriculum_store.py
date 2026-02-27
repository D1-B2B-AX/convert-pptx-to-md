import os
import re
import json
from pptx import Presentation
from openai import OpenAI
from dotenv import load_dotenv
from utils.pptx_parser import (
    generate_doc_id, group_slides_into_courses, strip_code_fences
)

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SOURCE_DIR = './input'
OUTPUT_DIR = './output/curriculum_store'


def generate_curriculum_store_markdown(filename, course_idx, overview_text, curriculum_text):
    """GPT-4o로 테이블 포맷 보존 Markdown을 생성합니다."""
    if len(curriculum_text) < 50:
        return None, None

    doc_id = generate_doc_id(filename, course_idx)

    prompt = f"""당신은 B2B 교육 제안서에서 커리큘럼을 추출하여 RAG 검색에 최적화된 Markdown으로 변환하는 전문가입니다.

[Input]
- File: {filename}
- Course Index: {course_idx}
- DOC_ID: {doc_id}
- Overview: {overview_text[:5000]}
- Curriculum: {curriculum_text[:25000]}

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
DOC_ID: {doc_id}
CLIENT: {{고객사명 - 파일명이나 본문에서 추출}}
INDUSTRY: {{산업군 - 금융/제조/IT/통신/유통/공공/기타}}
TOPIC: {{교육 주제 핵심 키워드}}
TARGET: {{교육 대상자}}
LEVEL: {{초급/중급/고급/전 수준 - 본문에서 추론}}
DURATION: {{총 교육 시수, 예: 21H (3일)}}
TOOLS: {{사용되는 AI 도구/기술 - 쉼표 구분}}
FORMAT: {{교육 방식 - 오프라인/온라인/블렌디드}}
SOURCE_FILE: {filename}

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
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = response.choices[0].message.content.strip()

        if "NO_DATA" in result:
            return None, None
        if len(result) < 50:
            return None, None

        result = strip_code_fences(result)

        # metadata 추출 (헤더 필드에서 파싱)
        metadata = {
            "doc_id": doc_id,
            "doc_type": "curriculum",
            "source_file": filename,
            "course_index": course_idx,
        }
        field_patterns = {
            "course_name": r'^# \[COURSE\] (.+)$',
            "client": r'^CLIENT: (.+)$',
            "industry": r'^INDUSTRY: (.+)$',
            "topic": r'^TOPIC: (.+)$',
            "target": r'^TARGET: (.+)$',
            "level": r'^LEVEL: (.+)$',
            "duration": r'^DURATION: (.+)$',
            "tools": r'^TOOLS: (.+)$',
            "format": r'^FORMAT: (.+)$',
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
    doc_id = metadata.get('doc_id', generate_doc_id(filename, course_idx))
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
