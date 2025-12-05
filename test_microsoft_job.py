#!/usr/bin/env python3
"""
Quick test script for the Microsoft job posting
"""
import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.agents.job_analyzer import JobAnalyzerAgent
from src.agents.cv_tailor import CVTailorAgent
from src.agents.bio_generator import BioGeneratorAgent

async def test_microsoft_job():
    """Test with Microsoft job posting"""
    
    # Load your profile
    with open('james_snape_profile.json', 'r') as f:
        profile_data = json.load(f)
    
    print("✅ Profile loaded")
    
    # Initialize agents
    job_analyzer = JobAnalyzerAgent()
    cv_tailor = CVTailorAgent()
    bio_generator = BioGeneratorAgent()
    
    # Analyze the Microsoft job
    job_url = "https://www.linkedin.com/jobs/view/4315439601/"
    print(f"🔍 Analyzing job: {job_url}")
    print("Using improved job analyzer...")
    
    job_analysis = await job_analyzer.analyze_job_posting(job_url)
    
    print("\n" + "="*60)
    print("JOB ANALYSIS RESULTS")
    print("="*60)
    print(f"📋 Job Title: {job_analysis.get('job_title', 'Not specified')}")
    print(f"🏢 Company: {job_analysis.get('company_name', 'Not specified')}")
    print(f"📍 Location: {job_analysis.get('location', 'Not specified')}")
    
    # Handle nested required_skills structure
    required_skills = job_analysis.get('required_skills', {})
    technical_skills = required_skills.get('technical_skills', [])
    soft_skills = required_skills.get('soft_skills', [])
    
    print(f"💻 Technical Skills: {', '.join(technical_skills) if technical_skills else 'Not specified'}")
    print(f"🤝 Soft Skills: {', '.join(soft_skills) if soft_skills else 'Not specified'}")
    print(f"📅 Experience: {job_analysis.get('required_experience', 'Not specified')}")
    print(f"🔑 Key Keywords: {', '.join(job_analysis.get('keywords', []))}")
    print("="*60)
    
    # Generate tailored CV with gap analysis
    print("\n📝 Generating tailored CV with gap analysis...")
    cv_result = await cv_tailor.generate_tailored_cv(
        user_profile=profile_data,
        job_analysis=job_analysis,
        style="professional",
        include_gap_analysis=True
    )
    
    print("\n" + "="*80)
    print("GENERATED TAILORED CV")
    print("="*80)
    print(cv_result["cv_content"])
    print("="*80)
    
    # Display gap analysis
    gap_analysis = cv_result.get("gap_analysis")
    if gap_analysis:
        print("\n" + "="*80)
        print("PROFILE GAP ANALYSIS & IMPROVEMENT SUGGESTIONS")
        print("="*80)
        
        print(f"📊 Profile Match: {gap_analysis.get('match_percentage', 'Unknown')}")
        
        # Technical skills gaps
        tech_gaps = gap_analysis.get('technical_skills_gaps', [])
        if tech_gaps:
            print("\n⚠️ MISSING TECHNICAL SKILLS:")
            for gap in tech_gaps:
                print(f"  • {gap.get('missing_skill', 'Unknown')}")
                print(f"    Why it matters: {gap.get('importance', 'Not specified')}")
                print(f"    Suggestion: {gap.get('suggestion', 'Not specified')}")
                print()
        
        # Experience gaps
        exp_gaps = gap_analysis.get('experience_gaps', [])
        if exp_gaps:
            print("⚠️ MISSING EXPERIENCE:")
            for gap in exp_gaps:
                print(f"  • {gap.get('missing_experience', 'Unknown')}")
                print(f"    Why it matters: {gap.get('importance', 'Not specified')}")
                print(f"    Suggestion: {gap.get('suggestion', 'Not specified')}")
                print()
        
        # Soft skills gaps
        soft_gaps = gap_analysis.get('soft_skills_gaps', [])
        if soft_gaps:
            print("⚠️ MISSING SOFT SKILLS:")
            for gap in soft_gaps:
                print(f"  • {gap.get('missing_soft_skill', 'Unknown')}")
                print(f"    Why it matters: {gap.get('importance', 'Not specified')}")
                print(f"    Suggestion: {gap.get('suggestion', 'Not specified')}")
                print()
        
        # Certification gaps
        cert_gaps = gap_analysis.get('certification_gaps', [])
        if cert_gaps:
            print("⚠️ RECOMMENDED CERTIFICATIONS:")
            for gap in cert_gaps:
                print(f"  • {gap.get('missing_certification', 'Unknown')}")
                print(f"    Why it matters: {gap.get('importance', 'Not specified')}")
                print(f"    Suggestion: {gap.get('suggestion', 'Not specified')}")
                print()
        
        # Strengths
        strengths = gap_analysis.get('overall_strengths', [])
        if strengths:
            print("✅ YOUR STRENGTHS FOR THIS ROLE:")
            for strength in strengths:
                print(f"  • {strength}")
        
        print("="*80)
    
    # Generate bio
    print("\n✍️ Generating professional bio...")
    bio_content = await bio_generator.generate_professional_bio(
        user_profile=profile_data,
        job_context=job_analysis,
        length="medium",
        context="presentation"
    )
    
    print("\n" + "="*80)
    print("GENERATED BIO")
    print("="*80)
    print(bio_content)
    print("="*80)
    
    print("\n🎉 Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_microsoft_job())