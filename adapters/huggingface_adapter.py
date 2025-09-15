import os
import requests
import time
from typing import Dict, Any, Optional

HF_API_BASE = "https://api-inference.huggingface.co/models"

class HuggingFaceAdapter:
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.2", token: Optional[str] = None, timeout: int = 60):
        self.model = model
        self.token = token or os.environ.get("HF_TOKEN")
        if not self.token:
            raise RuntimeError("HF_TOKEN not found. Set environment variable HF_TOKEN with your Hugging Face token.")
        self.timeout = timeout
        self.headers = {"Authorization": f"Bearer {self.token}", "User-Agent": "PromptLab/1.0 (+https://github.com)"}

    def generate(self, inputs: str, max_new_tokens: int = 256, temperature: float = 0.2, top_p: float = 0.95) -> Dict[str, Any]:
        url = f"{HF_API_BASE}/{self.model}"
        payload = {
            "inputs": inputs,
            "parameters": {"max_new_tokens": max_new_tokens, "temperature": temperature, "top_p": top_p},
            "options": {"wait_for_model": True}
        }
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=self.timeout)
        except requests.exceptions.RequestException as e:
            # Backoff and retry once
            time.sleep(1.0)
            resp = requests.post(url, headers=self.headers, json=payload, timeout=self.timeout)

        if resp.status_code != 200:
            raise RuntimeError(f"Hugging Face API error {resp.status_code}: {resp.text}")

        data = resp.json()
        # Some models return [{'generated_text': '...'}] others return dicts
        if isinstance(data, list) and len(data) > 0 and 'generated_text' in data[0]:
            return {"text": data[0]['generated_text']}
        if isinstance(data, dict) and 'generated_text' in data:
            return {"text": data['generated_text']}
        if isinstance(data, dict) and 'error' in data:
            raise RuntimeError("Model error: " + data.get('error'))
        # Fallback: stringify
        return {"text": str(data)}
