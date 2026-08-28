from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    image_url: Optional[str] = None
    thread_id: Optional[str] = None
    user_id: str = "local-user"
    conversation_id: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    name: Optional[str] = None
    status: str = "enabled"
    role_ids: list[str] = Field(default_factory=list)


class UserUpdate(BaseModel):
    username: str
    password: Optional[str] = None
    name: Optional[str] = None
    status: str = "enabled"
    role_ids: list[str] = Field(default_factory=list)


class RoleCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class RoleUpdate(RoleCreate):
    pass


class MenuCreate(BaseModel):
    parent_id: Optional[str] = None
    name: str
    path: str
    component: str
    icon: Optional[str] = None
    sort: int = 0
    visible: bool = True
    permission_code: Optional[str] = None


class MenuUpdate(MenuCreate):
    pass


class ButtonCreate(BaseModel):
    menu_id: str
    name: str
    code: str
    description: Optional[str] = None


class ButtonUpdate(ButtonCreate):
    pass


class IdListRequest(BaseModel):
    ids: list[str]


class DriverCreate(BaseModel):
    name: str
    phone: str
    id_card: Optional[str] = None
    license_no: Optional[str] = None
    status: str = "active"
    rating: float = 5.0
    hired_at: Optional[date] = None


class DriverUpdate(DriverCreate):
    pass


class VehicleCreate(BaseModel):
    plate_no: str
    brand: str
    model: str
    color: Optional[str] = None
    status: str = "idle"
    seat_count: int = 5
    driver_id: Optional[str] = None
    registered_at: Optional[date] = None


class VehicleUpdate(VehicleCreate):
    pass


class ConversationResponse(BaseModel):
    id: str
    title: str
    thread_id: str
    agent_type: str
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    image_url: Optional[str] = None
    created_at: str
