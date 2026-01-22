from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

from src.database import get_session
from src.models import Shop, ShopSite
from src.security import get_current_admin_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin_user)],
)

# --- Pydantic Schemas for Request/Response ---

class ShopResponse(BaseModel):
    shop_id: str
    owner_uid: str
    name: str
    tier: str
    line_config: Optional[Dict[str, Any]] = None
    ai_settings: Optional[Dict[str, Any]] = None
    # We can add a computed field to check connection status easily if needed
    
class IntegrationUpdate(BaseModel):
    channelSecret: str
    channelAccessToken: str
    botBasicId: str

class TierUpdate(BaseModel):
    tier: str

# --- Endpoints ---

@router.get("/shops", response_model=List[ShopResponse])
async def list_shops(
    offset: int = 0,
    limit: int = Query(default=20, le=100),
    session: AsyncSession = Depends(get_session)
):
    """
    List all shops with pagination.
    """
    query = select(Shop).offset(offset).limit(limit)
    result = await session.execute(query)
    shops = result.scalars().all()
    return shops

@router.get("/shops/{shop_id}", response_model=ShopResponse)
async def get_shop(
    shop_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get specific shop details.
    """
    shop = await session.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop

@router.patch("/shops/{shop_id}/integration", response_model=ShopResponse)
async def update_shop_integration(
    shop_id: str,
    integration_data: IntegrationUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update shop's LINE integration configuration.
    Updates or initializes the 'line_config' JSON field.
    """
    shop = await session.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Initialize dictionary if None
    current_config = shop.line_config or {}
    
    # Update with new values
    current_config["channelSecret"] = integration_data.channelSecret
    current_config["channelAccessToken"] = integration_data.channelAccessToken
    current_config["botBasicId"] = integration_data.botBasicId
    
    shop.line_config = current_config
    session.add(shop)
    await session.commit()
    await session.refresh(shop)
    return shop

@router.patch("/shops/{shop_id}/tier", response_model=ShopResponse)
async def update_shop_tier(
    shop_id: str,
    tier_data: TierUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update shop's package tier.
    """
    shop = await session.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    shop.tier = tier_data.tier
    session.add(shop)
    await session.commit()
    await session.refresh(shop)
    return shop
