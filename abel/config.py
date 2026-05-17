"""Abel runtime configuration — read from environment variables."""
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AbelConfig:
    mode: str         # "online" | "offline"
    local_model: str  # ollama model name for offline mode
    api_key: str | None
    db_path: Path


def load_config() -> AbelConfig:
    mode = os.getenv("ABEL_MODE", "online").lower()
    if mode not in ("online", "offline"):
        mode = "online"
    data_dir = Path(os.getenv("ABEL_DATA_DIR", str(Path.home() / ".abel")))
    return AbelConfig(
        mode=mode,
        local_model=os.getenv("ABEL_LOCAL_MODEL", "llama3.1"),
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        db_path=data_dir / "knowledge.db",
    )
