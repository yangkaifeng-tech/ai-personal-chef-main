from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.core.features import HIDDEN_MENU_CODES
from app.db.models import Button, Menu, Role, User


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def get_user_permission_codes(db: Session, user_id: str) -> set[str]:
    user = db.get(User, user_id)
    if not user:
        return set()
    return {button.code for role in user.roles for button in role.buttons}


def get_user_menus(db: Session, user_id: str) -> list[Menu]:
    user = db.get(User, user_id)
    if not user:
        return []

    menus_by_id: dict[str, Menu] = {}
    for role in user.roles:
        for menu in role.menus:
            if menu.visible and menu.permission_code not in HIDDEN_MENU_CODES:
                menus_by_id[menu.id] = menu
    return sorted(menus_by_id.values(), key=lambda item: (item.sort, item.name))


def build_menu_tree(menus: list[Menu]) -> list[dict[str, object]]:
    children_by_parent: dict[str | None, list[Menu]] = defaultdict(list)
    menu_ids = {menu.id for menu in menus}
    for menu in menus:
        parent_id = menu.parent_id if menu.parent_id in menu_ids else None
        children_by_parent[parent_id].append(menu)

    def serialize(menu: Menu) -> dict[str, object]:
        return {
            "id": menu.id,
            "parent_id": menu.parent_id,
            "name": menu.name,
            "path": menu.path,
            "component": menu.component,
            "icon": menu.icon,
            "sort": menu.sort,
            "visible": menu.visible,
            "permission_code": menu.permission_code,
            "children": [serialize(child) for child in sorted(children_by_parent[menu.id], key=lambda item: item.sort)],
        }

    return [serialize(menu) for menu in sorted(children_by_parent[None], key=lambda item: item.sort)]


def serialize_user(user: User) -> dict[str, object]:
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "status": user.status,
        "role_ids": [role.id for role in user.roles],
        "created_at": user.created_at.isoformat(),
    }


def serialize_role(role: Role) -> dict[str, object]:
    return {
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "description": role.description,
        "menu_ids": [menu.id for menu in role.menus],
        "button_ids": [button.id for button in role.buttons],
        "created_at": role.created_at.isoformat(),
    }


def serialize_menu(menu: Menu) -> dict[str, object]:
    return {
        "id": menu.id,
        "parent_id": menu.parent_id,
        "name": menu.name,
        "path": menu.path,
        "component": menu.component,
        "icon": menu.icon,
        "sort": menu.sort,
        "visible": menu.visible,
        "permission_code": menu.permission_code,
    }


def serialize_button(button: Button) -> dict[str, object]:
    return {
        "id": button.id,
        "menu_id": button.menu_id,
        "name": button.name,
        "code": button.code,
        "description": button.description,
    }


def create_user(db: Session, username: str, password: str, name: str | None, status: str, role_ids: list[str]) -> User:
    if get_user_by_username(db, username):
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=username, password_hash=hash_password(password), name=name, status=status)
    user.roles = list(db.scalars(select(Role).where(Role.id.in_(role_ids)))) if role_ids else []
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session,
    user_id: str,
    username: str,
    name: str | None,
    status: str,
    role_ids: list[str],
    password: str | None = None,
) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = get_user_by_username(db, username)
    if existing and existing.id != user_id:
        raise HTTPException(status_code=400, detail="Username already exists")
    user.username = username
    user.name = name
    user.status = status
    if password:
        user.password_hash = hash_password(password)
    user.roles = list(db.scalars(select(Role).where(Role.id.in_(role_ids)))) if role_ids else []
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: str) -> None:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


def set_user_roles(db: Session, user_id: str, role_ids: list[str]) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.roles = list(db.scalars(select(Role).where(Role.id.in_(role_ids)))) if role_ids else []
    db.commit()
    db.refresh(user)
    return user


def create_role(db: Session, name: str, code: str, description: str | None) -> Role:
    existing = db.scalar(select(Role).where(Role.code == code))
    if existing:
        raise HTTPException(status_code=400, detail="Role code already exists")
    role = Role(name=name, code=code, description=description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role_id: str, name: str, code: str, description: str | None) -> Role:
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    existing = db.scalar(select(Role).where(Role.code == code))
    if existing and existing.id != role_id:
        raise HTTPException(status_code=400, detail="Role code already exists")
    role.name = name
    role.code = code
    role.description = description
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: str) -> None:
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role)
    db.commit()


def set_role_menus(db: Session, role_id: str, menu_ids: list[str]) -> Role:
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    role.menus = list(db.scalars(select(Menu).where(Menu.id.in_(menu_ids)))) if menu_ids else []
    db.commit()
    db.refresh(role)
    return role


def set_role_buttons(db: Session, role_id: str, button_ids: list[str]) -> Role:
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    role.buttons = list(db.scalars(select(Button).where(Button.id.in_(button_ids)))) if button_ids else []
    db.commit()
    db.refresh(role)
    return role


def create_menu(
    db: Session,
    parent_id: str | None,
    name: str,
    path: str,
    component: str,
    icon: str | None,
    sort: int,
    visible: bool,
    permission_code: str | None,
) -> Menu:
    if parent_id and not db.get(Menu, parent_id):
        raise HTTPException(status_code=404, detail="Parent menu not found")
    menu = Menu(
        parent_id=parent_id,
        name=name,
        path=path,
        component=component,
        icon=icon,
        sort=sort,
        visible=visible,
        permission_code=permission_code,
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


def update_menu(
    db: Session,
    menu_id: str,
    parent_id: str | None,
    name: str,
    path: str,
    component: str,
    icon: str | None,
    sort: int,
    visible: bool,
    permission_code: str | None,
) -> Menu:
    menu = db.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    if parent_id == menu_id:
        raise HTTPException(status_code=400, detail="Menu cannot be its own parent")
    if parent_id and not db.get(Menu, parent_id):
        raise HTTPException(status_code=404, detail="Parent menu not found")
    menu.parent_id = parent_id
    menu.name = name
    menu.path = path
    menu.component = component
    menu.icon = icon
    menu.sort = sort
    menu.visible = visible
    menu.permission_code = permission_code
    db.commit()
    db.refresh(menu)
    return menu


def delete_menu(db: Session, menu_id: str) -> None:
    menu = db.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    db.delete(menu)
    db.commit()


def create_button(db: Session, menu_id: str, name: str, code: str, description: str | None) -> Button:
    if not db.get(Menu, menu_id):
        raise HTTPException(status_code=404, detail="Menu not found")
    existing = db.scalar(select(Button).where(Button.code == code))
    if existing:
        raise HTTPException(status_code=400, detail="Button code already exists")
    button = Button(menu_id=menu_id, name=name, code=code, description=description)
    db.add(button)
    db.commit()
    db.refresh(button)
    return button


def update_button(db: Session, button_id: str, menu_id: str, name: str, code: str, description: str | None) -> Button:
    button = db.get(Button, button_id)
    if not button:
        raise HTTPException(status_code=404, detail="Button not found")
    if not db.get(Menu, menu_id):
        raise HTTPException(status_code=404, detail="Menu not found")
    existing = db.scalar(select(Button).where(Button.code == code))
    if existing and existing.id != button_id:
        raise HTTPException(status_code=400, detail="Button code already exists")
    button.menu_id = menu_id
    button.name = name
    button.code = code
    button.description = description
    db.commit()
    db.refresh(button)
    return button


def delete_button(db: Session, button_id: str) -> None:
    button = db.get(Button, button_id)
    if not button:
        raise HTTPException(status_code=404, detail="Button not found")
    db.delete(button)
    db.commit()
