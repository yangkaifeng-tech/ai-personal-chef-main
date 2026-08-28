from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_permission
from app.core.features import HIDDEN_MENU_CODES
from app.db.models import Button, Menu, Role, User
from app.db.session import get_db
from app.models.schemas import (
    ButtonCreate,
    ButtonUpdate,
    IdListRequest,
    MenuCreate,
    MenuUpdate,
    RoleCreate,
    RoleUpdate,
    UserCreate,
    UserUpdate,
)
from app.services.permission_service import (
    build_menu_tree,
    create_button,
    create_menu,
    create_role,
    create_user,
    delete_button,
    delete_menu,
    delete_role,
    delete_user,
    serialize_button,
    serialize_menu,
    serialize_role,
    serialize_user,
    set_role_buttons,
    set_role_menus,
    set_user_roles,
    update_button,
    update_menu,
    update_role,
    update_user,
)

router = APIRouter()


@router.get("/permissions/users")
def list_users(
    keyword: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(User)
    if keyword:
        like = f"%{keyword}%"
        statement = statement.where((User.username.like(like)) | (User.name.like(like)))
    if status:
        statement = statement.where(User.status == status)
    items = list(db.scalars(statement.order_by(User.created_at.desc())))
    start = (page - 1) * page_size
    return {"items": [serialize_user(item) for item in items[start:start + page_size]], "total": len(items)}


@router.post("/permissions/users")
def add_user(
    request: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:user:create")),
):
    user = create_user(db, request.username, request.password, request.name, request.status, request.role_ids)
    return serialize_user(user)


@router.put("/permissions/users/{user_id}")
def edit_user(
    user_id: str,
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:user:update")),
):
    user = update_user(db, user_id, request.username, request.name, request.status, request.role_ids, request.password)
    return serialize_user(user)


@router.delete("/permissions/users/{user_id}")
def remove_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:user:delete")),
):
    delete_user(db, user_id)
    return {"success": True}


@router.put("/permissions/users/{user_id}/roles")
def assign_user_roles(
    user_id: str,
    request: IdListRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:user:update")),
):
    user = set_user_roles(db, user_id, request.ids)
    return serialize_user(user)


@router.get("/permissions/roles")
def list_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    roles = db.scalars(select(Role).order_by(Role.created_at.desc())).all()
    return {"items": [serialize_role(role) for role in roles]}


@router.post("/permissions/roles")
def add_role(
    request: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:role:create")),
):
    role = create_role(db, request.name, request.code, request.description)
    return serialize_role(role)


@router.put("/permissions/roles/{role_id}")
def edit_role(
    role_id: str,
    request: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:role:update")),
):
    role = update_role(db, role_id, request.name, request.code, request.description)
    return serialize_role(role)


@router.delete("/permissions/roles/{role_id}")
def remove_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:role:delete")),
):
    delete_role(db, role_id)
    return {"success": True}


@router.put("/permissions/roles/{role_id}/menus")
def assign_role_menus(
    role_id: str,
    request: IdListRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:role:update")),
):
    role = set_role_menus(db, role_id, request.ids)
    return serialize_role(role)


@router.put("/permissions/roles/{role_id}/buttons")
def assign_role_buttons(
    role_id: str,
    request: IdListRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:role:update")),
):
    role = set_role_buttons(db, role_id, request.ids)
    return serialize_role(role)


@router.get("/permissions/menus")
def list_menus(
    tree: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    menus = list(
        db.scalars(
            select(Menu)
            .where(Menu.permission_code.not_in(HIDDEN_MENU_CODES))
            .order_by(Menu.sort.asc(), Menu.name.asc())
        )
    )
    if tree:
        return {"items": build_menu_tree(menus)}
    return {"items": [serialize_menu(menu) for menu in menus]}


@router.post("/permissions/menus")
def add_menu(
    request: MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:menu:create")),
):
    menu = create_menu(
        db,
        request.parent_id,
        request.name,
        request.path,
        request.component,
        request.icon,
        request.sort,
        request.visible,
        request.permission_code,
    )
    return serialize_menu(menu)


@router.put("/permissions/menus/{menu_id}")
def edit_menu(
    menu_id: str,
    request: MenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:menu:update")),
):
    menu = update_menu(
        db,
        menu_id,
        request.parent_id,
        request.name,
        request.path,
        request.component,
        request.icon,
        request.sort,
        request.visible,
        request.permission_code,
    )
    return serialize_menu(menu)


@router.delete("/permissions/menus/{menu_id}")
def remove_menu(
    menu_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:menu:delete")),
):
    delete_menu(db, menu_id)
    return {"success": True}


@router.get("/permissions/buttons")
def list_buttons(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    buttons = db.scalars(select(Button).order_by(Button.code.asc())).all()
    return {"items": [serialize_button(button) for button in buttons]}


@router.post("/permissions/buttons")
def add_button(
    request: ButtonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:button:create")),
):
    button = create_button(db, request.menu_id, request.name, request.code, request.description)
    return serialize_button(button)


@router.put("/permissions/buttons/{button_id}")
def edit_button(
    button_id: str,
    request: ButtonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:button:update")),
):
    button = update_button(db, button_id, request.menu_id, request.name, request.code, request.description)
    return serialize_button(button)


@router.delete("/permissions/buttons/{button_id}")
def remove_button(
    button_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permission:button:delete")),
):
    delete_button(db, button_id)
    return {"success": True}
