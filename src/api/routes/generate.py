from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import io
import json

from ...database.connection import get_db
from ...database.models import JobAnalysis, UserProfile, GeneratedContent
from ...schemas.models import ContentGenerateRequest, ContentResponse
from ...agents.cv_tailor import CVTailorAgent
from ...agents.bio_generator import BioGeneratorAgent
from ..dependencies import get_current_user

router = APIRouter()


@router.post("/cv", response_model=ContentResponse)
async def generate_tailored_cv(
    request: ContentGenerateRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a tailored CV based on job analysis and user profile."""
    
    # Get job analysis
    job_result = await db.execute(
        select(JobAnalysis)
        .where(JobAnalysis.id == request.job_analysis_id)
        .where(JobAnalysis.user_id == current_user.id)
    )
    job_analysis = job_result.scalar_one_or_none()
    
    if not job_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    # Get user profile
    profile_result = await db.execute(
        select(UserProfile)
        .where(UserProfile.user_id == current_user.id)
        .where(UserProfile.is_active == True)
    )
    user_profile = profile_result.scalar_one_or_none()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please create a profile first."
        )
    
    # Generate CV using AI agent
    cv_agent = CVTailorAgent()
    
    try:
        cv_content = await cv_agent.generate_tailored_cv(
            user_profile=user_profile.profile_data,
            job_analysis=job_analysis.analysis_data,
            style=request.style or "professional",
            format_type=request.template or "ats_optimized"
        )
        
        # Store generated content
        generated_content = GeneratedContent(
            user_id=current_user.id,
            job_analysis_id=request.job_analysis_id,
            content_type="cv",
            content=cv_content,
            format=request.format,
            metadata={
                "style": request.style,
                "template": request.template,
                "additional_instructions": request.additional_instructions
            }
        )
        
        db.add(generated_content)
        await db.commit()
        await db.refresh(generated_content)
        
        return generated_content
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CV: {str(e)}"
        )


@router.post("/bio", response_model=ContentResponse)
async def generate_professional_bio(
    request: ContentGenerateRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    length: str = "medium",
    bio_style: str = "professional",
    context: str = "presentation"
):
    """Generate a professional bio for presentations or profiles."""
    
    # Get user profile
    profile_result = await db.execute(
        select(UserProfile)
        .where(UserProfile.user_id == current_user.id)
        .where(UserProfile.is_active == True)
    )
    user_profile = profile_result.scalar_one_or_none()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please create a profile first."
        )
    
    # Get job context if provided
    job_context = None
    if request.job_analysis_id:
        job_result = await db.execute(
            select(JobAnalysis)
            .where(JobAnalysis.id == request.job_analysis_id)
            .where(JobAnalysis.user_id == current_user.id)
        )
        job_analysis = job_result.scalar_one_or_none()
        if job_analysis:
            job_context = job_analysis.analysis_data
    
    # Generate bio using AI agent
    bio_agent = BioGeneratorAgent()
    
    try:
        if context == "presentation":
            bio_content = await bio_agent.generate_presentation_bio(
                user_profile=user_profile.profile_data,
                presentation_topic=request.additional_instructions,
                audience="professional"
            )
        elif context == "linkedin":
            bio_content = await bio_agent.generate_linkedin_summary(
                user_profile=user_profile.profile_data
            )
        elif context == "executive":
            bio_content = await bio_agent.generate_executive_summary(
                user_profile=user_profile.profile_data,
                executive_level="senior"
            )
        elif context == "elevator":
            bio_content = await bio_agent.generate_elevator_pitch(
                user_profile=user_profile.profile_data
            )
        else:
            bio_content = await bio_agent.generate_professional_bio(
                user_profile=user_profile.profile_data,
                job_context=job_context,
                length=length,
                style=bio_style,
                context=context
            )
        
        # Store generated content
        generated_content = GeneratedContent(
            user_id=current_user.id,
            job_analysis_id=request.job_analysis_id,
            content_type="bio",
            content=bio_content,
            format=request.format,
            metadata={
                "length": length,
                "style": bio_style,
                "context": context,
                "additional_instructions": request.additional_instructions
            }
        )
        
        db.add(generated_content)
        await db.commit()
        await db.refresh(generated_content)
        
        return generated_content
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate bio: {str(e)}"
        )


@router.get("/history", response_model=List[ContentResponse])
async def get_generation_history(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    content_type: str = None,
    limit: int = 50,
    offset: int = 0
):
    """Get user's content generation history."""
    
    query = select(GeneratedContent).where(GeneratedContent.user_id == current_user.id)
    
    if content_type:
        query = query.where(GeneratedContent.content_type == content_type)
    
    query = query.order_by(GeneratedContent.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    content_list = result.scalars().all()
    
    return content_list


@router.get("/{content_id}", response_model=ContentResponse)
async def get_generated_content(
    content_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific generated content by ID."""
    
    result = await db.execute(
        select(GeneratedContent)
        .where(GeneratedContent.id == content_id)
        .where(GeneratedContent.user_id == current_user.id)
    )
    
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated content not found"
        )
    
    return content


@router.get("/{content_id}/export")
async def export_content(
    content_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    export_format: str = "markdown"
):
    """Export generated content in various formats."""
    
    # Get content
    result = await db.execute(
        select(GeneratedContent)
        .where(GeneratedContent.id == content_id)
        .where(GeneratedContent.user_id == current_user.id)
    )
    
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated content not found"
        )
    
    # Determine filename
    filename = f"{content.content_type}_{content_id}"
    
    if export_format == "markdown" or export_format == "md":
        return Response(
            content=content.content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.md"
            }
        )
    
    elif export_format == "txt":
        # Strip markdown formatting for plain text
        import re
        plain_text = re.sub(r'[*_#`]', '', content.content)
        return Response(
            content=plain_text,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.txt"
            }
        )
    
    elif export_format == "json":
        export_data = {
            "id": content.id,
            "content_type": content.content_type,
            "content": content.content,
            "format": content.format,
            "metadata": content.metadata,
            "created_at": content.created_at.isoformat()
        }
        return Response(
            content=json.dumps(export_data, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.json"
            }
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported export format. Use 'markdown', 'txt', or 'json'"
        )


@router.delete("/{content_id}")
async def delete_generated_content(
    content_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete generated content."""
    
    result = await db.execute(
        select(GeneratedContent)
        .where(GeneratedContent.id == content_id)
        .where(GeneratedContent.user_id == current_user.id)
    )
    
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated content not found"
        )
    
    await db.delete(content)
    await db.commit()
    
    return {"message": "Generated content deleted successfully"}