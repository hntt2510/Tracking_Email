from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class ReceiverInfo:
  fullname: str
  email: str
  company: str
  phone: str

  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "ReceiverInfo":
    return cls(
      fullname=data.get("FullName"),
      email=data.get("Email"),
      company=data.get("Company"),
      phone=data.get("Phone")
    )