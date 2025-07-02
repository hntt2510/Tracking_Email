from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class SmtpSetting:
  server: str
  port: int
  email: str
  password: str

  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "SmtpSetting":
    return cls(
      server=data.get("SmtpAddress"),
      port=int(data.get("SmptPort")),
      email=data.get("SmptEmail"),
      password=data.get("SmtpPassword")
    )