# PPTX to Markdown Converter

교육 제안서 PPTX 파일을 분석하여 RAG(Retrieval-Augmented Generation)에 최적화된 Markdown으로 자동 변환하는 **FastAPI 서버**입니다.

**Dual Store 아키텍처**로 커리큘럼 스토어(테이블 포맷 보존)와 모듈 스토어(모듈별 개별 파일)를 동시에 생성하여, Gemini File Search Store 기반 RAG 검색 정확도를 높입니다.


## 주요 기능

1. **Dual Store 변환**
   - **커리큘럼 스토어**: 원본 테이블 구조를 그대로 보존한 단일 MD 파일 + 교육 설계 의도(DAY_FLOW, PROGRESSION, DESIGN_RATIONALE) 포함
   - **모듈 스토어**: 모듈별 개별 MD 파일 분리 + 과정 개요(course_overview.md) + custom_metadata JSON

2. **스마트 PPTX 파싱**
   - 숨김 슬라이드 자동 차단 (XML 레벨 `is_hidden` 감지)
   - 그룹 도형, 테이블 내부 텍스트까지 재귀 추출
   - 슬라이드 자동 분류: OVERVIEW / CURRICULUM / EXCLUDE / OTHER

3. **LLM 기반 구조화**
   - OpenAI(GPT-4o) 또는 Gemini(2.5 Flash)로 Raw Text를 구조화된 Markdown으로 변환
   - `LLM_PROVIDER` 환경변수로 전환 (코드 변경 불필요)
   - 스킬 카탈로그 매칭: 과정/모듈별 SKILL_ID 자동 태깅
   - 커리큘럼 무관 내용(강사 프로필, 회사 소개 등) 자동 필터링
   - 환각(Hallucination) 방지 프롬프트 적용

4. **FastAPI 서버 (Railway 배포)**
   - `POST /extract` — PPTX 업로드 → 양쪽 스토어 결과를 JSON으로 반환
   - `GET /health` — 헬스 체크
   - n8n 워크플로우에서 HTTP Request로 호출


## API

### `POST /extract`

PPTX 파일을 multipart로 업로드하면 dual store 결과를 반환합니다.

```bash
curl -X POST https://your-railway-url/extract \
  -F "file=@ABC기업 AI 역량 강화.pptx"
```

**응답 예시:**

```json
{
  "source_file": "ABC기업 AI 역량 강화.pptx",
  "courses": [
    {
      "doc_id": "CURR::abc기업_ai_역량_강화_c1",
      "curriculum_store": {
        "content": "# [COURSE] AI 역량 강화 과정\n...",
        "metadata": { "doc_type": "curriculum", "client": "ABC기업", ... }
      },
      "module_store": [
        { "filename": "course_overview.md", "content": "...", "metadata": { ... } },
        { "filename": "d01_m01_llm_기초.md", "content": "...", "metadata": { ... } },
        ...
      ]
    }
  ]
}
```


## 프로젝트 구조

```text
├── app.py                          # FastAPI 서버 (POST /extract, GET /health)
├── llm_client.py                   # LLM 추상화 (OpenAI/Gemini 환경변수 전환)
├── Dockerfile                      # Railway 배포용
├── requirements.txt                # Python 의존성
│
├── extract_curriculum_store_v2.py  # 커리큘럼 스토어 (스킬 카탈로그 매칭 포함)
├── extract_module_store_v2.py      # 모듈 스토어 (스킬 카탈로그 매칭 포함)
├── extract_curriculum_store.py     # v1 원본 (백업용, app.py에서 미사용)
├── extract_module_store.py         # v1 원본 (백업용, app.py에서 미사용)
├── extract_reference.py            # 레퍼런스(수행실적) 추출
├── skill_catalog_260226_v1.md      # 스킬 카탈로그 (SKILL_ID 매칭 참조)
│
├── utils/
│   ├── pptx_parser.py              # PPTX 파싱, 슬라이드 분류, 과정 그루핑 공통 로직
│   └── clean_pptx_names.py         # 파일명 일괄 정제 (NFD→NFC 변환 포함)
│
├── input/                          # 원본 PPTX 파일 (git 제외)
├── output/
│   ├── curriculum_store/           # 커리큘럼 스토어 출력 (git 제외)
│   ├── module_store/               # 모듈 스토어 출력 (git 제외)
│   └── reference/                  # 레퍼런스 출력 (git 제외)
│
├── .env                            # API Key (git 제외)
├── .env.example                    # 환경변수 템플릿
└── README.md
```


## 배포

### Railway

1. GitHub 레포 연결: `D1-B2B-AX/convert-pptx-to-md`
2. 환경변수 설정 (아래 표 참고)
3. Dockerfile 기반 자동 빌드/배포 (main push 시 자동)

### 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `LLM_PROVIDER` | `openai` | `gemini`로 변경 시 Gemini 사용 |
| `OPENAI_API_KEY` | - | OpenAI 사용 시 필수 |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI 모델 지정 |
| `GEMINI_API_KEY` | - | Gemini 사용 시 필수 |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini 모델 지정 |

### 로컬 실행

```bash
# 의존성 설치
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 환경변수
cp .env.example .env
# .env에 API Key + LLM_PROVIDER 설정

# 서버 실행
uvicorn app:app --host 0.0.0.0 --port 8000
```
