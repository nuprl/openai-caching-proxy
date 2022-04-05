from typing import List
import json
import requests

base_url = ""


def set_base_url(url: str):
    global base_url
    base_url = url


def completion(
    engine: str,
    prompt: str,
    temperature: float = 1.0,
    max_tokens: int = 16,
    top_p: float = 1.0,
    stop: List[str] = [],
    presence_penalty: float = 0.0,
    frequency_penalty: float = 0.0,
    n: int = 1,
):
    body = {
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "stop": stop,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "n": n,
    }
    resp = requests.post(f"{base_url}/completion/{engine}", json=json.dumps(body))
    return resp.json()
