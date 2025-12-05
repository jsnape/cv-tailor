#!/usr/bin/env python3
"""
CV Tailor Agent - Command Line Interface

A CLI tool for testing and interacting with the CV Tailor Agent functionality.
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import click

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.agents.job_analyzer import JobAnalyzerAgent
from src.agents.cv_tailor import CVTailorAgent
from src.agents.bio_generator import BioGeneratorAgent
from src.utils.config import settings
from src.utils.helpers import clean_text, generate_filename


class CVTailorCLI:
    """CLI interface for CV Tailor Agent."""
    
    def __init__(self):
        self.job_analyzer = JobAnalyzerAgent()
        self.cv_tailor = CVTailorAgent()
        self.bio_generator = BioGeneratorAgent()
        self.profile_data = None
        self.job_analysis = None
    
    async def load_profile(self, profile_path: str) -> bool:
        """Load user profile from JSON file."""
        try:
            with open(profile_path, 'r') as f:
                self.profile_data = json.load(f)
            click.echo(f"✅ Profile loaded from {profile_path}")
            return True
        except FileNotFoundError:
            click.echo(f"❌ Profile file not found: {profile_path}")
            return False
        except json.JSONDecodeError:
            click.echo(f"❌ Invalid JSON in profile file: {profile_path}")
            return False
    
    async def analyze_job(self, job_url: str = None, job_file: str = None) -> bool:
        """Analyze a job posting."""
        try:
            click.echo("🔍 Analyzing job posting...")
            
            if job_file:
                with open(job_file, 'r') as f:
                    job_text = f.read()
                self.job_analysis = await self.job_analyzer.analyze_job_posting(job_text=job_text)
            elif job_url:
                self.job_analysis = await self.job_analyzer.analyze_job_posting(job_url=job_url)
            else:
                click.echo("❌ Either job_url or job_file must be provided")
                return False
            
            click.echo("✅ Job analysis complete!")
            self._display_job_analysis()
            return True
            
        except Exception as e:
            click.echo(f"❌ Job analysis failed: {str(e)}")
            return False
    
    async def generate_cv(self, style: str = "professional", output_file: str = None) -> bool:
        """Generate tailored CV."""
        if not self.profile_data:
            click.echo("❌ No profile loaded. Use 'load-profile' first.")
            return False
        
        if not self.job_analysis:
            click.echo("❌ No job analysis available. Use 'analyze-job' first.")
            return False
        
        try:
            click.echo("📝 Generating tailored CV...")
            
            cv_content = await self.cv_tailor.generate_tailored_cv(
                user_profile=self.profile_data,
                job_analysis=self.job_analysis,
                style=style,
                format_type="ats_optimized"
            )
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(cv_content)
                click.echo(f"✅ CV saved to {output_file}")
            else:
                click.echo("\n" + "="*80)
                click.echo("GENERATED CV")
                click.echo("="*80)
                click.echo(cv_content)
                click.echo("="*80)
            
            return True
            
        except Exception as e:
            click.echo(f"❌ CV generation failed: {str(e)}")
            return False
    
    async def generate_bio(self, length: str = "medium", context: str = "presentation", output_file: str = None) -> bool:
        """Generate professional bio."""
        if not self.profile_data:
            click.echo("❌ No profile loaded. Use 'load-profile' first.")
            return False
        
        try:
            click.echo("✍️ Generating professional bio...")
            
            if context == "presentation":
                bio_content = await self.bio_generator.generate_presentation_bio(
                    user_profile=self.profile_data,
                    audience="professional"
                )
            elif context == "linkedin":
                bio_content = await self.bio_generator.generate_linkedin_summary(
                    user_profile=self.profile_data
                )
            elif context == "elevator":
                bio_content = await self.bio_generator.generate_elevator_pitch(
                    user_profile=self.profile_data
                )
            else:
                bio_content = await self.bio_generator.generate_professional_bio(
                    user_profile=self.profile_data,
                    job_context=self.job_analysis,
                    length=length,
                    context=context
                )
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(bio_content)
                click.echo(f"✅ Bio saved to {output_file}")
            else:
                click.echo("\n" + "="*80)
                click.echo(f"GENERATED BIO ({context.upper()}, {length.upper()})")
                click.echo("="*80)
                click.echo(bio_content)
                click.echo("="*80)
            
            return True
            
        except Exception as e:
            click.echo(f"❌ Bio generation failed: {str(e)}")
            return False
    
    def _display_job_analysis(self):
        """Display job analysis results."""
        if not self.job_analysis:
            return
        
        click.echo("\n" + "="*60)
        click.echo("JOB ANALYSIS RESULTS")
        click.echo("="*60)
        
        # Basic info
        click.echo(f"📋 Job Title: {self.job_analysis.get('job_title', 'N/A')}")
        click.echo(f"🏢 Company: {self.job_analysis.get('company_name', 'N/A')}")
        click.echo(f"📍 Location: {self.job_analysis.get('location', 'N/A')}")
        
        # Required skills
        required_skills = self.job_analysis.get('required_skills', {})
        if required_skills.get('technical_skills'):
            click.echo(f"💻 Technical Skills: {', '.join(required_skills['technical_skills'][:5])}")
        
        if required_skills.get('soft_skills'):
            click.echo(f"🤝 Soft Skills: {', '.join(required_skills['soft_skills'][:5])}")
        
        if required_skills.get('experience_years'):
            click.echo(f"📅 Experience: {required_skills['experience_years']} years")
        
        # Keywords
        keywords = self.job_analysis.get('keywords', [])
        if keywords:
            click.echo(f"🔑 Key Keywords: {', '.join(keywords[:8])}")
        
        click.echo("="*60)
    
    def create_sample_profile(self, output_file: str):
        """Create a sample profile file."""
        sample_profile = {
            "personal_info": {
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123",
                "location": "San Francisco, CA",
                "linkedin": "linkedin.com/in/johndoe",
                "portfolio": "johndoe.dev",
                "github": "github.com/johndoe"
            },
            "professional_summary": "Experienced software engineer with 8+ years in full-stack development, specializing in Python, JavaScript, and cloud technologies. Proven track record of leading teams and delivering scalable solutions.",
            "technical_skills": {
                "programming": ["Python", "JavaScript", "Java", "Go"],
                "frameworks": ["React", "Django", "FastAPI", "Node.js"],
                "tools": ["Docker", "Kubernetes", "Git", "Jenkins"],
                "databases": ["PostgreSQL", "MongoDB", "Redis"],
                "cloud": ["AWS", "Azure", "GCP"]
            },
            "soft_skills": ["Leadership", "Communication", "Problem-solving", "Team collaboration", "Mentoring"],
            "work_experience": [
                {
                    "company": "Tech Corp",
                    "position": "Senior Software Engineer",
                    "start_date": "2020-01-01",
                    "end_date": "2024-12-01",
                    "description": "Led development of microservices architecture serving 1M+ users. Mentored junior developers and improved deployment efficiency by 40%.",
                    "achievements": [
                        "Reduced system latency by 50% through optimization",
                        "Led team of 5 developers on critical projects",
                        "Implemented CI/CD pipeline reducing deployment time by 60%"
                    ],
                    "technologies": ["Python", "Django", "PostgreSQL", "AWS", "Docker"]
                },
                {
                    "company": "StartupXYZ",
                    "position": "Full Stack Developer",
                    "start_date": "2018-06-01",
                    "end_date": "2019-12-01",
                    "description": "Built entire web platform from scratch using modern technologies. Worked directly with founders to define product requirements.",
                    "achievements": [
                        "Developed MVP that secured $2M in Series A funding",
                        "Built real-time analytics dashboard processing 100K+ events/day"
                    ],
                    "technologies": ["JavaScript", "React", "Node.js", "MongoDB"]
                }
            ],
            "education": [
                {
                    "institution": "University of California, Berkeley",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Computer Science",
                    "start_date": "2014-09-01",
                    "end_date": "2018-05-01",
                    "gpa": "3.8",
                    "achievements": ["Dean's List", "Computer Science Honor Society"]
                }
            ],
            "projects": [
                {
                    "name": "Open Source ML Library",
                    "description": "Created and maintain a machine learning library with 2K+ GitHub stars",
                    "technologies": ["Python", "TensorFlow", "Scikit-learn"],
                    "url": "https://github.com/johndoe/ml-lib",
                    "start_date": "2022-01-01"
                },
                {
                    "name": "Personal Finance App",
                    "description": "Full-stack application for tracking expenses and investments",
                    "technologies": ["React", "Node.js", "PostgreSQL"],
                    "url": "https://financeapp.com",
                    "start_date": "2023-06-01",
                    "end_date": "2023-12-01"
                }
            ],
            "certifications": [
                {
                    "name": "AWS Solutions Architect",
                    "issuer": "Amazon Web Services",
                    "date_obtained": "2022-03-15",
                    "credential_id": "AWS-SAA-123456"
                }
            ],
            "languages": ["English (Native)", "Spanish (Conversational)"]
        }
        
        with open(output_file, 'w') as f:
            json.dump(sample_profile, f, indent=2)
        
        click.echo(f"✅ Sample profile created: {output_file}")


# CLI Commands
cli = CVTailorCLI()

@click.group()
def main():
    """CV Tailor Agent - CLI Tool for testing AI-powered resume customization."""
    # Check if GitHub token is configured
    if not settings.github_token or settings.github_token.startswith('ghp_your_'):
        click.echo("⚠️ Warning: GitHub token not configured in .env file")
        click.echo("   Some features may not work properly")


@main.command()
@click.argument('profile_path', type=click.Path(exists=True))
def load_profile(profile_path):
    """Load user profile from JSON file."""
    asyncio.run(cli.load_profile(profile_path))


@main.command()
@click.option('--url', help='Job posting URL')
@click.option('--file', 'job_file', help='Job posting text file')
def analyze_job(url, job_file):
    """Analyze a job posting from URL or text file."""
    if not url and not job_file:
        click.echo("❌ Either --url or --file must be provided")
        return
    
    asyncio.run(cli.analyze_job(job_url=url, job_file=job_file))


@main.command()
@click.option('--style', default='professional', 
              type=click.Choice(['professional', 'creative', 'modern', 'minimal']),
              help='CV style')
@click.option('--output', help='Output file path')
def generate_cv(style, output):
    """Generate tailored CV based on job analysis and profile."""
    asyncio.run(cli.generate_cv(style=style, output_file=output))


@main.command()
@click.option('--length', default='medium', 
              type=click.Choice(['short', 'medium', 'long']),
              help='Bio length')
@click.option('--context', default='presentation', 
              type=click.Choice(['presentation', 'linkedin', 'executive', 'elevator']),
              help='Bio context/purpose')
@click.option('--output', help='Output file path')
def generate_bio(length, context, output):
    """Generate professional bio."""
    asyncio.run(cli.generate_bio(length=length, context=context, output_file=output))


@main.command()
@click.argument('output_file', default='sample_profile.json')
def create_sample(output_file):
    """Create a sample profile file for testing."""
    cli.create_sample_profile(output_file)


@main.command()
@click.argument('job_text', required=False)
def quick_test(job_text):
    """Quick end-to-end test with sample data."""
    async def run_test():
        click.echo("🚀 Running quick end-to-end test...")
        
        # Create sample profile if it doesn't exist
        sample_profile = 'test_profile.json'
        if not Path(sample_profile).exists():
            cli.create_sample_profile(sample_profile)
        
        # Load profile
        await cli.load_profile(sample_profile)
        
        # Use provided job text or default
        if not job_text:
            test_job = """
            Senior Software Engineer - AI/ML Platform
            
            TechCorp is seeking a Senior Software Engineer to join our AI/ML Platform team. 
            
            Requirements:
            - 5+ years of software engineering experience
            - Strong proficiency in Python, JavaScript
            - Experience with machine learning frameworks (TensorFlow, PyTorch)
            - Cloud platforms (AWS, Azure, GCP)
            - Docker, Kubernetes experience
            - Strong problem-solving and communication skills
            
            Responsibilities:
            - Design and implement scalable ML pipelines
            - Collaborate with data scientists and engineers
            - Mentor junior team members
            - Contribute to architectural decisions
            
            Location: San Francisco, CA (Remote friendly)
            Salary: $150K - $200K
            """
        else:
            test_job = job_text
        
        # Save job text to temporary file
        temp_job_file = 'temp_job.txt'
        with open(temp_job_file, 'w') as f:
            f.write(test_job)
        
        # Analyze job
        await cli.analyze_job(job_file=temp_job_file)
        
        # Generate CV
        click.echo("\n" + "="*50)
        click.echo("GENERATING TAILORED CV")
        click.echo("="*50)
        await cli.generate_cv()
        
        # Generate bio
        click.echo("\n" + "="*50)
        click.echo("GENERATING PRESENTATION BIO")
        click.echo("="*50)
        await cli.generate_bio(context='presentation')
        
        # Cleanup
        Path(temp_job_file).unlink(missing_ok=True)
        
        click.echo("\n✅ Quick test completed!")
    
    asyncio.run(run_test())


@main.command()
def status():
    """Show configuration status."""
    click.echo(f"🔧 Configuration Status")
    click.echo(f"GitHub Token: {'✅ Configured' if settings.github_token and not settings.github_token.startswith('ghp_your_') else '❌ Not configured'}")
    click.echo(f"Default Model: {settings.default_model_id}")
    click.echo(f"Debug Mode: {settings.debug}")
    click.echo(f"Profile Loaded: {'✅ Yes' if cli.profile_data else '❌ No'}")
    click.echo(f"Job Analysis: {'✅ Available' if cli.job_analysis else '❌ Not available'}")


if __name__ == '__main__':
    main()