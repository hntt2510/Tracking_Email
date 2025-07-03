from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class ScheduleInfo:
  id: int
  type: str
  status: str
  hour: int
  minute: int

  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "ScheduleInfo":
    return cls(
      id=int(data.get("JobId")),
      type=data.get("JobType"),
      status=data.get("JobStatus"),
      hour=int(data.get("Hour")),
      minute=int(data.get("Minute"))
    )