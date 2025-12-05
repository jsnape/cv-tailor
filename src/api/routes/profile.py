from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ...database.connection import get_db
from ...database.models import UserProfile
from ...schemas.models import (
    UserProfileCreate, 
    UserProfileUpdate, 
    UserProfileResponse,
    UserProfileData
)
from ..dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=UserProfileResponse)
async def get_user_profile(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's active profile."""
    
    result = await db.execute(
        select(UserProfile)
        .where(UserProfile.user_id == current_user.id)
        .where(UserProfile.is_active == True)
        .order_by(UserProfile.version.desc())
    )
    
    profile = result.scalar_one_or_none()
    
    if not profile:
        # Return empty profile structure if none exists
        empty_profile_data = UserProfileData()
        return {
            "id": 0,
            "user_id": current_user.id,
            "profile_data": empty_profile_data,
            "version": 0,
            "is_active": False,
            "created_at": None
        }
    
    return profile


@router.post("/", response_model=UserProfileResponse)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user profile."""
    
    # Check if user already has an active profile
    result = await db.execute(
        select(UserProfile)
        .where(UserProfile.user_id == current_user.id)
        .where(UserProfile.is_active == True)
    )
    
    existing_profile = result.scalar_one_or_none()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active profile. Use PUT to update."
        )
    
    # Create new profile
    new_profile = UserProfile(
        user_id=current_user.id,
        profile_data=profile_data.profile_data.dict(),
        version=1,
        is_active=True
    )
    
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    
    return new_profile


@router.put("/", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's profile (creates new version)."""
    
    # Get current active profile
    result = await db.execute(
        select(UserProfile)
        .where(UserProfile.user_id == current_user.id)
        .where(UserProfile.is_active == True)
    )
    
    current_profile = result.scalar_one_or_none()
    
    # Deactivate current profile if it exists
    if current_profile:
        current_profile.is_active = False
        next_version = current_profile.version + 1
    else:
        next_version = 1
    
    # Create new profile version
    new_profile = UserProfile(
        user_id=current_user.id,
        profile_data=profile_update.profile_data.dict(),
        version=next_version,
        is_active=True
    )
    
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    
    return new_profile


@router.get("/history", response_model=List[UserProfileResponse])
async def get_profile_history(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10
):
    """Get user's profile version history."""
    
    result = await db.execute(
        select(UserProfile)
        .where(UserProfile.user_id == current_user.id)
        .order_by(UserProfile.version.desc())
        .limit(limit)
    )
    
    profiles = result.scalars().all()
    return profiles


@router.post("/revert/{version}")
async def revert_to_profile_version(
    version: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revert to a specific profile version."""
    
    # Find the target version
    result = await db.execute(
        select(UserProfile)
        .where(UserProfile.user_id == current_user.id)
        .where(UserProfile.version == version)
    )
    
    target_profile = result.scalar_one_or_none()
    
    if not target_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile version {version} not found"
        )
    
    # Deactivate current active profile
    current_result = await db.execute(
        select(UserProfile)
        .where(UserProfile.user_id == current_user.id)
        .where(UserProfile.is_active == True)
    )
    
    current_profile = current_result.scalar_one_or_none()
    if current_profile:
        current_profile.is_active = False
    
    # Create new profile with reverted data
    new_version = (current_profile.version + 1) if current_profile else 1
    
    reverted_profile = UserProfile(
        user_id=current_user.id,
        profile_data=target_profile.profile_data,
        version=new_version,
        is_active=True
    )
    
    db.add(reverted_profile)
    await db.commit()
    await db.refresh(reverted_profile)
    
    return {
        "message": f"Successfully reverted to version {version}",
        "new_version": new_version
    }


@router.post("/import")
async def import_profile_data(
    import_data: dict,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Import profile data from external sources (LinkedIn, resume parsers, etc.)."""
    
    try:
        # Validate and convert import data to profile structure
        # This is a simplified version - in practice, you'd have
        # specific parsers for different data sources
        
        profile_data = UserProfileData(**import_data)
        
        # Create or update profile
        result = await db.execute(
            select(UserProfile)
            .where(UserProfile.user_id == current_user.id)
            .where(UserProfile.is_active == True)
        )
        
        current_profile = result.scalar_one_or_none()
        
        if current_profile:
            current_profile.is_active = False
            next_version = current_profile.version + 1
        else:
            next_version = 1
        
        new_profile = UserProfile(
            user_id=current_user.id,
            profile_data=profile_data.dict(),
            version=next_version,
            is_active=True
        )
        
        db.add(new_profile)
        await db.commit()
        await db.refresh(new_profile)
        
        return {
            "message": "Profile data imported successfully",
            "version": next_version
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to import profile data: {str(e)}"
        )