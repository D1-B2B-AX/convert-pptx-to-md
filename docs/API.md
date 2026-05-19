# PPTX Markdown Converter API

## 개요

`pptx-md-converter-api`는 n8n 워크플로우에서 PPTX 파일을 업로드하면 커리큘럼 스토어용 Markdown과 metadata를 JSON으로 반환하는 HTTP API 서비스입니다.

이 서비스는 Python FastAPI로 구현되어 있으며, Coolify에는 별도 웹 서비스로 배포합니다.

## 서비스 구분

| 항목 | 값 |
| --- | --- |
| 서비스명 | `pptx-md-converter-api` |
| GitHub repo | `D1-B2B-AX/convert-pptx-to-md` |
| 기술 스택 | Python, FastAPI, Docker |
| 기본 포트 | `8000` |
| n8n 호출 endpoint | `POST /extract` |

## Base URL

권장 구성에서는 n8n과 변환 API를 같은 Docker Compose stack에 두고, Docker 내부 주소를 사용합니다.

```text
http://pptx-md-converter-api:8000
```

이 주소는 브라우저에서 접속하는 주소가 아니라 n8n 컨테이너 내부에서 호출하는 주소입니다.

외부 도메인으로 분리 배포할 수도 있지만, PPTX 파일 업로드가 Cloudflare 413 제한에 걸릴 수 있습니다.

```text
https://pptx-md-converter.skillflo.app
```

기존 Railway URL은 사용하지 않습니다.

```text
https://web-production-c728.up.railway.app/extract
```

## Endpoints

### `GET /`

서비스 정보와 사용 가능한 endpoint를 반환합니다. 브라우저에서 도메인에 직접 접속했을 때 확인용으로 사용합니다.

```bash
curl http://pptx-md-converter-api:8000/
```

응답 예시:

```json
{
  "service": "pptx-md-converter-api",
  "description": "Upload a PPTX file and receive curriculum-store Markdown JSON.",
  "endpoints": {
    "health": "GET /health",
    "extract": "POST /extract multipart/form-data field=file"
  },
  "auth_required": true
}
```

### `GET /health`

Coolify 헬스체크와 배포 확인에 사용합니다.

```bash
curl http://pptx-md-converter-api:8000/health
```

응답:

```json
{"status":"ok"}
```

### `POST /extract`

PPTX 파일을 multipart form-data로 업로드하면 변환 결과를 반환합니다.

요청 조건:

| 항목 | 값 |
| --- | --- |
| Method | `POST` |
| Content-Type | `multipart/form-data` |
| Form field | `file` |
| File type | `.pptx` |
| 인증 | `API_AUTH_TOKEN` 설정 시 `Authorization: Bearer <token>` 필요 |

curl 예시:

```bash
curl -X POST http://pptx-md-converter-api:8000/extract \
  -H "Authorization: Bearer $API_AUTH_TOKEN" \
  -F "file=@ABC기업 AI 역량 강화.pptx"
```

응답 예시:

```json
{
  "source_file": "ABC기업 AI 역량 강화.pptx",
  "courses": [
    {
      "doc_id": "CURR::abc기업_ai_역량_강화_c1",
      "curriculum_store": {
        "content": "# [COURSE] AI 역량 강화 과정\n...",
        "metadata": {
          "domain": "G",
          "skill_category": "GT",
          "skill_id": "GT001",
          "level": "basic",
          "industry": "제조",
          "target_role": "실무자",
          "duration": "8",
          "education_format": "실습형",
          "tools_used": "ChatGPT"
        }
      }
    }
  ]
}
```

## n8n HTTP Request 노드 설정

Google Drive에서 PPTX를 Download한 뒤 HTTP Request 노드를 추가합니다.

| n8n 설정 | 값 |
| --- | --- |
| Method | `POST` |
| URL | `http://pptx-md-converter-api:8000/extract` |
| Body Content Type | `Form-Data` |
| Parameter Type | `n8n Binary File` |
| Name | `file` |
| Input Data Field Name | `data` |

`Input Data Field Name`은 직전 Google Drive Download 노드의 binary property 이름과 같아야 합니다. 보통 `data`입니다.

`API_AUTH_TOKEN`을 설정했다면 Header도 추가합니다.

| Header Name | Header Value |
| --- | --- |
| `Authorization` | `Bearer <API_AUTH_TOKEN>` |

## 에러 응답

| 상태 코드 | 의미 | 조치 |
| --- | --- | --- |
| `400` | `.pptx`가 아니거나 PPTX 파싱 실패 | n8n에서 다운로드한 binary가 실제 PPTX인지 확인 |
| `401` | API 토큰 누락 또는 불일치 | n8n Authorization header 확인 |
| `500` | 변환 중 서버 오류 | Coolify 로그와 LLM API key 확인 |
