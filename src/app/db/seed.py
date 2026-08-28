from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.core.features import HIDDEN_MENU_CODES
from app.core.config import settings
from app.db.models import Button, Menu, Role, User


DEFAULT_MENUS = [
    {"code": "ride", "name": "网约车管理", "path": "/ride", "component": "Layout", "icon": "Van", "sort": 10, "parent": None},
    {"code": "driver", "name": "司机管理", "path": "/ride/drivers", "component": "ride/DriverManagement", "icon": "User", "sort": 11, "parent": "ride"},
    {"code": "ai", "name": "AI管家", "path": "/ai", "component": "Layout", "icon": "Service", "sort": 20, "parent": None},
    {"code": "ai:chef", "name": "私厨管家", "path": "/ai/chef", "component": "ai/ChefHousekeeper", "icon": "Dish", "sort": 21, "parent": "ai"},
    {"code": "permission", "name": "权限管理", "path": "/permissions", "component": "Layout", "icon": "Lock", "sort": 30, "parent": None},
    {"code": "permission:user", "name": "人员管理", "path": "/permissions/users", "component": "permissions/UserManagement", "icon": "UserFilled", "sort": 31, "parent": "permission"},
    {"code": "permission:role", "name": "角色管理", "path": "/permissions/roles", "component": "permissions/RoleManagement", "icon": "Avatar", "sort": 32, "parent": "permission"},
    {"code": "permission:menu", "name": "菜单管理", "path": "/permissions/menus", "component": "permissions/MenuManagement", "icon": "Menu", "sort": 33, "parent": "permission"},
    {"code": "permission:button", "name": "按钮管理", "path": "/permissions/buttons", "component": "permissions/ButtonManagement", "icon": "Pointer", "sort": 34, "parent": "permission"},
]

DEFAULT_BUTTONS = {
    "driver": [
        ("新增司机", "driver:create"),
        ("编辑司机", "driver:update"),
        ("删除司机", "driver:delete"),
    ],
    "permission:user": [
        ("新增人员", "permission:user:create"),
        ("编辑人员", "permission:user:update"),
        ("删除人员", "permission:user:delete"),
    ],
    "permission:role": [
        ("新增角色", "permission:role:create"),
        ("编辑角色", "permission:role:update"),
        ("删除角色", "permission:role:delete"),
    ],
    "permission:menu": [
        ("新增菜单", "permission:menu:create"),
        ("编辑菜单", "permission:menu:update"),
        ("删除菜单", "permission:menu:delete"),
    ],
    "permission:button": [
        ("新增按钮", "permission:button:create"),
        ("编辑按钮", "permission:button:update"),
        ("删除按钮", "permission:button:delete"),
    ],
}


def seed_default_data(db: Session) -> None:
    # Existing development databases may already contain these menus. Retain
    # their records for a later restore, but hide them from every role now.
    for menu in db.scalars(select(Menu).where(Menu.permission_code.in_(HIDDEN_MENU_CODES))):
        menu.visible = False
    db.commit()

    if db.scalar(select(User).where(User.username == settings.auth.default_admin_username)):
        return

    menus_by_code: dict[str, Menu] = {}
    for item in DEFAULT_MENUS:
        menu = Menu(
            name=item["name"],
            path=item["path"],
            component=item["component"],
            icon=item["icon"],
            sort=item["sort"],
            permission_code=item["code"],
        )
        menus_by_code[item["code"]] = menu
        db.add(menu)
    db.flush()

    for item in DEFAULT_MENUS:
        parent_code = item["parent"]
        if parent_code:
            menus_by_code[item["code"]].parent_id = menus_by_code[parent_code].id

    buttons_by_code: dict[str, Button] = {}
    for menu_code, buttons in DEFAULT_BUTTONS.items():
        for name, code in buttons:
            button = Button(menu_id=menus_by_code[menu_code].id, name=name, code=code)
            buttons_by_code[code] = button
            db.add(button)

    super_admin = Role(name="超级管理员", code="super_admin", description="拥有全部菜单和按钮权限")
    operator_admin = Role(name="运营管理员", code="operator_admin", description="拥有网约车和 AI 管家权限")
    support = Role(name="普通客服", code="support", description="拥有查看类权限")

    super_admin.menus = list(menus_by_code.values())
    super_admin.buttons = list(buttons_by_code.values())

    operator_menu_codes = {"ride", "driver", "ai", "ai:chef"}
    operator_admin.menus = [menus_by_code[code] for code in operator_menu_codes]
    operator_admin.buttons = [
        button
        for code, button in buttons_by_code.items()
        if code.startswith("driver:")
    ]

    support_menu_codes = {"ride", "driver", "ai", "ai:chef"}
    support.menus = [menus_by_code[code] for code in support_menu_codes]

    admin = User(
        username=settings.auth.default_admin_username,
        password_hash=hash_password(settings.auth.default_admin_password),
        name="系统管理员",
        status="enabled",
    )
    admin.roles = [super_admin]

    db.add_all([super_admin, operator_admin, support, admin])
    db.commit()
