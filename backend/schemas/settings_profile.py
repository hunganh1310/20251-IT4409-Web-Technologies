from pydantic import BaseModel
from typing import Optional

class SettingsProfile(BaseModel):
    username: str
    email: str
    theme: Optional[str] = "light"
    language: Optional[str] = "en"
    notifications_enabled: Optional[bool] = True
