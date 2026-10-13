from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    task: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    facts: dict[str, Any] = field(default_factory=dict)
    completed: bool = False
    final_message: str | None = None

    def add_step(self, action: dict[str, Any], result: dict[str, Any]):
        self.steps.append({"action": action, "result": result})
