"""Model backends behind one small interface.

Free-first (see docs/adr/0002): the default provider is a local Ollama model.
The Anthropic backend is opt-in and reads credentials from the environment
(ANTHROPIC_API_KEY) - keys are never passed in code or stored in files.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from ai_app.telemetry import cost_usd, log_call


@dataclass(frozen=True)
class LLMResponse:
    text: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float

    @property
    def cost_usd(self) -> float:
        return cost_usd(self.model, self.input_tokens, self.output_tokens)


class LLMClient(Protocol):
    def complete(self, prompt: str, system: str | None = None) -> LLMResponse: ...


class OllamaClient:
    """Local model via Ollama's /api/chat. Free; needs `ollama serve` running."""

    def __init__(self, model: str | None = None, base_url: str | None = None) -> None:
        self.model = model or os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
        self.base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    def complete(self, prompt: str, system: str | None = None) -> LLMResponse:
        messages = [{"role": "system", "content": system}] if system else []
        messages.append({"role": "user", "content": prompt})
        body = json.dumps({"model": self.model, "messages": messages, "stream": False}).encode()
        req = urllib.request.Request(
            f"{self.base_url}/api/chat", data=body, headers={"Content-Type": "application/json"}
        )
        start = time.perf_counter()
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
        return LLMResponse(
            text=data["message"]["content"],
            provider="ollama",
            model=self.model,
            input_tokens=data.get("prompt_eval_count", 0),
            output_tokens=data.get("eval_count", 0),
            latency_ms=(time.perf_counter() - start) * 1000,
        )


class AnthropicClient:
    """Claude via the official SDK. Paid; install with `uv sync --extra anthropic`."""

    def __init__(self, model: str | None = None) -> None:
        import anthropic  # lazy: only required when this backend is selected

        self.model = model or os.environ.get("ANTHROPIC_MODEL", "claude-haiku-5-5")
        self._client = anthropic.Anthropic()  # credentials resolved from the environment

    def complete(self, prompt: str, system: str | None = None) -> LLMResponse:
        kwargs = {"system": system} if system else {}
        start = time.perf_counter()
        response = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            output_config={"effort": "low"},  # cheapest setting; raise per task if evals demand
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        text = "".join(b.text for b in response.content if b.type == "text")
        return LLMResponse(
            text=text,
            provider="anthropic",
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=(time.perf_counter() - start) * 1000,
        )


class ReplayClient:
    """Returns recorded outputs keyed by prompt. Free and deterministic - used by CI evals."""

    def __init__(self, recordings: dict[str, str], model: str = "replay") -> None:
        self.recordings = recordings
        self.model = model

    def complete(self, prompt: str, system: str | None = None) -> LLMResponse:
        if prompt not in self.recordings:
            raise KeyError(
                f"No recording for prompt; re-record with --mode live --record: {prompt!r}"
            )
        return LLMResponse(self.recordings[prompt], "replay", self.model, 0, 0, 0.0)


def get_client() -> LLMClient:
    provider = os.environ.get("LLM_PROVIDER", "ollama").lower()
    if provider == "ollama":
        return OllamaClient()
    if provider == "anthropic":
        return AnthropicClient()
    raise ValueError(f"Unknown LLM_PROVIDER={provider!r} (expected 'ollama' or 'anthropic')")


def complete_logged(client: LLMClient, prompt: str, system: str | None = None) -> LLMResponse:
    """Call the model and append a cost/latency record to the telemetry log."""
    response = client.complete(prompt, system)
    log_call(response)
    return response
