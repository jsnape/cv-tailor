from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, validator


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# Profile Schemas
class PersonalInfo(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    github: Optional[str] = None


class WorkExperience(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: Optional[str] = None
    description: str
    achievements: List[str] = []
    technologies: List[str] = []


class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_date: str
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    achievements: List[str] = []


class Project(BaseModel):
    name: str
    description: str
    technologies: List[str] = []
    url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Certification(BaseModel):
    name: str
    issuer: str
    date_obtained: str
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None


class UserProfileData(BaseModel):
    personal_info: PersonalInfo = PersonalInfo()
    professional_summary: str = ""
    technical_skills: Dict[str, List[str]] = {}
    soft_skills: List[str] = []
    work_experience: List[WorkExperience] = []
    education: List[Education] = []
    projects: List[Project] = []
    certifications: List[Certification] = []
    languages: List[str] = []


class UserProfileCreate(BaseModel):
    profile_data: UserProfileData


class UserProfileUpdate(BaseModel):
    profile_data: UserProfileData


class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    profile_data: UserProfileData
    version: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True


# Job Analysis Schemas
class JobAnalysisCreate(BaseModel):
    job_url: Optional[str] = None
    job_text: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None


class RequiredSkills(BaseModel):
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    experience_years: Optional[int] = None
    education_requirements: List[str] = []


class CompanyCulture(BaseModel):
    values: List[str] = []
    work_environment: str = ""
    team_structure: str = ""


class JobAnalysisData(BaseModel):
    job_title: str
    company_name: str
    required_skills: RequiredSkills
    responsibilities: List[str] = []
    qualifications: List[str] = []
    company_culture: CompanyCulture = CompanyCulture()
    keywords: List[str] = []
    salary_range: Optional[str] = None
    location: Optional[str] = None
    remote_option: Optional[str] = None


class JobAnalysisResponse(BaseModel):
    id: int
    user_id: int
    job_url: Optional[str]
    job_title: Optional[str]
    company_name: Optional[str]
    analysis_data: JobAnalysisData
    created_at: datetime
    
    class Config:
        orm_mode = True


# Content Generation Schemas
class ContentGenerateRequest(BaseModel):
    job_analysis_id: int
    content_type: str  # 'cv', 'bio', 'cover_letter'
    format: str = "markdown"  # 'markdown', 'pdf', 'docx'
    style: Optional[str] = "professional"
    template: Optional[str] = "modern"
    additional_instructions: Optional[str] = None


class ContentResponse(BaseModel):
    id: int
    user_id: int
    job_analysis_id: Optional[int]
    content_type: str
    content: str
    format: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        orm_mode = True