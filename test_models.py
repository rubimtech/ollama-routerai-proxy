import requests
import json
import time
import sys

PROXY_URL = "http://localhost:11436"

MODELS = [
    "deepseek-v4-flash",
    "glm-5.2",
    "qwen3.7-plus",
    "claude-sonnet-5",
    "gemini-3.1-pro-preview",
    "grok-4.5",
    "hy3",
]

PAYLOAD = {
    "model": "",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant. Answer concisely."},
        {"role": "user", "content": "Say hello in exactly 3 words."}
    ],
    "stream": False
}

def test_ollama_chat(model):
    payload = PAYLOAD.copy()
    payload["model"] = model
    headers = {"Content-Type": "application/json"}
    try:
        start = time.time()
        r = requests.post(f"{PROXY_URL}/api/chat", json=payload, headers=headers, timeout=120)
        elapsed = time.time() - start
        if r.status_code != 200:
            return f"FAIL [HTTP {r.status_code}] {r.text[:200]}"
        data = r.json()
        content = data.get("message", {}).get("content", "")
        done = data.get("done", False)
        return f"OK ({elapsed:.1f}s) content={content[:80]!r} done={done}"
    except Exception as e:
        return f"FAIL [{type(e).__name__}] {e}"

def test_openai_chat(model):
    payload = PAYLOAD.copy()
    payload["model"] = model
    headers = {"Content-Type": "application/json"}
    try:
        start = time.time()
        r = requests.post(f"{PROXY_URL}/v1/chat/completions", json=payload, headers=headers, timeout=120)
        elapsed = time.time() - start
        if r.status_code != 200:
            return f"FAIL [HTTP {r.status_code}] {r.text[:200]}"
        data = r.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return f"OK ({elapsed:.1f}s) content={content[:80]!r}"
    except Exception as e:
        return f"FAIL [{type(e).__name__}] {e}"

def main():
    print("=" * 70)
    print("Model Test Suite")
    print(f"Proxy: {PROXY_URL}")
    print("=" * 70)

    # 1. Health check
    print("\n[1] Health check")
    try:
        r = requests.get(f"{PROXY_URL}/", timeout=10)
        print(f"    GET  / -> HTTP {r.status_code} {r.text!r}")
    except Exception as e:
        print(f"    FAIL {e}")
        sys.exit(1)

    # 2. List models
    print("\n[2] Available models via /api/tags")
    try:
        r = requests.get(f"{PROXY_URL}/api/tags", timeout=10)
        data = r.json()
        available = [m["name"] for m in data.get("models", [])]
        print(f"    Total models: {len(available)}")
        for m in MODELS:
            found = m in available
            print(f"    {m}: {'FOUND' if found else 'MISSING'}")
            if not found:
                print(f"    SUGGESTIONS: {[a for a in available if m.split('-')[0] in a][:3]}")
    except Exception as e:
        print(f"    FAIL {e}")

    # 3. Chat via Ollama /api/chat (non-streaming)
    print("\n[3] Ollama /api/chat (non-streaming)")
    for model in MODELS:
        print(f"  {model:40s} ", end="", flush=True)
        result = test_ollama_chat(model)
        print(result)

    # 4. Chat via OpenAI /v1/chat/completions (non-streaming)
    print("\n[4] OpenAI /v1/chat/completions (non-streaming)")
    for model in MODELS:
        print(f"  {model:40s} ", end="", flush=True)
        result = test_openai_chat(model)
        print(result)

    print("\n" + "=" * 70)
    print("Done")

if __name__ == "__main__":
    main()
