import os
import re
import unicodedata

# =========================================================
# 텍스트 정규화
# =========================================================
def normalize(text):
    """텍스트의 공백을 제거하고 소문자로 변환하여 정규화합니다."""
    return re.sub(r'\s+', '', str(text).lower())

# =========================================================
# 키워드 상수
# =========================================================
EXCLUDE_KEYWORDS = [
    "유사", "사례", "실적", "reference", "case", "history", "result",
    "강사프로필", "수행실적", "제안사", "회사소개", "레퍼런스", "목차"
]

OVERVIEW_KEYWORDS = [
    "과정 소개", "과정소개", "과정 개요", "과정개요",
    "교육 소개", "교육소개", "교육 개요", "교육개요",
    "개요", "소개", "overview", "summary", "요약", "제안 배경", "기획 의도",
    "목표", "대상"
]

CURRICULUM_KEYWORDS = [
    "커리큘럼", "세부과정", "교육과정", "교육내용", "모듈구성",
    "상세과정", "프로그램", "module", "schedule", "curriculum",
    "모듈", "일정", "방법", "contents", "agenda", "syllabus",
    "1일차", "2일차", "1h", "2h", "time"
]

CURRICULUM_BODY_INDICATORS = [
    "세부과정", "교육내용", "모듈구성", "상세과정",
    "교육목표", "학습목표", "주요내용", "교육시수", "강의시수",
    "curriculum", "syllabus"
]

# =========================================================
# 슬라이드 유틸리티
# =========================================================
def is_slide_hidden(slide):
    """슬라이드가 '숨기기' 처리되어 있는지 확인합니다. (XML 속성 검사)"""
    return slide._element.get('show') == '0'

def get_visual_title(slide):
    """슬라이드의 시각적 제목(가장 상단에 위치한 텍스트)을 추출합니다."""
    if slide.shapes.title and slide.shapes.title.text.strip():
        return slide.shapes.title.text.strip()

    candidates = []
    for shape in slide.shapes:
        if not hasattr(shape, "text") or not shape.text.strip():
            continue
        if shape.top < 2000000:
            candidates.append((shape.top, shape.left, shape.text.strip()))

    if candidates:
        candidates.sort(key=lambda x: (x[0], x[1]))
        return candidates[0][2]

    return ""

def extract_text_from_slide(slide):
    """슬라이드 내의 모든 텍스트(도형, 표 포함)를 추출합니다."""
    lines = []
    visual_title = get_visual_title(slide)

    if visual_title:
        lines.append(f"### {visual_title}")

    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text.strip():
            if shape.text.strip() == visual_title:
                continue
            lines.append(shape.text.strip())

        if shape.has_table:
            for row in shape.table.rows:
                row_cells = [c.text.replace('\n', ' ').strip() for c in row.cells if c.text.strip()]
                if row_cells:
                    lines.append(f"| {' | '.join(row_cells)} |")

    return "\n".join(lines)

# =========================================================
# 슬라이드 분류
# =========================================================
def check_table_headers(slide):
    """테이블 헤더에 커리큘럼 키워드가 있는지 확인합니다."""
    for shape in slide.shapes:
        if shape.has_table:
            header_text = ""
            try:
                for cell in shape.table.rows[0].cells:
                    header_text += cell.text + " "
            except:
                continue
            norm_header = normalize(header_text)
            for key in CURRICULUM_KEYWORDS:
                if normalize(key) in norm_header:
                    return True
    return False

def check_body_indicators(slide):
    """본문 텍스트에서 커리큘럼 강한 지표 키워드를 확인합니다."""
    body_text = ""
    for shape in slide.shapes:
        if hasattr(shape, "text"):
            body_text += shape.text + " "
    norm_body = normalize(body_text)
    for key in CURRICULUM_BODY_INDICATORS:
        if normalize(key) in norm_body:
            return True
    return False

def classify_slide_advanced(slide):
    """슬라이드를 OVERVIEW/CURRICULUM/EXCLUDE/OTHER로 분류합니다."""
    title = get_visual_title(slide)
    norm_title = normalize(title)
    for key in EXCLUDE_KEYWORDS:
        if normalize(key) in norm_title:
            return "EXCLUDE"
    for key in CURRICULUM_KEYWORDS:
        if normalize(key) in norm_title:
            return "CURRICULUM"
    for key in OVERVIEW_KEYWORDS:
        if normalize(key) in norm_title:
            return "OVERVIEW"
    if check_table_headers(slide):
        return "CURRICULUM"
    if check_body_indicators(slide):
        return "CURRICULUM"
    return "OTHER"

# =========================================================
# DOC_ID 생성 및 코드펜스 제거
# =========================================================
def generate_doc_id(filename, course_idx):
    """파일명과 과정 인덱스로 DOC_ID를 생성합니다."""
    name = os.path.splitext(filename)[0]
    name = unicodedata.normalize('NFC', name)
    clean = re.sub(r'\d{6}', '', name)
    for term in ["패스트캠퍼스", "데이원컴퍼니", "FC B2B", "FC", "최종", "vf", "VF",
                  "발표용", "교육제안서", "교육 제안서", "제안서"]:
        clean = clean.replace(term, '')
    clean = re.sub(r'[^\w\s가-힣]', '', clean)
    clean = re.sub(r'\s+', '_', clean).strip('_').lower()
    if not clean:
        clean = "unknown"
    return f"CURR::{clean}_c{course_idx}"

def strip_code_fences(text):
    """마크다운 코드펜스(```)를 제거합니다."""
    text = re.sub(r'^```\s*(?:markdown|md)?\s*\n?', '', text)
    text = re.sub(r'\n?```\s*$', '', text)
    return text.strip()

# =========================================================
# 슬라이드 그루핑: 과정 단위로 묶기
# =========================================================
def group_slides_into_courses(prs):
    """PPTX의 슬라이드를 순회하며 과정 단위로 그루핑합니다.

    Returns:
        list[dict]: [{"overview": [str], "curriculum": [str]}, ...]
    """
    courses = []
    current_course = {'overview': [], 'curriculum': []}

    for slide in prs.slides:
        if is_slide_hidden(slide):
            continue

        slide_type = classify_slide_advanced(slide)
        if slide_type == "EXCLUDE":
            continue

        text = extract_text_from_slide(slide)

        if slide_type == "OVERVIEW":
            if current_course['curriculum']:
                courses.append(current_course)
                current_course = {'overview': [], 'curriculum': []}
            current_course['overview'].append(text)

        elif slide_type == "CURRICULUM":
            current_course['curriculum'].append(text)

    if current_course['curriculum']:
        courses.append(current_course)

    return courses
