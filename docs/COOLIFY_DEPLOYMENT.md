# Coolify Deployment

## 목표

Railway 구독 취소로 사라진 변환 서버를 Coolify에 새 서비스로 배포합니다.

새 서비스는 n8n과 분리된 전용 API입니다.

```text
n8n workflow
-> HTTP Request
-> pptx-md-converter-api
-> POST /extract
```

## 권장 서비스명

```text
pptx-md-converter-api
```

## Coolify 생성

1. Coolify에서 새 Resource를 생성합니다.
2. GitHub repo를 연결합니다.

```text
D1-B2B-AX/convert-pptx-to-md
```

3. Build 방식은 Dockerfile을 사용합니다.
4. App port는 `8000`으로 설정합니다.
5. 도메인을 연결합니다.

예시:

```text
https://pptx-md-converter.skillflo.app
```

## 환경변수

OpenAI 사용 시:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o
API_AUTH_TOKEN=replace-with-long-random-token
```

Gemini 사용 시:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
API_AUTH_TOKEN=replace-with-long-random-token
```

`API_AUTH_TOKEN`은 선택값이지만, 공개 도메인으로 배포할 때는 설정하는 것을 권장합니다. 설정하면 n8n HTTP Request 노드에서 아래 Header를 함께 보내야 합니다.

```text
Authorization: Bearer <API_AUTH_TOKEN>
```

## 배포 확인

배포 후 health endpoint를 확인합니다.

```bash
curl https://pptx-md-converter.skillflo.app/health
```

정상 응답:

```json
{"status":"ok"}
```

루트 주소도 확인합니다.

```bash
curl https://pptx-md-converter.skillflo.app/
```

`auth_required`가 `true`이면 `/extract` 호출에 Bearer token이 필요합니다.

## n8n URL 교체

기존 Railway URL:

```text
https://web-production-c728.up.railway.app/extract
```

새 Coolify URL:

```text
https://pptx-md-converter.skillflo.app/extract
```

n8n HTTP Request 노드에서 URL만 새 주소로 바꾸고, `API_AUTH_TOKEN`을 설정했다면 Header를 추가합니다.

## n8n HTTP Request 설정

| 설정 | 값 |
| --- | --- |
| Method | `POST` |
| URL | `https://pptx-md-converter.skillflo.app/extract` |
| Body Content Type | `Form-Data` |
| Parameter Type | `n8n Binary File` |
| Name | `file` |
| Input Data Field Name | `data` |

Google Drive Download 노드의 binary property 이름이 `data`가 아니라면 그 이름으로 `Input Data Field Name`을 바꿉니다.
