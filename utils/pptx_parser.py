import re

def normalize(text):
    """텍스트의 공백을 제거하고 소문자로 변환하여 정규화합니다."""
    return re.sub(r'\s+', '', str(text).lower())

def is_slide_hidden(slide):
    """슬라이드가 '숨기기' 처리되어 있는지 확인합니다. (XML 속성 검사)"""
    return slide._element.get('show') == '0'

def get_visual_title(slide):
    """슬라이드의 시각적 제목(가장 상단에 위치한 텍스트)을 추출합니다."""
    # 1. 기본 제목 속성이 있는 경우
    if slide.shapes.title and slide.shapes.title.text.strip():
        return slide.shapes.title.text.strip()
    
    # 2. 제목 속성이 없으면 위치(Top)를 기반으로 추론
    candidates = []
    for shape in slide.shapes:
        if not hasattr(shape, "text") or not shape.text.strip():
            continue
        # 상단에 위치한 텍스트를 제목 후보로 간주 (2,000,000 EMU 이하)
        if shape.top < 2000000: 
            candidates.append((shape.top, shape.left, shape.text.strip()))
    
    if candidates:
        # top(y좌표), left(x좌표) 순으로 오름차순 정렬하여 가장 좌측 상단의 텍스트 반환
        candidates.sort(key=lambda x: (x[0], x[1])) 
        return candidates[0][2]
    
    return ""

def extract_text_from_slide(slide):
    """슬라이드 내의 모든 텍스트(도형, 표 포함)를 추출합니다."""
    lines = []
    visual_title = get_visual_title(slide)
    
    # 제목 먼저 추가
    if visual_title:
        lines.append(f"### {visual_title}")
    
    for shape in slide.shapes:
        # 일반 텍스트 도형 (제목과 중복되는 내용 건너뛰기)
        if hasattr(shape, "text") and shape.text.strip():
            if shape.text.strip() == visual_title:
                continue
            lines.append(shape.text.strip())
        
        # 표(Table) 데이터 추출
        if shape.has_table:
            for row in shape.table.rows:
                # 표 내용 한 줄로 합치기 (Markdown 변환 시 LLM이 처리하도록 원본 형태 유지)
                row_cells = [c.text.replace('\n', ' ').strip() for c in row.cells if c.text.strip()]
                if row_cells:
                    lines.append(f"| {' | '.join(row_cells)} |")
                    
    return "\n".join(lines)