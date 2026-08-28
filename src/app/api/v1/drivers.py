from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_permission
from app.db.models import Driver, User
from app.db.session import get_db
from app.models.schemas import DriverCreate, DriverUpdate

router = APIRouter()


def serialize_driver(driver: Driver) -> dict[str, object]:
    return {
        "id": driver.id,
        "name": driver.name,
        "phone": driver.phone,
        "id_card": driver.id_card,
        "license_no": driver.license_no,
        "status": driver.status,
        "rating": driver.rating,
        "hired_at": driver.hired_at.isoformat() if driver.hired_at else None,
        "created_at": driver.created_at.isoformat(),
        "updated_at": driver.updated_at.isoformat(),
    }


@router.get("/drivers")
def list_drivers(
    keyword: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    statement = select(Driver)
    if keyword:
        like = f"%{keyword}%"
        statement = statement.where((Driver.name.like(like)) | (Driver.phone.like(like)))
    if status:
        statement = statement.where(Driver.status == status)
    all_items = list(db.scalars(statement.order_by(Driver.created_at.desc())))
    start = (page - 1) * page_size
    return {"items": [serialize_driver(item) for item in all_items[start:start + page_size]], "total": len(all_items)}


@router.get("/drivers/{driver_id}")
def get_driver(driver_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return serialize_driver(driver)


@router.post("/drivers")
def create_driver(
    request: DriverCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("driver:create")),
):
    driver = Driver(**request.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return serialize_driver(driver)


@router.put("/drivers/{driver_id}")
def update_driver(
    driver_id: str,
    request: DriverUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("driver:update")),
):
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    for key, value in request.model_dump().items():
        setattr(driver, key, value)
    db.commit()
    db.refresh(driver)
    return serialize_driver(driver)


@router.delete("/drivers/{driver_id}")
def delete_driver(
    driver_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("driver:delete")),
):
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    db.delete(driver)
    db.commit()
    return {"success": True}
