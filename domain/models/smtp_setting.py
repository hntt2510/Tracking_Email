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
      server=data.get("SMTPServer"),
      port=int(data.get("SMTPPort")),
      email=data.get("SMTPEmail"),
      password=data.get("SMTPPass")
    )