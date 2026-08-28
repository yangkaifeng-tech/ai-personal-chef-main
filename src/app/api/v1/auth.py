from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, verify_password
from app.db.models import User
from app.db.session import get_db
from app.models.schemas import LoginRequest
from app.services.permission_service import (
    build_menu_tree,
    get_user_by_username,
    get_user_menus,
    get_user_permission_codes,
    serialize_user,
)

router = APIRouter()


@router.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, request.username)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if user.status != "enabled":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": serialize_user(user),
        "menus": build_menu_tree(get_user_menus(db, user.id)),
        "permissions": sorted(get_user_permission_codes(db, user.id)),
    }


@router.get("/auth/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "user": serialize_user(user),
        "menus": build_menu_tree(get_user_menus(db, user.id)),
        "permissions": sorted(get_user_permission_codes(db, user.id)),
    }


@router.get("/auth/menus")
def menus(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "menus": build_menu_tree(get_user_menus(db, user.id)),
        "permissions": sorted(get_user_permission_codes(db, user.id)),
    }
