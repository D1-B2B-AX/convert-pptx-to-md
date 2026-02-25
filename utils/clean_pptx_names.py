import os
import re
import unicodedata  

# =========================================================
# [설정] 대상 폴더 및 제거할 단어
# =========================================================
SOURCE_DIR = './input'  # 작업할 폴더

# 파일명에서 아예 지워버릴 단어들
REMOVE_TERMS = [
    "패스트캠퍼스", "데이원컴퍼니", "FC B2B", "FC", 
    "최종", "vf", "VF", "발표용", "교육제안서", "교육 제안서", "제안서",
    "★", "커리큘럼", "과정"
]

def get_clean_name(filename):
    filename = unicodedata.normalize('NFC', filename)
    name, ext = os.path.splitext(filename)
    
    # 1. 날짜 제거 (6자리 숫자: 240827, 250124 등)
    clean_name = re.sub(r'\d{6}', '', name)
    
    # 2. 괄호 안의 버전 정보 제거
    clean_name = re.sub(r'\((최종|vf|VF|발표용)\)', '', clean_name)

    # 3. 불필요한 단어 제거
    for term in REMOVE_TERMS:
        clean_name = clean_name.replace(term, '')

    # 4. [핵심] 언더바(_)를 공백( )으로 변경
    clean_name = clean_name.replace('_', ' ')

    # 5. 특수문자 제거 (한글, 영문, 숫자, 공백만 남김)
    clean_name = re.sub(r'[^\w\s]', '', clean_name)
    
    # 6. 다중 공백을 '한 개의 공백'으로 정리하고 앞뒤 공백 제거
    # 예: "하나은행  퍼블릭    샌드박스" -> "하나은행 퍼블릭 샌드박스"
    clean_name = re.sub(r'\s+', ' ', clean_name).strip()
    
    # 만약 이름이 다 지워져서 비어있으면 기본값 설정
    if not clean_name:
        clean_name = "Unknown_Project"

    return clean_name + ext

def rename_files():
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ 폴더를 찾을 수 없습니다: {SOURCE_DIR}")
        return

    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.pptx')]
    print(f"📂 총 {len(files)}개의 파일 이름을 변경합니다...\n")

    count = 0
    for old_filename in files:
        # 새 이름 생성
        new_filename = get_clean_name(old_filename)
        
        # 이름이 똑같으면 스킵
        if old_filename == new_filename:
            continue

        old_path = os.path.join(SOURCE_DIR, old_filename)
        new_path = os.path.join(SOURCE_DIR, new_filename)

        # 중복 이름 방지 (이미 같은 이름이 있으면 숫자 붙임)
        if os.path.exists(new_path):
            name, ext = os.path.splitext(new_filename)
            dup_count = 1
            while os.path.exists(new_path):
                new_path = os.path.join(SOURCE_DIR, f"{name} {dup_count}{ext}")
                dup_count += 1
            new_filename = os.path.basename(new_path)

        # 변경 실행
        try:
            os.rename(old_path, new_path)
            print(f"✅ 변경: {old_filename} \n    -> {new_filename}")
            count += 1
        except Exception as e:
            print(f"❌ 실패 ({old_filename}): {e}")

    print(f"\n🎉 총 {count}개의 파일 이름이 깔끔하게 변경되었습니다!")

if __name__ == "__main__":
    rename_files()