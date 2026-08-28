from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_permission
from app.db.models import User, Vehicle
from app.db.session import get_db
from app.models.schemas import VehicleCreate, VehicleUpdate

router = APIRouter()


def serialize_vehicle(vehicle: Vehicle) -> dict[str, object]:
    return {
        "id": vehicle.id,
        "plate_no": vehicle.plate_no,
        "brand": vehicle.brand,
        "model": vehicle.model,
        "color": vehicle.color,
        "status": vehicle.status,
        "seat_count": vehicle.seat_count,
        "driver_id": vehicle.driver_id,
        "driver_name": vehicle.driver.name if vehicle.driver else None,
        "registered_at": vehicle.registered_at.isoformat() if vehicle.registered_at else None,
        "created_at": vehicle.created_at.isoformat(),
        "updated_at": vehicle.updated_at.isoformat(),
    }


@router.get("/vehicles")
def list_vehicles(
    keyword: str | None = None,
    status: str | None = None,
    driver_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    statement = select(Vehicle)
    if keyword:
        like = f"%{keyword}%"
        statement = statement.where((Vehicle.plate_no.like(like)) | (Vehicle.brand.like(like)) | (Vehicle.model.like(like)))
    if status:
        statement = statement.where(Vehicle.status == status)
    if driver_id:
        statement = statement.where(Vehicle.driver_id == driver_id)
    all_items = list(db.scalars(statement.order_by(Vehicle.created_at.desc())))
    start = (page - 1) * page_size
    return {"items": [serialize_vehicle(item) for item in all_items[start:start + page_size]], "total": len(all_items)}


@router.get("/vehicles/{vehicle_id}")
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return serialize_vehicle(vehicle)


@router.post("/vehicles")
def create_vehicle(
    request: VehicleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("vehicle:create")),
):
    vehicle = Vehicle(**request.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return serialize_vehicle(vehicle)


@router.put("/vehicles/{vehicle_id}")
def update_vehicle(
    vehicle_id: str,
    request: VehicleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("vehicle:update")),
):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    for key, value in request.model_dump().items():
        setattr(vehicle, key, value)
    db.commit()
    db.refresh(vehicle)
    return serialize_vehicle(vehicle)


@router.delete("/vehicles/{vehicle_id}")
def delete_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("vehicle:delete")),
):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(vehicle)
    db.commit()
    return {"success": True}
