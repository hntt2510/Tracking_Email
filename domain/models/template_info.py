from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class TemplateInfo:
  id: int
  subject: str
  html_url: str

  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "TemplateInfo":
    return cls(
      id=int(data.get("EmailTemplateId")),
      subject=data.get("EmailSubject"),
      html_url=data.get("EmailHtmlUrl")
    )