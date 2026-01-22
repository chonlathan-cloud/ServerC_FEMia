from sqlmodel import SQLModel, Field, Column, JSON
from pgvector.sqlalchemy import Vector
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

class Shop(SQLModel, table=True):
    __tablename__ = "shops"
    
    shop_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    owner_uid: str = Field(index=True)
    name: str
    tier: str = Field(default="free")
    line_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    ai_settings: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ShopSite(SQLModel, table=True):
    __tablename__ = "shop_sites"
    site_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    shop_id: str = Field(foreign_key="shops.shop_id", index=True)
    config_json: Dict[str, Any] = Field(sa_column=Column(JSON))
    status: str = Field(default="draft")
    slug: Optional[str] = Field(default=None, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
