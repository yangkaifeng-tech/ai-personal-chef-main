from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.db.models import Driver, Role, User, Vehicle
from app.db.session import SessionLocal, init_db


DEMO_USERS = [
    {"username": "operator", "password": "operator123", "name": "运营管理员", "role_code": "operator_admin"},
    {"username": "support", "password": "support123", "name": "普通客服", "role_code": "support"},
    {"username": "manager", "password": "manager123", "name": "车队经理", "role_code": "operator_admin"},
]

DEMO_DRIVERS = [
    {"name": "张伟", "phone": "13800001001", "id_card": "310101199001010011", "license_no": "沪驾A1001", "status": "active", "rating": 4.9, "hired_at": date(2023, 2, 12)},
    {"name": "王强", "phone": "13800001002", "id_card": "310101199103120022", "license_no": "沪驾A1002", "status": "active", "rating": 4.8, "hired_at": date(2023, 4, 18)},
    {"name": "李娜", "phone": "13800001003", "id_card": "310101199207230033", "license_no": "沪驾A1003", "status": "active", "rating": 4.7, "hired_at": date(2023, 7, 2)},
    {"name": "赵磊", "phone": "13800001004", "id_card": "310101198812050044", "license_no": "沪驾A1004", "status": "disabled", "rating": 4.5, "hired_at": date(2022, 11, 9)},
    {"name": "陈晨", "phone": "13800001005", "id_card": "310101199505170055", "license_no": "沪驾A1005", "status": "active", "rating": 5.0, "hired_at": date(2024, 1, 6)},
    {"name": "刘洋", "phone": "13800001006", "id_card": "310101199406280066", "license_no": "沪驾A1006", "status": "active", "rating": 4.6, "hired_at": date(2024, 3, 15)},
    {"name": "孙浩", "phone": "13800001007", "id_card": "310101198911110077", "license_no": "沪驾A1007", "status": "left", "rating": 4.2, "hired_at": date(2021, 8, 20)},
    {"name": "周敏", "phone": "13800001008", "id_card": "310101199612310088", "license_no": "沪驾A1008", "status": "active", "rating": 4.9, "hired_at": date(2024, 6, 1)},
    {"name": "吴迪", "phone": "13800001009", "id_card": "310101199302140099", "license_no": "沪驾A1009", "status": "active", "rating": 4.4, "hired_at": date(2023, 9, 27)},
    {"name": "郑凯", "phone": "13800001010", "id_card": "310101199010100100", "license_no": "沪驾A1010", "status": "disabled", "rating": 4.1, "hired_at": date(2022, 5, 5)},
    {"name": "钱雪", "phone": "13800001011", "id_card": "310101199808080111", "license_no": "沪驾A1011", "status": "active", "rating": 4.8, "hired_at": date(2025, 1, 10)},
    {"name": "何峰", "phone": "13800001012", "id_card": "310101198706060122", "license_no": "沪驾A1012", "status": "active", "rating": 4.3, "hired_at": date(2022, 10, 22)},
]

DEMO_VEHICLES = [
    {"plate_no": "沪A·D1001", "brand": "比亚迪", "model": "秦 PLUS EV", "color": "白色", "status": "idle", "seat_count": 5, "driver_phone": "13800001001", "registered_at": date(2023, 3, 1)},
    {"plate_no": "沪A·D1002", "brand": "广汽埃安", "model": "AION S", "color": "银色", "status": "running", "seat_count": 5, "driver_phone": "13800001002", "registered_at": date(2023, 5, 10)},
    {"plate_no": "沪A·D1003", "brand": "上汽荣威", "model": "Ei5", "color": "蓝色", "status": "idle", "seat_count": 5, "driver_phone": "13800001003", "registered_at": date(2023, 7, 18)},
    {"plate_no": "沪A·D1004", "brand": "特斯拉", "model": "Model 3", "color": "黑色", "status": "repair", "seat_count": 5, "driver_phone": "13800001004", "registered_at": date(2022, 12, 2)},
    {"plate_no": "沪A·D1005", "brand": "比亚迪", "model": "海豹", "color": "灰色", "status": "running", "seat_count": 5, "driver_phone": "13800001005", "registered_at": date(2024, 2, 8)},
    {"plate_no": "沪A·D1006", "brand": "小鹏", "model": "P7", "color": "白色", "status": "idle", "seat_count": 5, "driver_phone": "13800001006", "registered_at": date(2024, 4, 16)},
    {"plate_no": "沪A·D1007", "brand": "大众", "model": "ID.4", "color": "红色", "status": "disabled", "seat_count": 5, "driver_phone": None, "registered_at": date(2022, 9, 9)},
    {"plate_no": "沪A·D1008", "brand": "理想", "model": "L6", "color": "绿色", "status": "running", "seat_count": 5, "driver_phone": "13800001008", "registered_at": date(2024, 6, 21)},
    {"plate_no": "沪A·D1009", "brand": "蔚来", "model": "ET5", "color": "蓝色", "status": "idle", "seat_count": 5, "driver_phone": "13800001009", "registered_at": date(2024, 8, 5)},
    {"plate_no": "沪A·D1010", "brand": "吉利", "model": "几何 A", "color": "白色", "status": "repair", "seat_count": 5, "driver_phone": "13800001010", "registered_at": date(2023, 11, 11)},
]


def seed_demo_users(db: Session) -> int:
    created = 0
    for item in DEMO_USERS:
        if db.scalar(select(User).where(User.username == item["username"])):
            continue
        role = db.scalar(select(Role).where(Role.code == item["role_code"]))
        user = User(
            username=item["username"],
            password_hash=hash_password(item["password"]),
            name=item["name"],
            status="enabled",
        )
        if role:
            user.roles = [role]
        db.add(user)
        created += 1
    return created


def seed_demo_drivers(db: Session) -> int:
    created = 0
    for item in DEMO_DRIVERS:
        if db.scalar(select(Driver).where(Driver.phone == item["phone"])):
            continue
        db.add(Driver(**item))
        created += 1
    return created


def seed_demo_vehicles(db: Session) -> int:
    created = 0
    for item in DEMO_VEHICLES:
        if db.scalar(select(Vehicle).where(Vehicle.plate_no == item["plate_no"])):
            continue
        driver = None
        if item["driver_phone"]:
            driver = db.scalar(select(Driver).where(Driver.phone == item["driver_phone"]))
        payload = {key: value for key, value in item.items() if key != "driver_phone"}
        payload["driver_id"] = driver.id if driver else None
        db.add(Vehicle(**payload))
        created += 1
    return created


def seed_fake_data() -> dict[str, int]:
    init_db()
    with SessionLocal() as db:
        users = seed_demo_users(db)
        drivers = seed_demo_drivers(db)
        db.flush()
        vehicles = seed_demo_vehicles(db)
        db.commit()
        return {"users": users, "drivers": drivers, "vehicles": vehicles}


if __name__ == "__main__":
    result = seed_fake_data()
    print(f"created users={result['users']} drivers={result['drivers']} vehicles={result['vehicles']}")
