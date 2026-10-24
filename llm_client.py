"""
ASI-1 and OpenAI-compatible LLM Client.
Supports structured JSON parsing, error resilience, and automatic Agentverse key detection.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import config
import http_client

logger = logging.getLogger("launchkit.llm")


def get_api_key() -> str:
    """Retrieve injected ASI-1 key from Agentverse or environment."""
    for key in ("ASI1_API_KEY", "ASI_API_KEY", "ASI_ONE_API_KEY"):
        val = os.getenv(key)
        if val and val.strip():
            return val.strip()
    return ""


def is_available() -> bool:
    """Check if an LLM key is configured."""
    return bool(get_api_key())


def chat(
    messages: List[Dict[str, str]],
    max_tokens: int = 1200,
    temperature: float = 0.7,
    timeout: int = 25,
) -> Tuple[Optional[str], str]:
    """Send chat messages to ASI-1 completions API."""
    key = get_api_key()
    if not key:
        return None, "No ASI-1 API key found"

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.ASI_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        url = config.get_asi_base_url()
        resp = http_client.post(url, json_data=payload, headers=headers, timeout=timeout)
        if resp.status_code >= 400:
            err = f"HTTP {resp.status_code}: {resp.text[:140].replace(chr(10), ' ')}"
            logger.warning(f"LLM request error: {err}")
            return None, err

        data = resp.json()
        choices = data.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "").strip()
            return content, ""
        return None, "Empty reply choices from model"
    except Exception as e:
        logger.warning(f"LLM exception: {e}")
        return None, str(e)


def single_prompt(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1200,
    temperature: float = 0.7,
) -> Tuple[Optional[str], str]:
    """Execute a simple system + user prompt pair."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return chat(messages, max_tokens=max_tokens, temperature=temperature)


def extract_json(raw: str) -> Optional[Any]:
    """Strip markdown formatting and parse JSON safely."""
    if not raw:
        return None
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        # Search for first { ... } or [ ... ] block
        m = re.search(r"(\{.*\}|\[.*\])", cleaned, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    return None
