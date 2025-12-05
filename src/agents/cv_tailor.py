from typing import Dict, Any, List
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI
from ..utils.config import settings


class CVTailorAgent:
    """AI agent for generating tailored CVs based on job requirements and user profile."""
    
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
            name="CVTailor",
            instructions=self._get_system_instructions(),
        )
    
    def _get_system_instructions(self) -> str:
        return """
        You are an expert CV writer and career advisor. Your task is to create tailored, professional CVs that:
        
        1. TRUTHFULLY represent the candidate's actual experience
        2. Highlight genuinely relevant experience and skills
        3. Use industry-specific keywords naturally (only where truthful)
        4. Follow professional formatting standards
        5. Tell an authentic career story
        
        CRITICAL Guidelines:
        - NEVER exaggerate, embellish, or fabricate experience
        - Only claim skills and experience explicitly in the candidate's profile
        - Reframe existing experience positively but truthfully
        - Use action verbs for actual accomplishments only
        - Prioritize relevant experience but maintain chronological accuracy
        - Include keywords only when they genuinely match candidate's background
        - Keep content concise, professional, and 100% defensible in interviews
        
        Always provide CV content in clean Markdown format with proper sections and formatting.
        """
    
    async def generate_tailored_cv(
        self, 
        user_profile: Dict[str, Any], 
        job_analysis: Dict[str, Any],
        style: str = "professional",
        format_type: str = "ats_optimized",
        include_gap_analysis: bool = True
    ) -> Dict[str, Any]:
        """Generate a tailored CV based on user profile and job requirements."""
        
        cv_prompt = f"""
        Create a truthful, tailored CV for this job application:

        JOB REQUIREMENTS:
        {job_analysis}

        CANDIDATE PROFILE:
        {user_profile}

        CV REQUIREMENTS:
        - Style: {style}
        - Format: {format_type}
        - Length: 2 pages maximum
        - Include sections: Contact Info, Professional Summary, Experience, Skills, Education, Projects (if relevant)
        - Optimize for ATS scanning while maintaining 100% accuracy
        - ONLY emphasize achievements explicitly stated in candidate profile
        - Use keywords ONLY where they genuinely match candidate's actual experience
        - Quantify accomplishments ONLY using data provided in profile
        - Reframe experience positively but never exaggerate or fabricate
        - Ensure every claim is defensible in an interview setting

        Generate a complete CV in Markdown format. Prioritize authenticity over perceived impact.
        """
        
        result = await self.agent.run(cv_prompt)
        
        response = {
            "cv_content": result.text,
            "gap_analysis": None
        }
        
        if include_gap_analysis:
            response["gap_analysis"] = await self.analyze_profile_gaps(user_profile, job_analysis)
        
        return response
    
    async def generate_professional_summary(
        self, 
        user_profile: Dict[str, Any], 
        job_analysis: Dict[str, Any]
    ) -> str:
        """Generate a targeted professional summary."""
        
        summary_prompt = f"""
        Create a compelling professional summary (3-4 sentences) for this candidate and job:

        JOB: {job_analysis.get('job_title', 'Unknown')} at {job_analysis.get('company_name', 'Unknown')}
        
        KEY REQUIREMENTS:
        - Technical Skills: {job_analysis.get('required_skills', {}).get('technical_skills', [])}
        - Experience: {job_analysis.get('required_skills', {}).get('experience_years', 'Not specified')} years
        - Education: {job_analysis.get('required_skills', {}).get('education_requirements', [])}

        CANDIDATE BACKGROUND:
        - Experience: {user_profile.get('work_experience', [])}
        - Skills: {user_profile.get('technical_skills', {})}
        - Education: {user_profile.get('education', [])}

        Write a summary that:
        1. Highlights years of experience in relevant field
        2. Mentions key technical skills that match requirements
        3. Emphasizes relevant achievements
        4. Shows value proposition for this specific role

        Return only the summary text, no additional formatting.
        """
        
        result = await self.agent.run(summary_prompt)
        return result.text.strip()
    
    async def optimize_experience_section(
        self, 
        work_experience: List[Dict], 
        job_requirements: Dict[str, Any]
    ) -> List[Dict]:
        """Optimize work experience descriptions for the specific job."""
        
        optimized_experience = []
        
        for exp in work_experience:
            optimize_prompt = f"""
            Reframe this work experience entry to align with job requirements while staying 100% truthful:

            JOB REQUIREMENTS:
            {job_requirements}

            ORIGINAL EXPERIENCE:
            Company: {exp.get('company')}
            Position: {exp.get('position')}
            Description: {exp.get('description')}
            Achievements: {exp.get('achievements', [])}

            Reframe to:
            1. Use keywords ONLY where they genuinely apply to the original experience
            2. Highlight aspects of the role that are relevant to job requirements
            3. Use appropriate action verbs for what was actually done
            4. Keep all quantified results exactly as provided (do not invent numbers)
            5. Maintain factual accuracy while emphasizing relevant aspects
            6. NEVER add skills, technologies, or achievements not mentioned in original

            Return as JSON:
            {{
                "description": "truthfully reframed description",
                "achievements": ["original achievement 1", "original achievement 2", ...]
            }}
            """
            
            result = await self.agent.run(optimize_prompt)
            
            try:
                import json
                # Extract JSON from response
                json_start = result.text.find('{')
                json_end = result.text.rfind('}') + 1
                optimized_data = json.loads(result.text[json_start:json_end])
                
                # Update experience with optimized content
                updated_exp = exp.copy()
                updated_exp.update(optimized_data)
                optimized_experience.append(updated_exp)
                
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, keep original
                optimized_experience.append(exp)
        
        return optimized_experience
    
    async def select_relevant_projects(
        self, 
        projects: List[Dict], 
        job_requirements: Dict[str, Any],
        max_projects: int = 3
    ) -> List[Dict]:
        """Select and optimize the most relevant projects for the job."""
        
        if not projects:
            return []
        
        selection_prompt = f"""
        Select the {max_projects} most relevant projects from this list for the job requirements:

        JOB REQUIREMENTS:
        {job_requirements}

        AVAILABLE PROJECTS:
        {projects}

        Criteria:
        1. Technology stack alignment
        2. Project scope and complexity
        3. Relevance to job responsibilities
        4. Demonstrable impact/results

        Return the selected projects as a JSON array, including any improvements to descriptions to better match the job.
        """
        
        result = await self.agent.run(selection_prompt)
        
        try:
            import json
            json_start = result.text.find('[')
            json_end = result.text.rfind(']') + 1
            selected_projects = json.loads(result.text[json_start:json_end])
            return selected_projects[:max_projects]
        except (json.JSONDecodeError, ValueError):
            # Fallback: return first N projects
            return projects[:max_projects]
    
    async def analyze_profile_gaps(
        self,
        user_profile: Dict[str, Any],
        job_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze gaps between job requirements and candidate profile."""
        
        gap_analysis_prompt = f"""
        Analyze the gaps between job requirements and candidate profile. Provide specific feedback on what's missing.

        JOB REQUIREMENTS:
        {job_analysis}

        CANDIDATE PROFILE:
        {user_profile}

        Analyze and identify:
        1. Technical skills mentioned in job requirements but not clearly evident in candidate profile
        2. Experience types/domains required but not well-represented in profile
        3. Specific tools, frameworks, or technologies mentioned in job but missing from profile
        4. Soft skills or leadership qualities required but not demonstrated in profile
        5. Industry certifications or qualifications that would strengthen the application

        For each gap, provide:
        - What's missing
        - Why it matters for this role
        - Specific suggestion on what to add to profile (be very specific about wording/examples)

        Return as JSON:
        {{
            "technical_skills_gaps": [
                {{
                    "missing_skill": "specific skill name",
                    "importance": "why this matters for the role",
                    "suggestion": "specific text/example to add to profile"
                }}
            ],
            "experience_gaps": [
                {{
                    "missing_experience": "type of experience",
                    "importance": "why this matters",
                    "suggestion": "what to add or emphasize in profile"
                }}
            ],
            "certification_gaps": [
                {{
                    "missing_certification": "certification name",
                    "importance": "why this would help",
                    "suggestion": "how to represent this in profile"
                }}
            ],
            "soft_skills_gaps": [
                {{
                    "missing_soft_skill": "soft skill",
                    "importance": "why this matters",
                    "suggestion": "how to demonstrate this in profile"
                }}
            ],
            "overall_strengths": ["strength 1", "strength 2", ...],
            "match_percentage": "estimated percentage match"
        }}
        """
        
        result = await self.agent.run(gap_analysis_prompt)
        
        try:
            import json
            json_start = result.text.find('{')
            json_end = result.text.rfind('}') + 1
            gap_analysis = json.loads(result.text[json_start:json_end])
            return gap_analysis
        except (json.JSONDecodeError, ValueError):
            return {
                "technical_skills_gaps": [],
                "experience_gaps": [],
                "certification_gaps": [],
                "soft_skills_gaps": [],
                "overall_strengths": [],
                "match_percentage": "Unable to analyze"
            }

    async def generate_skills_section(
        self, 
        user_skills: Dict[str, List[str]], 
        job_requirements: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate an optimized skills section that matches job requirements."""
        
        skills_prompt = f"""
        Optimize this skills section for the job requirements:

        JOB REQUIREMENTS:
        {job_requirements}

        CANDIDATE SKILLS:
        {user_skills}

        Create an optimized skills section that:
        1. Prioritizes skills mentioned in job requirements
        2. Groups skills logically (Programming, Frameworks, Tools, etc.)
        3. Orders by relevance to the job
        4. Includes all relevant skills the candidate has

        Return as JSON:
        {{
            "programming_languages": ["lang1", "lang2", ...],
            "frameworks_libraries": ["framework1", ...],
            "tools_technologies": ["tool1", ...],
            "databases": ["db1", ...],
            "cloud_platforms": ["platform1", ...],
            "other": ["skill1", ...]
        }}
        """
        
        result = await self.agent.run(skills_prompt)
        
        try:
            import json
            json_start = result.text.find('{')
            json_end = result.text.rfind('}') + 1
            optimized_skills = json.loads(result.text[json_start:json_end])
            return optimized_skills
        except (json.JSONDecodeError, ValueError):
            # Fallback: return original skills
            return user_skills