# 📄 PPTX to Markdown Converter

교육 제안서 및 커리큘럼이 담긴 PPTX 파일들을 대량으로 분석하여, LLM 및 RAG(Retrieval-Augmented Generation) 시스템에 최적화된 **Clean Markdown (.md)** 파일로 자동 변환하는 파이프라인 스크립트입니다.



## ✨ 주요 기능 (Features)

1. **파일명 정제 자동화 (`rename_pptx.py`)**
   - 불규칙한 제안서 파일명에서 불필요한 단어(날짜, 버전, 사내 용어 등)를 일괄 제거합니다.
   - **macOS 한글 깨짐 방지**: 자음/모음이 분리된 NFD 포맷을 정상적인 NFC 포맷으로 자동 변환하여 정규표현식 필터링이 완벽하게 작동하게 합니다.

2. **스마트 PPTX 텍스트 추출 (`pptx_to_md.py`)**
   - **숨기기 처리된 슬라이드 완벽 차단**: `is_hidden` 속성을 XML 레벨에서 파악하여 불필요한 예비용/과거 장표를 분석에서 제외합니다.
   - 그룹화된 도형, 복잡한 표(Table) 안의 텍스트까지 재귀적으로(Recursive) 모두 추출합니다.

3. **LLM 기반 Markdown 포맷팅 및 필터링**
   - OpenAI API(GPT-4o)를 활용하여 추출된 Raw Text를 구조화된 마크다운으로 변환합니다.
   - 강사 프로필, 레퍼런스, 회사 소개 등 **커리큘럼과 무관한 내용은 필터링**하고, 교육 모듈 및 시간표는 **Markdown Table**로 강제 변환합니다.
   - 환각(Hallucination) 방지 프롬프트가 적용되어 있어 없는 내용을 지어내지 않습니다.

---

## 📂 프로젝트 구조 (Directory Structure)

```text
├── input/                  # 분석할 원본 PPTX 제안서 파일들을 넣는 공통 폴더
├── output/                 # 변환이 완료된 Markdown 파일이 저장되는 최상위 폴더
│   ├── curriculum/         # 커리큘럼 추출 결과물 (.md) 저장 위치
│   └── reference/          # 레퍼런스(수행실적) 추출 결과물 (.md) 저장 위치
│
├── utils/                  # [공통 모듈 폴더]
│   ├── clean_pptx_names.py # 파일명 일괄 정제 스크립트
│   └── pptx_parser.py      # PPTX 파싱, 숨김 슬라이드 필터링 및 텍스트 추출 공통 로직
│
├── extract_curriculum.py   # [커리큘럼 전용] PPTX 파싱 및 Markdown 변환 엔진
├── extract_reference.py    # [레퍼런스 전용] PPTX 파싱 및 Markdown 변환 엔진 (추가 예정)
│
├── .env                    # (Git 커밋 제외) OpenAI API Key 보관
├── .gitignore              # 보안을 위한 Git 무시 파일 목록
└── README.md               # 프로젝트 설명서
```