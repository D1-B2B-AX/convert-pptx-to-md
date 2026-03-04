## 5. 스킬 카탈로그 (75개)

### GenAI (G, 63개)

GenAI 도메인은 3단계 스펙트럼을 커버:
```
[기본 활용] ──── [엔지니어링] ──── [모델 커스터마이징/배포]
 프롬프트/UI      코드/API           파인튜닝/양자화/서빙
 basic           intermediate       advanced
```

#### G-T: Tool/Platform (16) — 이름 "~활용"으로 통일

| ID | name | level | related_tool_ids |
|---|---|---|---|
| G-T001 | ChatGPT 활용 | basic | tool-chatgpt |
| G-T002 | Claude 활용 | basic | tool-claude |
| G-T003 | Gemini 활용 | basic | tool-gemini |
| G-T004 | Perplexity 활용 | basic | tool-perplexity |
| G-T005 | Microsoft Copilot (M365) 활용 | basic | tool-copilot-m365 |
| G-T006 | Copilot Studio 활용 | intermediate | tool-copilot-studio |
| G-T007 | Midjourney 활용 | basic | tool-midjourney |
| G-T008 | DALL-E 활용 | basic | tool-dall-e |
| G-T009 | Stable Diffusion / ComfyUI 활용 | intermediate | tool-stable-diffusion |
| G-T010 | Runway 활용 | basic | tool-runway |
| G-T011 | Gamma / Napkin AI 활용 | basic | tool-gamma, tool-napkin-ai |
| G-T012 | NotebookLM 활용 | basic | tool-notebooklm |
| G-T013 | Cursor AI 활용 | intermediate | tool-cursor |
| G-T014 | Canva AI 활용 | basic | tool-canva |
| G-T015 | Claude Code 활용 | intermediate | — |
| G-T016 | Hugging Face 활용 | intermediate | — |

> G-T016: MLDL에서 이동. 오픈소스 LLM/Diffusion 모델을 다운로드·로드·추론하는 허브 플랫폼 활용 역량. GenAI 모델을 코드로 다루는 첫 관문.

#### G-M: Method/Model (14)

| ID | name | level | 비고 |
|---|---|---|---|
| G-M001 | 생성형 AI 개념 및 LLM 동작 원리 | basic | |
| G-M002 | 프롬프트 엔지니어링 기초 | basic | |
| G-M003 | 프롬프트 엔지니어링 심화 | intermediate | |
| G-M004 | AI 윤리/보안/할루시네이션 관리 | basic | |
| G-M005 | AI 도구 선택 및 비교 평가 | basic | |
| G-M006 | 경영진 AI 전략 및 변화관리 | basic | |
| G-M007 | 컨텍스트 엔지니어링 | intermediate | |
| G-M008 | ControlNet / LoRA 이미지 제어 | intermediate | |
| G-M009 | OpenAI Function Calling / Tool Use | intermediate | |
| G-M010 | 생성형 AI 트렌드 및 산업 사례 분석 | basic | |
| G-M011 | 바이브코딩 방법론 | basic | |
| G-M012 | Transformer / Attention 메커니즘 | intermediate | MLDL에서 이동 |
| G-M013 | Diffusion Models 구조 및 원리 | advanced | MLDL에서 이동 |
| G-M014 | LLM 파인튜닝 및 양자화 | advanced | MLDL에서 이동 |

> **G-M012~014 이동 근거**:
> - G-M012: Transformer/Attention을 배우는 목적 자체가 LLM을 더 잘 이해하고 활용하기 위함
> - G-M013: Diffusion 아키텍처 이해 → Stable Diffusion 커스터마이징의 기반
> - G-M014: 오픈소스 LLM → SLLM 양자화/파인튜닝 = **GenAI의 극단적 활용**
>
> **GenAI 내 Method 레벨 진행**:
> ```
> G-M001 개념이해 → G-M002 프롬프트 → G-M012 아키텍처 → G-M014 파인튜닝/양자화
>   (basic)         (basic)          (intermediate)      (advanced)
> ```

#### G-R: Retrieval/Knowledge (5) — RAG 특화

| ID | name | level | 비고 |
|---|---|---|---|
| G-R001 | RAG 기본 (Embedding/VectorDB/Retrieval) | intermediate | |
| G-R002 | GPTs Knowledge Base 구성 | basic | |
| G-R003 | 문서 청킹 및 전처리 | intermediate | |
| G-R004 | RAG 성능 최적화 (Reranking/Hybrid Search) | advanced | |
| G-R005 | Embedding 모델 학습 및 평가 | advanced | MLDL에서 이동 |

> G-R005: 기존 Embedding 모델을 사용하는 G-R001(basic RAG)의 상위 스킬. 커스텀 Embedding 모델을 학습하여 RAG 품질을 극대화하는 역량. RAG 고도화가 목적이므로 GenAI G-R에 배치.

#### G-A: Workflow/Agent (10) — MECE 3축 + 인프라

```
G-A = 자동화(Non-LLM) ∪ Task Agent화 ∪ AI Workflow 오케스트레이션/배포
```

**축 1: 규칙 기반 자동화** — LLM 없이 반복 업무를 스크립트/플랫폼으로 자동화

| ID | name | level |
|---|---|---|
| G-A001 | 엑셀 VBA/매크로 자동화 | basic |
| G-A002 | Python 스크립트 업무 자동화 | intermediate |
| G-A003 | Power Automate / Teams Workflows 자동화 | intermediate |

**축 2: Task Agent화** — 단일 업무/질의를 AI Agent로 전환

| ID | name | level |
|---|---|---|
| G-A004 | GPTs 업무 Agent 제작 | intermediate |
| G-A005 | LangChain/LangGraph Agent 개발 | advanced |
| G-A006 | Langflow 노코드 Agent 구축 | intermediate |

**축 3: AI Workflow 오케스트레이션 및 배포** — 복수 단계/에이전트 연결 또는 GenAI 모델 서빙

| ID | name | level | 비고 |
|---|---|---|---|
| G-A007 | Make.com AI 워크플로우 구축 | intermediate | |
| G-A008 | n8n / Dify AI 워크플로우 구축 | intermediate | |
| G-A009 | Multi-Agent 오케스트레이션 (MCP/A2A) | advanced | |
| G-A010 | LLM 추론 서빙 (vLLM/TGI) | advanced | MLDL에서 이동 |

> G-A010: LLM을 프로덕션 환경에 배포·서빙하는 인프라 역량. 파인튜닝(G-M014)한 모델을 실제로 운용하기 위한 마지막 단계.
> 축 3에 배치: 워크플로우 → 멀티에이전트 → 모델 서빙으로 이어지는 "AI 시스템 구축" 스펙트럼.

> **MECE 구조 설명**:
> - **축 1 (자동화)**: LLM 미개입. 규칙/스크립트로 반복 업무 제거 → "이전부터 있던 자동화"
> - **축 2 (Agent화)**: 단일 task를 LLM Agent가 처리 → "업무 하나를 AI가 대신"
> - **축 3 (Workflow/배포)**: 복수 AI 단계를 연결하거나 모델을 서빙 → "전체 시스템을 AI로 구축"
> - 복잡도/AI 의존도 순: 축 1 < 축 2 < 축 3

#### G-C: Capability/Function (18) — "AI ~" 접두어로 산출물 성격 강조

| ID | name | level | 비고 |
|---|---|---|---|
| G-C001 | AI 텍스트 요약 | basic | |
| G-C002 | AI 장문 텍스트 생성 | basic | |
| G-C003 | AI 번역 / 다국어 변환 | basic | |
| G-C004 | AI 텍스트 분류 / 감성 분석 | basic | |
| G-C005 | AI 데이터 분석 (ADA/Code Interpreter) | intermediate | |
| G-C006 | AI 코드 생성 / 디버깅 | intermediate | |
| G-C007 | AI 이미지 생성 (T2I) | basic | 프롬프트/UI 레벨 |
| G-C008 | AI 이미지 편집 (Inpainting/Outpainting) | intermediate | |
| G-C009 | AI 이미지 변환 (I2I/Style Transfer) | intermediate | |
| G-C010 | AI 영상 생성 (T2V/I2V) | intermediate | |
| G-C011 | AI 음성 생성 (TTS) | basic | |
| G-C012 | AI 음악 생성 | basic | |
| G-C013 | AI 엑셀 수식/함수 생성 | basic | |
| G-C014 | AI 데이터 시각화 | basic | |
| G-C015 | AI 정보 추출 (NER/구조화) | intermediate | |
| G-C016 | AI PPT 슬라이드 생성 | basic | |
| G-C017 | AI 이미지 생성 (Diffusion 코드 구현) | advanced | MLDL에서 이동 |
| G-C018 | AI 텍스트 생성 (LLM API 구현) | intermediate | MLDL에서 이동 |

> **G-C017/018 이동 근거 및 기존 스킬과의 구분**:
>
> | 스킬 | 접근 방식 | 레벨 |
> |---|---|---|
> | G-C007 AI 이미지 생성 (T2I) | Midjourney/DALL-E **프롬프트** | basic |
> | G-C017 AI 이미지 생성 (Diffusion 코드 구현) | HuggingFace/ComfyUI **Python 파이프라인** | advanced |
> | G-C002 AI 장문 텍스트 생성 | ChatGPT/Claude **대화형** | basic |
> | G-C018 AI 텍스트 생성 (LLM API 구현) | OpenAI API / 오픈소스 LLM **코드 호출** | intermediate |
>
> 산출물(이미지/텍스트)은 동일하나 **구현 방식과 요구 스킬 수준이 근본적으로 다름**.
> F5(Capability)에 배치: "AI가 산출하는 기능"이라는 본질은 같고, 구현 레벨만 다름.

---

### MLDL (D, 12개) — 전통적 ML/DL

#### D-T: Tool/Platform (2)

| ID | name | level |
|---|---|---|
| D-T001 | Python 과학 컴퓨팅 환경 (NumPy/Pandas/Sklearn) | basic |
| D-T002 | PyTorch / TensorFlow 프레임워크 | intermediate |

> D-T002는 GenAI 파인튜닝에도 사용되지만, **범용 딥러닝 프레임워크**로서 MLDL에 유지. GenAI 스킬에서 선수 스킬로 참조.

#### D-M: Method/Model (5)

| ID | name | level |
|---|---|---|
| D-M001 | 지도학습 분류 알고리즘 | basic |
| D-M002 | 비지도학습 클러스터링 | basic |
| D-M003 | 신경망/MLP 기초 | basic |
| D-M004 | CNN 아키텍처 및 전이학습 | intermediate |
| D-M005 | 피처 엔지니어링 및 데이터 전처리 | basic |

> D-M005: 구 D-M008에서 번호 재배정. 전통적 ML 데이터 전처리 역량.

#### D-A: Workflow/Agent (1)

| ID | name | level |
|---|---|---|
| D-A001 | ML 실험 파이프라인 (Train/Eval/Deploy) | intermediate |

#### D-C: Capability/Function (4)

| ID | name | level |
|---|---|---|
| D-C001 | 이미지 분류 (CNN/ViT) | intermediate |
| D-C002 | 객체 검출 (YOLO) | intermediate |
| D-C003 | 이상탐지 (통계/ML 기반) | intermediate |
| D-C004 | 이상탐지 (DL 기반 - Autoencoder/LSTM) | advanced |

---