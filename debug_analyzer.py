#!/usr/bin/env python3
"""
Test the improved job analyzer with debug output
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.agents.job_analyzer import JobAnalyzerAgent

async def test_improved_analyzer():
    """Test the improved job analyzer"""
    
    analyzer = JobAnalyzerAgent()
    url = "https://www.linkedin.com/jobs/view/4315439601/"
    
    print(f"🔍 Analyzing: {url}")
    
    # Fetch and clean content
    raw_content = await analyzer.fetch_job_content(url)
    print(f"📊 Raw content length: {len(raw_content)}")
    
    cleaned_content = analyzer._clean_job_text(raw_content)
    print(f"📊 Cleaned content length: {len(cleaned_content)}")
    
    print("\n" + "="*80)
    print("FIRST 2000 CHARACTERS OF CLEANED CONTENT:")
    print("="*80)
    print(cleaned_content[:2000])
    print("="*80)
    
    print("\n🤖 Running AI analysis...")
    result = await analyzer.analyze_job_posting(job_url=url)
    
    print("\n" + "="*80)
    print("STRUCTURED ANALYSIS RESULTS:")
    print("="*80)
    import json
    print(json.dumps(result, indent=2))
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_improved_analyzer())