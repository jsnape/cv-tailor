#!/usr/bin/env python3
"""
Debug script to see what content is being fetched from LinkedIn
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def debug_linkedin_fetch():
    """Debug LinkedIn content fetching"""
    
    url = "https://www.linkedin.com/jobs/view/4315439601/"
    print(f"🔍 Fetching content from: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Add headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            async with session.get(url, headers=headers) as response:
                print(f"📊 Response status: {response.status}")
                print(f"📊 Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    html = await response.text()
                    print(f"📊 HTML length: {len(html)} characters")
                    
                    # Save raw HTML for inspection
                    with open('debug_linkedin_raw.html', 'w', encoding='utf-8') as f:
                        f.write(html)
                    print("💾 Saved raw HTML to debug_linkedin_raw.html")
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text
                    text = soup.get_text()
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    clean_text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    print(f"📊 Cleaned text length: {len(clean_text)} characters")
                    print("\n" + "="*80)
                    print("FIRST 2000 CHARACTERS OF CLEANED TEXT:")
                    print("="*80)
                    print(clean_text[:2000])
                    print("="*80)
                    
                    # Save cleaned text
                    with open('debug_linkedin_cleaned.txt', 'w', encoding='utf-8') as f:
                        f.write(clean_text)
                    print("💾 Saved cleaned text to debug_linkedin_cleaned.txt")
                    
                else:
                    print(f"❌ Failed to fetch: HTTP {response.status}")
                    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_linkedin_fetch())