from extract_curriculum_store_v2_gemini import process_curriculum_store
from extract_module_store_v2_gemini import process_module_store


def main():
    print("=" * 60)
    print("[1/2] Curriculum Store (Gemini)")
    print("=" * 60)
    process_curriculum_store()

    print()
    print("=" * 60)
    print("[2/2] Module Store (Gemini)")
    print("=" * 60)
    process_module_store()

    print()
    print("=" * 60)
    print("Dual Store 변환 완료! (Gemini)")
    print("  - output/curriculum_store/  (과정별 테이블 커리큘럼)")
    print("  - output/module_store/      (모듈별 개별 파일)")
    print("=" * 60)


if __name__ == "__main__":
    main()
