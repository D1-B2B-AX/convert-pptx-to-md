# 커리큘럼 문서 분리 및 메타데이터 설계

## 배경

2026-02-26에 extract_curriculum.py의 GPT 프롬프트를 개선하여 RAG 최적화 Markdown 포맷을 적용했다.
그 과정에서 다음 구조적 문제가 확인되었다.

## 현재 구조 (As-Is)

과정 하나 = MD 파일 하나.

```
IBK기업은행_LLM_역량_육성_Course_1.md  (~3,000 토큰)
├── 과정 메타데이터 (DOC_ID, CLIENT, INDUSTRY, ...)
├── 교육 개요
├── [MODULE] m01 (~130 토큰)
├── [MODULE] m02 (~160 토큰)
├── ...
└── [MODULE] m11 (~120 토큰)
```

### 문제점

1. **청크 경계 비제어**: Gemini File Search Store의 whitespace 기반 chunking이 `## [MODULE]` 헤딩에서 정확히 분리된다는 보장이 없다. 모듈 중간에서 잘릴 경우 BREADCRUMB 없는 청크가 생겨 맥락이 유실된다.

2. **metadata_filter 활용 불가**: `custom_metadata`는 문서(파일) 단위로 부여된다. 하나의 파일에 모든 모듈이 들어 있으면 모듈별/회차별 필터링이 불가능하다.

3. **회차 간 흐름 정보 부재**: 1일차→2일차→3일차의 학습 연계와 설계 의도를 담은 정보가 없어서 "전체 과정 흐름" 관련 쿼리에 답변할 수 없다.

## 변경 구조 (To-Be)

과정 하나 = 디렉토리 하나. 과정 개요 1개 + 모듈별 MD 파일.

```
output/curriculum/
  IBK기업은행_LLM_역량_육성/
    course_overview.md              ← 과정 전체 정보
    d01_m01_llm의_이해.md           ← 모듈별 개별 파일
    d01_m02_embedding과_rag.md
    d01_m03_llm_application.md
    d01_m04_rag_구성요소.md
    d02_m05_advanced_rag.md
    ...
    d03_m11_quantization.md
```

### course_overview.md

과정 레벨 쿼리를 전담하는 파일. 전체 메타데이터, 교육 개요, 로드맵을 포함한다.

```
# IBK기업은행: LLM 역량 육성 과정
DOC_ID: CURR::ibk기업은행_llm_역량_육성_c1
CLIENT: IBK기업은행
INDUSTRY: 금융
TOPIC: LLM, RAG, 파인튜닝
TARGET: 조직 내 AI 적용을 주도할 수 있는 실전형 인재
LEVEL: 전 수준
DURATION: 21H (3일)
TOOLS: Transformer, Langchain, VectorDB, PEFT, RLHF, GRPO
FORMAT: 오프라인
SOURCE_FILE: IBK기업은행 LLM 역량 육성.pptx

## 교육 개요
IBK기업은행에 맞춤 교육을 통해 조직 내 AI 적용을 주도할 수 있는 실전형 인재를 양성하는 것이 목표입니다. 교육은 LLM과 RAG 구조 이해, 파인튜닝 및 성능 개선 방법을 다룹니다.

## 로드맵
1일차 LLM 기초 → 2일차 RAG 응용 → 3일차 파인튜닝 및 최적화

## 모듈 목록
- 1일차 M01: Large Language Model의 이해 (1.5H)
- 1일차 M02: Embedding과 RAG (2H)
- 1일차 M03: LLM Application (2H)
- 1일차 M04: RAG 구성요소 (1.5H)
- 2일차 M01: Advanced RAG (2H)
- 2일차 M02: RAG 성능 평가 방법 및 LLM 성능 평가 (1H)
- 2일차 M03: Large Language Model (2H)
- 2일차 M04: Data for LLM (2H)
- 3일차 M01: Fine-Tuning & Alignments (3H)
- 3일차 M02: Reasoning Model (2H)
- 3일차 M03: Quantization (2H)
```

### 모듈 파일 (예: d01_m02_embedding과_rag.md)

본문에는 semantic search에 잡히기 위한 최소 컨텍스트만 포함한다.
필터링용 정보는 custom_metadata로 분리한다.

**본문:**

```
# IBK기업은행: LLM 역량 육성 과정
1일차 | 21H | 금융 | 전 수준

## Embedding과 RAG
MODULE_SUMMARY: RAG 방법론 및 활용과 임베딩 모델을 학습합니다.
DURATION: 2H
TOOLS: Langchain, VectorDB

### 학습목표
- RAG 방법론 이해
- 임베딩 모델 활용

### 세부내용
- RAG 방법론 및 활용
- 임베딩 모델과 RAG

### 실습
- RAG를 활용한 간단 챗봇 제작
```

**custom_metadata (업로드 시 API 파라미터로 전달):**

```json
{
  "doc_id": "CURR::ibk기업은행_llm_역량_육성_c1::m02",
  "doc_type": "module",
  "course_name": "LLM 역량 육성 과정",
  "client": "IBK기업은행",
  "industry": "금융",
  "module_name": "Embedding과 RAG",
  "module_summary": "RAG 방법론 및 활용과 임베딩 모델을 학습합니다.",
  "day": 1,
  "module_index": 2,
  "duration": "2H",
  "tools": "Langchain, VectorDB",
  "level": "전 수준",
  "source_file": "IBK기업은행 LLM 역량 육성.pptx"
}
```

## 설계 근거

### 본문 최소 컨텍스트 vs 전체 메타데이터 반복

| 방식 | 장점 | 단점 |
|---|---|---|
| 전체 메타데이터 반복 | 파일 하나로 완전 자립 | 11개 파일 임베딩이 유사해져 검색 구분력 저하 |
| 컨텍스트 없음 (metadata만) | 임베딩 고유성 최대 | "IBK기업은행 교육" 검색 시 텍스트에 없어서 안 잡힘 |
| **최소 컨텍스트 (2줄)** | **검색 가능 + 임베딩 고유성 유지** | metadata_filter 병행 필요 |

채택: **최소 컨텍스트 (2줄)**. 과정명과 고객사가 본문에 포함되어 semantic search에 잡히면서, 모듈 고유 내용이 임베딩의 대부분을 차지하여 모듈 간 구분력을 유지한다.

### 회차 간 흐름 정보

| 방식 | 장점 | 단점 |
|---|---|---|
| 모듈 파일마다 DAY_FLOW/PROGRESSION 반복 | 어디서든 흐름 파악 가능 | 공유 텍스트 증가, 임베딩 유사도 상승 |
| **course_overview.md에만 포함** | **임베딩 오염 없음, 역할 분리 명확** | 흐름 쿼리는 overview 파일에 의존 |

채택: **course_overview.md 전담**. 모듈 파일의 "1회차" 표기로 소속 회차는 알 수 있고, 회차 간 연계/설계 의도는 overview 파일이 담당한다.

## 예상 토큰 분포

| 파일 유형 | 토큰 수 | 예상 청크 수 |
|---|---|---|
| course_overview.md | 250~400 | 1 |
| 모듈 파일 (개당) | 130~250 | 1 |
| 11개 모듈 합계 | 1,430~2,750 | 11 |
| **과정 전체** | **1,680~3,150** | **12** |

모듈 파일 하나가 400 토큰 이하이므로, 파일 하나 = 청크 하나가 보장된다.
chunking에 의한 의도치 않은 분리가 발생하지 않는다.

## 구현 범위

### In Scope
- extract_curriculum.py: 출력 형식 변경 (단일 MD → 디렉토리 + 개별 MD)
- GPT 프롬프트: course_overview + 모듈별 출력 구조 반영
- metadata JSON 파일 생성: 각 MD 파일과 함께 업로드 시 사용

### Out of Scope
- n8n 워크플로우 수정 (업로드 파이프라인의 metadata 전달)
- metadata_filter 쿼리 로직 (Stream 2.2, Stream 3 수정)
- extract_reference.py 개선
- Gemini File Search Store의 chunking_config 튜닝
