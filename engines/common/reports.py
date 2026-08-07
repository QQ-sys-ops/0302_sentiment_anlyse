from pathlib import Path
from engines.contracts.settings import get_settings
from engines.contracts.agent_roles import RoleKey


def get_output_dir(task_id: str, role: RoleKey) -> str:
    return str(Path(get_settings().RUNTIME_DIR) / f"{task_id}/{role}")
