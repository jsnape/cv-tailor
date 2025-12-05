from typing import Dict, Any
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI
from ..utils.config import settings


class BioGeneratorAgent:
    """AI agent for generating professional bios for presentations and profiles."""
    
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
            name="BioGenerator",
            instructions=self._get_system_instructions(),
        )
    
    def _get_system_instructions(self) -> str:
        return """
        You are an expert professional bio writer. Your task is to create compelling, concise professional bios that:
        
        1. Capture the person's professional essence
        2. Highlight key achievements and expertise
        3. Match the intended audience and context
        4. Use engaging, professional language
        5. Tell a coherent professional story
        
        Guidelines:
        - Use third person perspective
        - Focus on impact and results
        - Include relevant credentials and experience
        - Tailor tone to the context (conference, LinkedIn, company bio, etc.)
        - Keep within specified length requirements
        - Make it memorable and authentic
        """
    
    async def generate_professional_bio(
        self,
        user_profile: Dict[str, Any],
        job_context: Dict[str, Any] = None,
        length: str = "medium",  # short, medium, long
        style: str = "professional",  # professional, creative, academic
        context: str = "general"  # presentation, linkedin, conference, company
    ) -> str:
        """Generate a professional bio tailored for specific context."""
        
        # Define length guidelines
        length_guidelines = {
            "short": "50-75 words (elevator pitch)",
            "medium": "100-150 words (one paragraph)", 
            "long": "200-300 words (multiple paragraphs)"
        }
        
        bio_prompt = f"""
        Create a compelling professional bio with these specifications:

        USER PROFILE:
        {user_profile}

        JOB CONTEXT (if applicable):
        {job_context or 'General professional bio'}

        BIO SPECIFICATIONS:
        - Length: {length} ({length_guidelines.get(length, '100-150 words')})
        - Style: {style}
        - Context: {context}
        - Perspective: Third person

        Guidelines for this bio:
        1. Start with current role and key expertise
        2. Highlight most impressive achievements
        3. Include relevant experience and skills
        4. End with personal touch or future focus
        5. Use engaging, professional language
        6. Ensure it's appropriate for {context}

        Return only the bio text, no additional formatting or explanations.
        """
        
        result = await self.agent.run(bio_prompt)
        return result.text.strip()
    
    async def generate_presentation_bio(
        self,
        user_profile: Dict[str, Any],
        presentation_topic: str = None,
        audience: str = "professional"
    ) -> str:
        """Generate a bio specifically for presentation slides (PowerPoint ready)."""
        
        presentation_prompt = f"""
        Create a one-page professional bio perfect for PowerPoint presentations:

        USER PROFILE:
        {user_profile}

        PRESENTATION CONTEXT:
        - Topic: {presentation_topic or 'General professional presentation'}
        - Audience: {audience}

        Requirements:
        - 150-200 words maximum
        - Formatted for easy reading on slides
        - Highlight expertise relevant to presentation topic
        - Include key credentials and achievements
        - Professional but engaging tone
        - Third person perspective

        Format as clean text paragraphs that can be easily copied into PowerPoint.
        Focus on credibility and expertise that supports the presentation topic.
        """
        
        result = await self.agent.run(presentation_prompt)
        return result.text.strip()
    
    async def generate_linkedin_summary(
        self,
        user_profile: Dict[str, Any],
        target_roles: list = None,
        industry_focus: str = None
    ) -> str:
        """Generate an optimized LinkedIn summary section."""
        
        linkedin_prompt = f"""
        Create an optimized LinkedIn summary for professional networking and job opportunities:

        USER PROFILE:
        {user_profile}

        TARGET ROLES:
        {target_roles or 'General career advancement'}

        INDUSTRY FOCUS:
        {industry_focus or 'Current industry'}

        LinkedIn Summary Requirements:
        - 200-300 words
        - First person perspective (LinkedIn convention)
        - Hook in first line
        - Include key skills and achievements
        - Show personality and passion
        - Call to action at the end
        - Optimize for LinkedIn search keywords
        - Professional but personable tone

        Format as LinkedIn-ready text with natural paragraph breaks.
        """
        
        result = await self.agent.run(linkedin_prompt)
        return result.text.strip()
    
    async def generate_executive_summary(
        self,
        user_profile: Dict[str, Any],
        executive_level: str = "senior"  # junior, senior, executive, c-level
    ) -> str:
        """Generate an executive-level professional summary."""
        
        exec_prompt = f"""
        Create a high-level executive summary for {executive_level} leadership contexts:

        USER PROFILE:
        {user_profile}

        EXECUTIVE LEVEL: {executive_level}

        Executive Summary Requirements:
        - 100-150 words
        - Focus on leadership and strategic impact
        - Quantify major achievements
        - Emphasize vision and results
        - Industry expertise and thought leadership
        - Board-ready language and tone
        - Third person perspective

        Style should reflect the gravitas and accomplishments expected at the {executive_level} level.
        """
        
        result = await self.agent.run(exec_prompt)
        return result.text.strip()
    
    async def generate_elevator_pitch(
        self,
        user_profile: Dict[str, Any],
        target_audience: str = "potential_employer"
    ) -> str:
        """Generate a 30-second elevator pitch."""
        
        pitch_prompt = f"""
        Create a compelling 30-second elevator pitch:

        USER PROFILE:
        {user_profile}

        TARGET AUDIENCE: {target_audience}

        Elevator Pitch Requirements:
        - 30-45 words maximum
        - First person perspective
        - Hook + expertise + value proposition
        - Conversational and memorable
        - Perfect for networking events
        - Clear call to action or next step

        Make it punchy, confident, and tailored to {target_audience}.
        """
        
        result = await self.agent.run(pitch_prompt)
        return result.text.strip()