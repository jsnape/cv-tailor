    def _clean_job_text(self, text: str) -> str:
        """Clean and prepare job text for analysis."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Extract key information from the beginning (company, job title)
        header_info = ""
        company_match = re.search(r'Microsoft.*?hiring\s+(.*?)\s+in\s+(.*?)\s+\|', text, re.IGNORECASE)
        if company_match:
            header_info = f"Company: Microsoft\nJob Title: {company_match.group(1)}\nLocation: {company_match.group(2)}\n\n"
        
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