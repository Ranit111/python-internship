"""
Pydantic validation schemas for Items/Tasks CRUD operations.
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Resource title")
    description: Optional[str] = Field(None, description="Detailed resource content or notes")
    status: str = Field(default="PENDING", pattern="^(PENDING|IN_PROGRESS|COMPLETED|ARCHIVED)$")
    priority: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH|URGENT)$")


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(PENDING|IN_PROGRESS|COMPLETED|ARCHIVED)$")
    priority: Optional[str] = Field(None, pattern="^(LOW|MEDIUM|HIGH|URGENT)$")


class ItemResponse(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime


class ItemListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ItemResponse]
