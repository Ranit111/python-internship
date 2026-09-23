"""
CRUD API endpoints for Items and Resources.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db
from app.db.models import Item, User
from app.schemas.item import ItemCreate, ItemListResponse, ItemResponse, ItemUpdate

router = APIRouter(prefix="/items", tags=["Items & Task Management"])


@router.get("/", response_model=ItemListResponse)
def read_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Page size limit"),
    status: Optional[str] = Query(None, description="Filter items by status"),
    search: Optional[str] = Query(None, description="Search term in title or description"),
) -> Any:
    """
    Retrieves paginated list of items owned by current user with optional filtering and search.
    """
    query = db.query(Item).filter(Item.owner_id == current_user.id)
    if status:
        query = query.filter(Item.status == status.upper())
    if search:
        query = query.filter(
            (Item.title.ilike(f"%{search}%")) | (Item.description.ilike(f"%{search}%"))
        )

    total_count = query.count()
    items = query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total_count,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "items": items,
    }


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Creates a new item resource associated with the authenticated user.
    """
    item = Item(
        title=item_in.title,
        description=item_in.description,
        status=item_in.status,
        priority=item_in.priority,
        owner_id=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemResponse)
def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieves a single item resource by ID (ownership verification enforced).
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")
    return item


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Updates an existing item resource by ID.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this resource")

    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Deletes an item resource by ID.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this resource")

    db.delete(item)
    db.commit()
    return None
