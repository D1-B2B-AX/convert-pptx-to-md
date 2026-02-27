# Curriculum Preprocessing RAG Optimization Design

## Goal
extract_curriculum.py의 출력 MD 품질을 개선하여 Gemini File Search Store의 검색 정확도를 향상시킨다.

## Changes

### 1. GPT 프롬프트 수정
- 코드 펜스(```markdown) 금지
- 과정 레벨 메타데이터 추출 지시 (CLIENT, INDUSTRY, TOPIC, TARGET, LEVEL, DURATION, TOOLS, FORMAT)
- 모듈별 인라인 메타데이터 지시 (BREADCRUMB, MODULE_SUMMARY, DURATION, TOOLS)
- DOC_ID/MODULE_ID 포맷 포함

### 2. DOC_ID 자동 생성
- 파일명 기반: `CURR::정제된_파일명_c{과정번호}`
- MODULE_ID: `DOC_ID::m{순번}`

### 3. 텍스트 절삭 상한 확대
- overview: 3000 → 5000
- curriculum: 15000 → 25000

### 4. 후처리 안전장치
- GPT 출력에 코드 펜스 잔존 시 strip

### 5. 유틸 함수 중복 제거
- utils/pptx_parser.py에서 import

## Output Format

```
# [COURSE] 과정명
DOC_ID: CURR::파일명_c번호
CLIENT: ...
INDUSTRY: ...
...

## 교육 개요
...

## [MODULE] 모듈명 (DOC_ID::m번호)
BREADCRUMB: 과정명 > 회차 > 모듈명
MODULE_SUMMARY: 1줄 요약
DURATION: ...
TOOLS: ...

### 학습목표
- ...
### 실습
- ...
```

## Scope Out
- extract_reference.py
- n8n 워크플로우 수정
- logo_hash_map 구축
