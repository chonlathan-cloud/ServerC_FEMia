import httpx  # <--- 1. อย่าลืมบรรทัดนี้!
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict

from src.database import get_session
from src.models import Shop, ShopSite
from src.security import get_current_admin_user
from src.config import settings

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin_user)],
)

# --- Pydantic Schemas ---

class ShopResponse(BaseModel):
    shop_id: str
    owner_uid: str
    name: str
    tier: str
    line_config: Optional[Dict[str, Any]] = None
    ai_settings: Optional[Dict[str, Any]] = None
    public_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
    
class IntegrationUpdate(BaseModel):
    channelSecret: str
    channelAccessToken: str
    botBasicId: Optional[str] = None  # เป็น Optional เพื่อให้ Auto-detect ได้
    displayName: Optional[str] = None 

class TierUpdate(BaseModel):
    tier: str
    
class ShopCreate(BaseModel):
    name: str
    owner_uid: str

# --- Helpers ---

def _build_public_url(shop_id: str) -> str:
    base = settings.public_site_base_url.rstrip("/")
    return f"{base}/{shop_id}"

def _serialize_shop(shop: Shop) -> Dict[str, Any]:
    data = ShopResponse.model_validate(shop).model_dump()
    data["public_url"] = _build_public_url(shop.shop_id)
    return data

# --- Endpoints ---

@router.get("/shops", response_model=List[ShopResponse])
async def list_shops(
    offset: int = 0,
    limit: int = Query(default=20, le=100),
    session: AsyncSession = Depends(get_session)
):
    query = select(Shop).offset(offset).limit(limit)
    result = await session.execute(query)
    shops = result.scalars().all()
    return [_serialize_shop(shop) for shop in shops]

@router.get("/shops/{shop_id}", response_model=ShopResponse)
async def get_shop(
    shop_id: str,
    session: AsyncSession = Depends(get_session)
):
    shop = await session.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return _serialize_shop(shop)

@router.post("/shops", response_model=ShopResponse)
async def create_shop(
    shop_data: ShopCreate,
    session: AsyncSession = Depends(get_session)
):
    new_shop = Shop(
        name=shop_data.name,
        owner_uid=shop_data.owner_uid,
        tier="Free"
    )
    session.add(new_shop)
    await session.commit()
    await session.refresh(new_shop)
    return _serialize_shop(new_shop)

@router.patch("/shops/{shop_id}/integration", response_model=ShopResponse)
async def update_shop_integration(
    shop_id: str,
    integration_data: IntegrationUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update shop's LINE integration.
    Auto-fetches Bot ID from LINE API using the Access Token.
    """
    shop = await session.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    current_config = dict(shop.line_config) if shop.line_config else {}
    
    # --- 🤖 ส่วนสำคัญ: Auto-detect Bot Info ---
    fetched_bot_id = integration_data.botBasicId
    fetched_display_name = integration_data.displayName
    fetched_picture_url = current_config.get("pictureUrl")

    if integration_data.channelAccessToken:
        try:
            print("Fetching bot info from LINE API...")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.line.me/v2/bot/info",
                    headers={"Authorization": f"Bearer {integration_data.channelAccessToken}"}
                )
                
                if response.status_code == 200:
                    bot_info = response.json()
                    print(f"Bot info fetched: {bot_info}")
                    
                    # userId -> ใช้เป็น botBasicId สำหรับ Webhook (ขึ้นต้นด้วย U...)
                    fetched_bot_id = bot_info.get("userId")
                    fetched_display_name = bot_info.get("displayName")
                    fetched_picture_url = bot_info.get("pictureUrl")
                    
                    # basicId -> เก็บไว้โชว์ (@...)
                    current_config["basicId"] = bot_info.get("basicId")
                else:
                    print(f"Warning: Failed to fetch bot info. Status: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error fetching LINE bot info: {e}")
    # ------------------------------------------

    # Update Values
    current_config["channelSecret"] = integration_data.channelSecret
    current_config["channelAccessToken"] = integration_data.channelAccessToken
    
    # บันทึกค่าที่ดึงมาได้ (หรือค่าเดิมถ้าดึงไม่ได้)
    if fetched_bot_id:
        current_config["botBasicId"] = fetched_bot_id
    if fetched_display_name:
        current_config["displayName"] = fetched_display_name
    if fetched_picture_url:
        current_config["pictureUrl"] = fetched_picture_url

    shop.line_config = current_config
    session.add(shop)
    await session.commit()
    await session.refresh(shop)
    return _serialize_shop(shop)

@router.patch("/shops/{shop_id}/tier", response_model=ShopResponse)
async def update_shop_tier(
    shop_id: str,
    tier_data: TierUpdate,
    session: AsyncSession = Depends(get_session)
):
    shop = await session.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    shop.tier = tier_data.tier
    session.add(shop)
    await session.commit()
    await session.refresh(shop)
    return _serialize_shop(shop)
