from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.connection import get_db
from ...database.models import JobAnalysis
from ...schemas.models import JobAnalysisCreate, JobAnalysisResponse
from ...agents.job_analyzer import JobAnalyzerAgent
from ..dependencies import get_current_user
from sqlalchemy.future import select

router = APIRouter()


@router.post("/analyze", response_model=JobAnalysisResponse)
async def analyze_job_posting(
    job_data: JobAnalysisCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a job posting and extract structured requirements."""
    
    # Initialize job analyzer agent
    analyzer = JobAnalyzerAgent()
    
    try:
        # Analyze the job posting
        analysis_result = await analyzer.analyze_job_posting(
            job_url=job_data.job_url,
            job_text=job_data.job_text
        )
        
        # Extract basic job info
        job_title = job_data.job_title or analysis_result.get('job_title', 'Unknown Position')
        company_name = job_data.company_name or analysis_result.get('company_name', 'Unknown Company')
        
        # Store analysis in database
        job_analysis = JobAnalysis(
            user_id=current_user.id,
            job_url=job_data.job_url,
            job_title=job_title,
            company_name=company_name,
            analysis_data=analysis_result
        )
        
        db.add(job_analysis)
        await db.commit()
        await db.refresh(job_analysis)
        
        return job_analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to analyze job posting: {str(e)}"
        )


@router.get("/history", response_model=List[JobAnalysisResponse])
async def get_job_analysis_history(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get user's job analysis history."""
    
    result = await db.execute(
        select(JobAnalysis)
        .where(JobAnalysis.user_id == current_user.id)
        .order_by(JobAnalysis.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    
    analyses = result.scalars().all()
    return analyses


@router.get("/{analysis_id}", response_model=JobAnalysisResponse)
async def get_job_analysis(
    analysis_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific job analysis by ID."""
    
    result = await db.execute(
        select(JobAnalysis)
        .where(JobAnalysis.id == analysis_id)
        .where(JobAnalysis.user_id == current_user.id)
    )
    
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    return analysis


@router.delete("/{analysis_id}")
async def delete_job_analysis(
    analysis_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a job analysis."""
    
    result = await db.execute(
        select(JobAnalysis)
        .where(JobAnalysis.id == analysis_id)
        .where(JobAnalysis.user_id == current_user.id)
    )
    
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    await db.delete(analysis)
    await db.commit()
    
    return {"message": "Job analysis deleted successfully"}


@router.get("/{analysis_id}/keywords")
async def get_ats_keywords(
    analysis_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get ATS-optimized keywords for a specific job analysis."""
    
    # Get job analysis
    result = await db.execute(
        select(JobAnalysis)
        .where(JobAnalysis.id == analysis_id)
        .where(JobAnalysis.user_id == current_user.id)
    )
    
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )
    
    # Extract keywords using analyzer
    analyzer = JobAnalyzerAgent()
    
    try:
        keywords = await analyzer.extract_keywords_for_ats(analysis.analysis_data)
        return {
            "job_title": analysis.job_title,
            "company_name": analysis.company_name,
            "keywords": keywords
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract keywords: {str(e)}"
        )