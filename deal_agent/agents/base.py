"""The Agent abstraction: a system prompt + a set of tools, driven by the SDK's
tool runner (it handles the call -> tool-exec -> feed-result loop automatically)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..client import get_client
from ..config import settings
from ..util import file_to_content_block, message_text


@dataclass
class Agent:
    name: str
    system: str
    tools: list = field(default_factory=list)
    model: str = settings.model
    effort: str = settings.effort
    max_tokens: int = settings.max_tokens

    def run(self, prompt: str, attachments: list[str] | None = None) -> str:
        """Run the agent to completion on a prompt and return its final text.

        Args:
            prompt: The instruction / question for the agent.
            attachments: Optional list of image/PDF paths to include with the prompt
                (e.g. a map to interpret).
        """
        content: Any = prompt
        if attachments:
            blocks = [file_to_content_block(p) for p in attachments]
            content = [*blocks, {"type": "text", "text": prompt}]

        client = get_client()
        runner = client.beta.messages.tool_runner(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system,
            thinking={"type": "adaptive"},
            output_config={"effort": self.effort},
            tools=self.tools,
            messages=[{"role": "user", "content": content}],
        )

        final = None
        for message in runner:  # iterates until Claude stops calling tools
            final = message
        return message_text(final)
