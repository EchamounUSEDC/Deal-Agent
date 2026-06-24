"""
Optional LLM narrative layer for the IC agent toolkit.

Every agent works fully WITHOUT this module \u2014 the deterministic, rule-based
output is the default.  When an ANTHROPIC_API_KEY is present, agents can call
polish() to turn structured findings into committee-ready prose.

This keeps numbers and screen logic auditable (rule-based) while letting
the LLM handle wording only.  Set the key with:
    export ANTHROPIC_API_KEY=sk-ant-...

Changelog vs. original:
  - Retries up to _MAX_RETRIES times on transient HTTP errors (429, 5xx)
    with exponential backoff (_BACKOFF_BASE seconds, doubling each attempt)
  - Logs a warning for each retry and on final fallback, so the calling agent
    can see why it got deterministic text instead of LLM prose
"""
import os, json, time, urllib.request, urllib.error
import logging

log = logging.getLogger(__name__)

MODEL    = "claude-sonnet-4-6"
ENDPOINT = "https://api.anthropic.com/v1/messages"

# Retry config
_MAX_RETRIES    = 3
_RETRY_STATUSES = {429, 500, 502, 503, 529}   # transient; worth retrying
_BACKOFF_BASE   = 1.5                          # seconds; doubles each attempt


def available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def polish(system: str, user: str, max_tokens: int = 700, fallback: str = "") -> str:
    """Return LLM prose, or `fallback` (deterministic text) if no key or on error.

    Retries up to _MAX_RETRIES times on transient HTTP errors with exponential
    backoff.  Every retry and the final fallback are logged at WARNING level so
    operators can diagnose connectivity issues without inspecting return values.
    """
    if not available():
        return fallback

    body = json.dumps({
        "model":      MODEL,
        "max_tokens": max_tokens,
        "system":     system,
        "messages":   [{"role": "user", "content": user}],
    }).encode()

    for attempt in range(_MAX_RETRIES):
        try:
            req = urllib.request.Request(
                ENDPOINT,
                data=body,
                headers={
                    "content-type":      "application/json",
                    "x-api-key":         os.environ["ANTHROPIC_API_KEY"],
                    "anthropic-version": "2023-06-01",
                },
            )
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.load(r)

            text = "".join(
                b.get("text", "") for b in data.get("content", [])
                if b.get("type") == "text"
            ).strip()
            return text or fallback

        except urllib.error.HTTPError as exc:
            if exc.code in _RETRY_STATUSES and attempt < _MAX_RETRIES - 1:
                wait = _BACKOFF_BASE * (2 ** attempt)
                log.warning(
                    "LLM polish: HTTP %s on attempt %d/%d \u2014 retrying in %.1fs",
                    exc.code, attempt + 1, _MAX_RETRIES, wait,
                )
                time.sleep(wait)
            else:
                log.warning(
                    "LLM polish: HTTP %s \u2014 falling back to deterministic text", exc.code
                )
                return fallback

        except Exception as exc:  # noqa: BLE001
            if attempt < _MAX_RETRIES - 1:
                wait = _BACKOFF_BASE * (2 ** attempt)
                log.warning(
                    "LLM polish: %s on attempt %d/%d \u2014 retrying in %.1fs",
                    type(exc).__name__, attempt + 1, _MAX_RETRIES, wait,
                )
                time.sleep(wait)
            else:
                log.warning(
                    "LLM polish: %s after %d attempts \u2014 falling back to deterministic text",
                    type(exc).__name__, _MAX_RETRIES,
                )
                return fallback

    return fallback   # unreachable; satisfies type checkers


# House guardrail for any narrative the toolkit generates.
IC_SYSTEM = (
    "You are drafting for a real-estate Investment Committee at D1 Real Estate.  "
    "Be concise, neutral, and decision-useful.  Never invent figures \u2014 use only the "
    "numbers provided.  The committee, not you, makes the Go/No-Go call; present the "
    "case and the risks, do not recommend a decision."
)
