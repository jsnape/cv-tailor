"""
Helper utilities for the CV Tailor application.
"""
import re
from typing import Dict, List, Any
from datetime import datetime
import markdown
from io import StringIO


def clean_text(text: str) -> str:
    """Clean and normalize text input."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common HTML entities
    html_entities = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&mdash;': '—',
        '&ndash;': '–'
    }
    
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)
    
    return text


def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    if not url:
        return ""
    
    # Remove protocol
    domain = re.sub(r'^https?://', '', url)
    # Remove www
    domain = re.sub(r'^www\.', '', domain)
    # Remove path
    domain = domain.split('/')[0]
    
    return domain


def format_date_range(start_date: str, end_date: str = None) -> str:
    """Format date range for display."""
    if not start_date:
        return ""
    
    # Try to parse and format dates
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        start_str = start.strftime("%B %Y")
        
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            end_str = end.strftime("%B %Y")
            return f"{start_str} - {end_str}"
        else:
            return f"{start_str} - Present"
    except ValueError:
        # If parsing fails, return as-is
        if end_date:
            return f"{start_date} - {end_date}"
        else:
            return f"{start_date} - Present"


def calculate_experience_years(work_experience: List[Dict]) -> float:
    """Calculate total years of experience from work history."""
    total_months = 0
    
    for job in work_experience:
        start_date = job.get('start_date')
        end_date = job.get('end_date')
        
        if not start_date:
            continue
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d")
            else:
                end = datetime.now()
            
            # Calculate months
            months = (end.year - start.year) * 12 + (end.month - start.month)
            total_months += months
            
        except ValueError:
            # Skip if date parsing fails
            continue
    
    return round(total_months / 12, 1)


def extract_skills_from_text(text: str, known_skills: List[str] = None) -> List[str]:
    """Extract potential skills from text using pattern matching."""
    if not text or not known_skills:
        return []
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in known_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicates


def markdown_to_plain_text(markdown_text: str) -> str:
    """Convert markdown to plain text."""
    if not markdown_text:
        return ""
    
    # Convert markdown to HTML first
    html = markdown.markdown(markdown_text)
    
    # Remove HTML tags
    clean_text_content = re.sub(r'<[^>]+>', '', html)
    
    # Clean up extra whitespace
    clean_text_content = re.sub(r'\s+', ' ', clean_text_content.strip())
    
    return clean_text_content


def truncate_text(text: str, max_length: int, add_ellipsis: bool = True) -> str:
    """Truncate text to specified length."""
    if not text or len(text) <= max_length:
        return text
    
    if add_ellipsis and max_length > 3:
        return text[:max_length - 3] + "..."
    else:
        return text[:max_length]


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if it's a reasonable phone number length
    return 10 <= len(digits) <= 15


def validate_url(url: str) -> bool:
    """Validate URL format."""
    if not url:
        return False
    
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def score_skill_match(user_skills: List[str], required_skills: List[str]) -> float:
    """Calculate skill match score between user and job requirements."""
    if not user_skills or not required_skills:
        return 0.0
    
    user_skills_lower = [skill.lower() for skill in user_skills]
    required_skills_lower = [skill.lower() for skill in required_skills]
    
    matched_skills = set(user_skills_lower) & set(required_skills_lower)
    
    return len(matched_skills) / len(required_skills_lower)


def generate_filename(content_type: str, user_id: int, timestamp: datetime = None) -> str:
    """Generate a safe filename for exported content."""
    if timestamp is None:
        timestamp = datetime.now()
    
    date_str = timestamp.strftime("%Y%m%d_%H%M%S")
    return f"{content_type}_user{user_id}_{date_str}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing unsafe characters."""
    # Remove or replace unsafe characters
    safe_filename = re.sub(r'[^\w\s.-]', '_', filename)
    
    # Replace spaces with underscores
    safe_filename = safe_filename.replace(' ', '_')
    
    # Remove multiple consecutive underscores
    safe_filename = re.sub(r'_+', '_', safe_filename)
    
    return safe_filename.strip('_')