from dataclasses import dataclass
from typing import Any, List, Union

@dataclass
class ApiResult:
    success: bool
    diag: int
    error: Union[str, List[str], None] = None
    output: Union[str, None] = None
    data: Any = None
