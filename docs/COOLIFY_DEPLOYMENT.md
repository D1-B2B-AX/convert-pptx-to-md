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

## 권장 운영 방식

PPTX 업로드 파일이 Cloudflare 제한에 걸릴 수 있으므로, n8n과 변환 API를 같은 Docker Compose stack에 두는 방식을 권장합니다.

이 경우 변환 API는 외부 도메인을 만들지 않고, n8n이 Docker 내부 DNS로 직접 호출합니다.

```text
n8n
-> http://pptx-md-converter-api:8000/extract
-> pptx-md-converter-api
```

이 방식은 Cloudflare 413 업로드 제한과 외부 포트 개방을 피합니다.

## 같은 Compose stack으로 배포

Coolify에서 `Docker Compose` build pack을 선택하고 이 파일을 사용합니다.

```text
docker-compose.coolify.yml
```

이 stack 안에는 두 서비스가 있습니다.

| 서비스 | 역할 | 외부 도메인 필요 여부 |
| --- | --- | --- |
| `n8n` | 워크플로우 실행 | 필요 |
| `pptx-md-converter-api` | PPTX to Markdown 변환 | 불필요 |

Coolify 도메인은 `n8n` 서비스의 container port `5678`에만 연결합니다.

```text
https://ax-workflow.skillflo.app:5678
```

변환 API에는 도메인을 연결하지 않습니다.

### 기존 n8n 이전 주의

기존 n8n을 새 Compose stack으로 옮기는 경우, 아래 두 값이 특히 중요합니다.

```env
N8N_DATA_VOLUME=기존_n8n_volume_이름
N8N_ENCRYPTION_KEY=기존_n8n_encryption_key
```

`N8N_ENCRYPTION_KEY`가 기존 값과 다르면 기존 credential 복호화가 실패할 수 있습니다.

환경변수 예시는 아래 파일을 참고합니다.

```text
.env.coolify-combined.example
```

### n8n 내부 호출 URL

n8n HTTP Request 노드의 URL은 외부 도메인이 아니라 아래 내부 주소를 사용합니다.

```text
http://pptx-md-converter-api:8000/extract
```

헬스체크 테스트는 아래 주소로 합니다.

```text
http://pptx-md-converter-api:8000/health
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

같은 Compose stack 내부 URL:

```text
http://pptx-md-converter-api:8000/extract
```

n8n HTTP Request 노드에서 URL만 새 주소로 바꾸고, `API_AUTH_TOKEN`을 설정했다면 Header를 추가합니다.

## n8n HTTP Request 설정

| 설정 | 값 |
| --- | --- |
| Method | `POST` |
| URL | `http://pptx-md-converter-api:8000/extract` |
| Body Content Type | `Form-Data` |
| Parameter Type | `n8n Binary File` |
| Name | `file` |
| Input Data Field Name | `data` |

Google Drive Download 노드의 binary property 이름이 `data`가 아니라면 그 이름으로 `Input Data Field Name`을 바꿉니다.
