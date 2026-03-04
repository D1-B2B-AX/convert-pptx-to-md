import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")


def generate(prompt, json_mode=False):
    """LLM_PROVIDER 환경변수에 따라 OpenAI 또는 Gemini를 호출합니다."""
    if LLM_PROVIDER == "gemini":
        return _generate_gemini(prompt, json_mode)
    return _generate_openai(prompt, json_mode)


def _generate_openai(prompt, json_mode):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    kwargs = {
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o"),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content.strip()


def _generate_gemini(prompt, json_mode):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    config_kwargs = {"temperature": 0}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"
    response = client.models.generate_content(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=prompt,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    return response.text.strip()
