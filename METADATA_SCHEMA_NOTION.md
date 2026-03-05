# Curriculum Store — Metadata Schema

> PPTX 제안서에서 커리큘럼을 추출할 때 적용되는 custom_metadata 스키마입니다.

---

## 메타데이터 필드 (9개)

| 필드 | 설명 | 값 | 매칭 방식 |
|------|------|-----|-----------|
| `domain` | 교육 도메인 | `G`, `D`, `DA` | `=` 정확 매칭 |
| `skillCategory` | 스킬 패밀리 코드 | `GT`, `GM`, `DAA` 등 | `=` 정확 매칭 |
| `skillId` | 핵심 스킬 ID | `GT001,GM002` | 쉼표 구분, 1~3개 |
| `level` | 교육 난이도 | `basic`, `intermediate`, `advanced` | `=` 정확 매칭 |
| `industry` | 산업/업종 | `제조`, `금융` 등 11개 | `=` 정확 매칭 |
| `targetRole` | 교육 대상 | `실무자`, `개발자` 등 7개 | `=` 정확 매칭 |
| `duration` | 총 교육 시수 | `8`, `16`, `24` | `=` 정확 매칭 |
| `educationFormat` | 교육 형태 | `강의형`, `실습형` 등 5개 | `=` 정확 매칭 |
| `toolsUsed` | 사용 도구 | `ChatGPT,Python,LangChain` | 쉼표 구분, 3개 이내 |

---

## 표준값 목록

### level
| 값 | 설명 |
|---|---|
| basic | 입문/기초 (사전 지식 불필요, 개념 이해 중심) |
| intermediate | 중급 (기본 지식 전제, 실무 적용 중심) |
| advanced | 고급 (실무 경험 전제, 심화/프로젝트 중심) |

### industry
| 값 |
|---|
| 제조 / 금융 / IT / 유통 / 의료 / 교육 / 공공 / 에너지 / 건설 / 미디어 / 기타 |

### targetRole
| 값 | 설명 |
|---|---|
| 임원 | C-Level, 본부장급 이상 |
| 중간관리자 | 팀장, 파트장급 |
| 실무자 | 일반 직원, 담당자 |
| 신입사원 | 신입/주니어 |
| 개발자 | SW 개발 직군 |
| 데이터분석가 | 데이터/분석 직군 |
| 전사 | 직군 무관 전 직원 대상 |

### educationFormat
| 값 | 설명 |
|---|---|
| 강의형 | 이론 중심 강의 |
| 실습형 | 실습/핸즈온 중심 |
| 프로젝트형 | PoC/프로젝트 기반 |
| 혼합형 | 강의 + 실습 혼합 |
| 워크숍형 | 그룹 활동/토론 중심 |

### toolsUsed (주요 도구명 참조)
ChatGPT, Claude, Gemini, Perplexity, Copilot, CopilotStudio, Midjourney, DALL-E, StableDiffusion, Runway, Gamma, NotebookLM, CursorAI, CanvaAI, ClaudeCode, HuggingFace, Python, Excel, PowerBI, Tableau, SQL, Jupyter, LangChain, LangGraph, Langflow, Make, n8n, Dify, PowerAutomate, PyTorch, TensorFlow, MLflow, Streamlit

---

## 도메인/스킬 코드 참조

| 도메인 | 코드 | 스킬 수 |
|--------|------|---------|
| GenAI | G | 71 |
| MLDL | D | 25 |
| Data Analytics & BI | DA | 30 |

| 패밀리 | 코드 |
|--------|------|
| Tool/Platform | T |
| Method/Model | M |
| Retrieval/Knowledge | R |
| Workflow/Agent | A |
| Capability/Function | C |

스킬 ID 원본: `G-T005`, `DA-A001` → 메타데이터 저장 시 하이픈 제거: `GT005`, `DAA001`

---

## 요약

| 필드 | 값 개수 | 복수 허용 | 비고 |
|---|---|---|---|
| domain | 고정 3개 | X (1개만) | G, D, DA |
| skillCategory | 고정 13개 | X (1개만) | GT, GM 등 |
| skillId | 카탈로그 126개 | O (쉼표 구분) | 1~3개 |
| level | 고정 3개 | X (1개만) | |
| industry | 고정 11개 | X (1개만) | |
| targetRole | 고정 7개 | X (1개만) | |
| duration | 자유 (숫자) | X | 시간 단위 정수 |
| educationFormat | 고정 5개 | X (1개만) | |
| toolsUsed | 카탈로그 참조 | O (쉼표 구분) | 3개 이내 권장 |

---

*2026-03-05 적용 / skills_catalog_v3.jsonl (126개) 기준*
