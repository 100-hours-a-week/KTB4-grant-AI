# AI 요약
import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma4:e2b"

def summarize_text(text: str) -> str | None:
    """입력 text를 ollama를 통해 한 문장으로 요악"""
    prompt = f"다음 글을 한국어로 짧게 한 문장으로 요약하고, 요약한 내용만 출력해줘:\n\n{text}"
    try:
        response = httpx.post(
            url = OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60.,
        )
        return response.json()["response"].strip()
    except Exception as e:
        print(f"Error 발생: {e}")
        return None