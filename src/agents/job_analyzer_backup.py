from typing import Dict, Any, List
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI
from bs4 import BeautifulSoup
import aiohttp
import re
from ..utils.config import settings


class JobAnalyzerAgent:
    """AI agent for analyzing job postings and extracting requirements."""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(
            base_url="https://models.github.ai/inference",
            api_key=settings.github_token,
        )
        self.chat_client = OpenAIChatClient(
            async_client=self.openai_client,
            model_id=settings.default_model_id
        )
        self.agent = ChatAgent(
            chat_client=self.chat_client,
            name="JobAnalyzer",
            instructions=self._get_system_instructions(),
        )
    
    def _get_system_instructions(self) -> str:
        return """
        You are an expert job posting analyzer. Your task is to extract structured information from job postings.
        
        Analyze the job posting and extract:
        1. Job title and company name
        2. Required technical skills (programming languages, frameworks, tools)
        3. Required soft skills (communication, leadership, etc.)
        4. Experience requirements (years, specific experience)
        5. Education requirements
        6. Key responsibilities
        7. Company culture indicators
        8. Important keywords for ATS optimization
        
        Return your analysis as a structured JSON object with clear categories.
        Be thorough but concise. Focus on actionable requirements that can be matched against a candidate's profile.
        """
    
    async def fetch_job_content(self, url: str) -> str:
        """Fetch job posting content from URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get text and clean up
                        text = soup.get_text()
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = ' '.join(chunk for chunk in chunks if chunk)
                        
                        return text
                    else:
                        raise Exception(f"Failed to fetch URL: HTTP {response.status}")
        except Exception as e:
            raise Exception(f"Error fetching job posting: {str(e)}")
    
    def _clean_job_text(self, text: str) -> str:
        """Clean and prepare job text for analysis."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Extract key information from the beginning (company, job title)
        header_info = \"\"
        company_match = re.search(r'Microsoft.*?hiring\\s+(.*?)\\s+in\\s+(.*?)\\s+\\|', text, re.IGNORECASE)
        if company_match:
            header_info = f\"Company: Microsoft\\nJob Title: {company_match.group(1)}\\nLocation: {company_match.group(2)}\\n\\n\"
        
        # LinkedIn-specific cleaning - find the actual job content
        # Look for job description patterns
        job_start_patterns = [
            r'Overview.*?About The Role',
            r'About The Role',
            r'In this role you will',
            r'Required experience',
            r'Qualifications',
            r'We are looking for',
            r'Job Description',
        ]
        
        job_content = text
        for pattern in job_start_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                job_content = text[match.start():]
                break
        
        # Remove common noise and LinkedIn-specific clutter
        noise_patterns = [
            r'Apply now.*?$',
            r'Share this job.*?$',
            r'Cookie policy.*?$',
            r'Privacy policy.*?$',
            r'Sign in.*?Sign in',
            r'Join to apply.*?Join now',
            r'LinkedIn.*?User Agreement.*?Cookie Policy',
            r'Similar jobs.*$',
            r'People also viewed.*$',
            r'Show more.*Show less.*$',
        ]
        
        for pattern in noise_patterns:
            job_content = re.sub(pattern, '', job_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Combine header info with job content
        final_content = header_info + job_content.strip()
        return final_content
    
    async def analyze_job_posting(self, job_url: str = None, job_text: str = None) -> Dict[str, Any]:
        """Analyze a job posting and extract structured requirements."""
        
        # Get job content
        if job_url:
            content = await self.fetch_job_content(job_url)
        elif job_text:
            content = job_text
        else:
            raise ValueError("Either job_url or job_text must be provided")
        
        # Clean the content
        content = self._clean_job_text(content)
        
        # Prepare analysis prompt with more content
        analysis_prompt = f"""
        Analyze this job posting and extract structured information:

        JOB POSTING:
        {content[:8000]}  # Increased content limit for better analysis
        
        Please provide a detailed analysis in this exact JSON format:
        {{
            "job_title": "exact job title",
            "company_name": "company name",
            "required_skills": {{
                "technical_skills": ["skill1", "skill2", ...],
                "soft_skills": ["skill1", "skill2", ...],
                "experience_years": number or null,
                "education_requirements": ["requirement1", ...]
            }},
            "responsibilities": ["responsibility1", "responsibility2", ...],
            "qualifications": ["qualification1", "qualification2", ...],
            "company_culture": {{
                "values": ["value1", "value2", ...],
                "work_environment": "description",
                "team_structure": "description"
            }},
            "keywords": ["keyword1", "keyword2", ...],
            "salary_range": "range or null",
            "location": "location or null",
            "remote_option": "remote/hybrid/onsite or null"
        }}
        
        Be comprehensive but precise. Extract only information that's explicitly mentioned or clearly implied.
        """
        
        # Get analysis from agent
        result = await self.agent.run(analysis_prompt)
        
        # Parse the JSON response
        try:
            import json
            # Extract JSON from the response (in case there's extra text)
            json_start = result.text.find('{')
            json_end = result.text.rfind('}') + 1
            json_str = result.text[json_start:json_end]
            
            analysis_data = json.loads(json_str)
            return analysis_data
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: return raw analysis if JSON parsing fails
            return {
                "raw_analysis": result.text,
                "error": f"Failed to parse structured analysis: {str(e)}"
            }
    
    async def extract_keywords_for_ats(self, job_analysis: Dict[str, Any]) -> List[str]:
        """Extract keywords optimized for ATS (Applicant Tracking Systems)."""
        
        keywords_prompt = f"""
        Based on this job analysis, generate a list of ATS-optimized keywords that a candidate should include in their CV:
        
        Job Analysis:
        {job_analysis}
        
        Generate 15-25 keywords that are:
        1. Directly mentioned in the job posting
        2. Important for ATS scanning
        3. Relevant to the role
        4. Include both technical and soft skills
        5. Include industry-specific terms
        
        Return as a simple comma-separated list.
        """
        
        result = await self.agent.run(keywords_prompt)
        
        # Parse keywords
        keywords_text = result.text.strip()
        keywords = [kw.strip() for kw in keywords_text.split(',')]
        
        return keywords[:25]  # Limit to 25 keywords