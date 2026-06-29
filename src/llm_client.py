"""
LLM client for the RBL-4 experiment.

Two implementations behind ONE interface, call_llm(system, user, use_mock):
- call_llm_mock: offline fake. No API key, no cost. Lets us build and test
  the whole pipeline while waiting for the key and the real data.
- call_llm_real: the real OpenAI call (gpt-4o-mini, temperature 0.0, JSON
  mode) with exponential-backoff retry on rate limits.

Both return the SAME tuple:
    (raw_text, response_model, usage)
where:
    raw_text       : the raw string the model returned ("" on empty)
    response_model : which model actually served the request
    usage          : dict {prompt_tokens, completion_tokens} or None
"""

import json
import time
import os

from prompt_config import MODEL_API_ID, TEMPERATURE


# ---- Pricing (USD per 1,000,000 tokens) for cost logging only. ----
# gpt-4o-mini, confirmed 2026: $0.15 / 1M input, $0.60 / 1M output.
PRICE_INPUT_PER_M = 0.15
PRICE_OUTPUT_PER_M = 0.60


def estimate_cost(usage):
    if not usage:
        return 0.0
    pt = usage.get("prompt_tokens", 0) or 0
    ct = usage.get("completion_tokens", 0) or 0
    return pt / 1_000_000 * PRICE_INPUT_PER_M + ct / 1_000_000 * PRICE_OUTPUT_PER_M


# ===================== MOCK (offline) =====================
def call_llm_mock(system_prompt, user_prompt):
    """Return a deterministic fake response so we can test the pipeline
    end-to-end with no key and no cost.

    Two sentinel strings let us exercise the INVALID path on purpose:
      - "SIMULATE_EMPTY"   -> empty response  (-> INVALID: empty_response)
      - "SIMULATE_BADJSON" -> non-JSON text   (-> INVALID: parse_error)
    Any other input returns valid JSON with simple keyword-based labels,
    just so the dummy output looks varied and realistic.
    """
    fake_usage = {"prompt_tokens": 350, "completion_tokens": 120}

    if "SIMULATE_EMPTY" in user_prompt:
        return "", "mock-gpt-4o-mini", fake_usage
    if "SIMULATE_BADJSON" in user_prompt:
        return "OB is sufficient, EB missing (this is not JSON)", "mock-gpt-4o-mini", fake_usage

    text = user_prompt.lower()

    def guess(clear, vague):
        if clear:
            return "Sufficient"
        if vague:
            return "Ambiguous"
        return "Missing"

    ob = guess("error" in text or "crash" in text or "keyerror" in text,
               "wrong" in text or "broken" in text or "not work" in text)
    eb = guess("should" in text or "expected" in text, "normally" in text)
    s2r = guess("step" in text or "1." in text or "run " in text, "try" in text)

    payload = {
        "OB": {"label": ob, "reason": "mock reason for OB"},
        "EB": {"label": eb, "reason": "mock reason for EB"},
        "S2R": {"label": s2r, "reason": "mock reason for S2R"},
    }
    return json.dumps(payload), "mock-gpt-4o-mini", fake_usage


# ===================== REAL (OpenAI) =====================
def call_llm_real(system_prompt, user_prompt, max_retries=5):
    """Call gpt-4o-mini with temperature 0.0 and JSON mode.

    JSON mode (response_format={"type":"json_object"}) forces the model to
    return syntactically valid JSON. This removes the most common cause of
    fake-INVALID rows: the model wrapping its JSON in ``` code fences.
    OpenAI requires the word "json" to appear somewhere in the prompt for
    this mode; our system prompt already says "Return STRICTLY this JSON
    object", so we satisfy that.

    Exponential backoff: on a rate-limit / transient error we wait
    1s, 2s, 4s, 8s... (doubling) before retrying, up to max_retries. Doubling
    the wait avoids hammering the API and getting blocked again immediately.
    """
    # Imported here so the mock path needs zero dependency on the SDK.
    from openai import OpenAI
    from openai import (RateLimitError, APIError,
                        APITimeoutError, APIConnectionError)

    #client = OpenAI()  # reads OPENAI_API_KEY from the environment
    # base_url đọc từ .env (OPENAI_BASE_URL). Nếu không có -> mặc định OpenAI chính chủ.
    # Cho phép trỏ sang API tương thích OpenAI của bên thứ ba khi nhóm đã đồng ý.
    client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL") or None)

    last_error = None
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL_API_ID,
                temperature=TEMPERATURE,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = resp.choices[0].message.content or ""
            usage = None
            if resp.usage is not None:
                usage = {
                    "prompt_tokens": resp.usage.prompt_tokens,
                    "completion_tokens": resp.usage.completion_tokens,
                }
            return text, resp.model, usage

        except (RateLimitError, APITimeoutError, APIConnectionError, APIError) as e:
            # Transient / server-side error -> wait and retry (backoff).
            last_error = e
            time.sleep(2 ** attempt)

    # All retries exhausted -> raise so the caller logs it and marks INVALID.
    raise RuntimeError(f"OpenAI call failed after {max_retries} retries: {last_error}")


def call_llm(system_prompt, user_prompt, use_mock):
    if use_mock:
        return call_llm_mock(system_prompt, user_prompt)
    return call_llm_real(system_prompt, user_prompt)
