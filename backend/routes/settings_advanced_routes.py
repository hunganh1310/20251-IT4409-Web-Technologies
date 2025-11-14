from fastapi import Request
@router.post("/settings/advanced/{user_id}/import")
async def import_settings(user_id: str, request: Request):
    data = await request.json()
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    # Overwrite all settings with imported data (simple demo logic)
    fake_db[user_id].notifications = data.get("notifications", fake_db[user_id].notifications)
    fake_db[user_id].privacy = data.get("privacy", fake_db[user_id].privacy)
    fake_db[user_id].theme = data.get("theme", fake_db[user_id].theme)
    fake_db[user_id].language = data.get("language", fake_db[user_id].language)
    fake_db[user_id].security = data.get("security", fake_db[user_id].security)
    return {"detail": "Settings imported"}
@router.get("/settings/advanced/{user_id}/export")
def export_settings(user_id: str):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    return fake_db[user_id].dict()
@router.post("/settings/advanced/{user_id}/reset")
def reset_all_settings(user_id: str):
    from backend.schemas.settings_advanced import UserNotificationSettings, UserPrivacySettings, UserThemeSettings, UserLanguageSettings, UserSecuritySettings
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    fake_db[user_id].notifications = UserNotificationSettings()
    fake_db[user_id].privacy = UserPrivacySettings()
    fake_db[user_id].theme = UserThemeSettings()
    fake_db[user_id].language = UserLanguageSettings()
    fake_db[user_id].security = UserSecuritySettings()
    return {"detail": "All settings reset to default"}
@router.post("/settings/advanced/{user_id}/notifications/toggle")
def toggle_all_notifications(user_id: str, enable: bool = True):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    notif = fake_db[user_id].notifications
    notif.email_notifications = enable
    notif.push_notifications = enable
    notif.sms_notifications = enable
    notif.newsletter_subscribed = enable
    notif.marketing_notifications = enable
    notif.product_updates = enable
    notif.weekly_summary = enable
    notif.app_updates = enable
    notif.event_reminders = enable
    notif.sound_alerts = enable
    fake_db[user_id].notifications = notif
    return notif
@router.get("/settings/advanced/{user_id}/theme", response_model=UserThemeSettings)
def get_theme(user_id: str):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    return fake_db[user_id].theme

@router.get("/settings/advanced/{user_id}/language", response_model=UserLanguageSettings)
def get_language(user_id: str):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    return fake_db[user_id].language

@router.get("/settings/advanced/{user_id}/security", response_model=UserSecuritySettings)
def get_security(user_id: str):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    return fake_db[user_id].security

@router.delete("/settings/advanced/{user_id}/theme")
def delete_theme(user_id: str):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    fake_db[user_id].theme = UserThemeSettings()
    return {"detail": "Theme reset to default"}

@router.delete("/settings/advanced/{user_id}/language")
def delete_language(user_id: str):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    fake_db[user_id].language = UserLanguageSettings()
    return {"detail": "Language reset to default"}

@router.delete("/settings/advanced/{user_id}/security")
def delete_security(user_id: str):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    fake_db[user_id].security = UserSecuritySettings()
    return {"detail": "Security reset to default"}
from fastapi import Body
@router.put("/settings/advanced/{user_id}/theme", response_model=UserThemeSettings)
def update_theme(user_id: str, theme: UserThemeSettings = Body(...)):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    fake_db[user_id].theme = theme
    return theme

@router.put("/settings/advanced/{user_id}/language", response_model=UserLanguageSettings)
def update_language(user_id: str, language: UserLanguageSettings = Body(...)):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    fake_db[user_id].language = language
    return language

@router.put("/settings/advanced/{user_id}/security", response_model=UserSecuritySettings)
def update_security(user_id: str, security: UserSecuritySettings = Body(...)):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    fake_db[user_id].security = security
    return security
from fastapi import APIRouter, HTTPException
from backend.schemas.settings_advanced import (
    UserSettingsUpdateRequest, UserSettingsResponse,
    UserNotificationSettings, UserPrivacySettings, UserThemeSettings, UserLanguageSettings, UserSecuritySettings
)
from typing import Dict

router = APIRouter()

fake_db: Dict[str, UserSettingsResponse] = {}

@router.get("/settings/advanced/{user_id}", response_model=UserSettingsResponse)
def get_advanced_settings(user_id: str):
    if user_id not in fake_db:
        fake_db[user_id] = UserSettingsResponse(
            user_id=user_id,
            notifications=UserNotificationSettings(),
            privacy=UserPrivacySettings(),
            theme=UserThemeSettings(),
            language=UserLanguageSettings(),
            security=UserSecuritySettings()
        )
    return fake_db[user_id]

@router.put("/settings/advanced/{user_id}", response_model=UserSettingsResponse)
def update_advanced_settings(user_id: str, req: UserSettingsUpdateRequest):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    current = fake_db[user_id]
    if req.notifications:
        current.notifications = req.notifications
    if req.privacy:
        current.privacy = req.privacy
    if req.theme:
        current.theme = req.theme
    if req.language:
        current.language = req.language
    if req.security:
        current.security = req.security
    fake_db[user_id] = current
    return current

@router.put("/settings/advanced/{user_id}/notifications", response_model=UserNotificationSettings)
def update_notifications(user_id: str, notifications: UserNotificationSettings):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    fake_db[user_id].notifications = notifications
    return notifications

@router.put("/settings/advanced/{user_id}/privacy", response_model=UserPrivacySettings)
def update_privacy(user_id: str, privacy: UserPrivacySettings):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    fake_db[user_id].privacy = privacy
    return privacy
