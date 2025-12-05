# CV Tailor Agent - CLI Usage Guide

## Overview
The CLI tool allows you to test the CV Tailor Agent functionality without setting up the full web API. It provides all core features including job analysis, CV generation, and bio creation.

## Prerequisites
1. Set up your `.env` file with a valid GitHub token
2. Install dependencies: `pip install -r requirements.txt`

## Quick Start

### 1. Run End-to-End Test
Test the entire workflow with sample data:
```bash
python cli.py quick-test
```
This will:
- Create a sample profile
- Analyze a sample job posting  
- Generate a tailored CV
- Generate a presentation bio

### 2. Create Your Profile
Create a sample profile to customize:
```bash
python cli.py create-sample my_profile.json
```
Then edit `my_profile.json` with your actual information.

## Detailed Usage

### Profile Management
```bash
# Create a sample profile file
python cli.py create-sample [profile_file]

# Load your profile (required for CV/bio generation)
python cli.py load-profile path/to/profile.json
```

### Job Analysis
```bash
# Analyze job from URL
python cli.py analyze-job --url "https://company.com/careers/job-id"

# Analyze job from text file
python cli.py analyze-job --file job_posting.txt

# Both commands will display extracted job requirements
```

### CV Generation
```bash
# Generate CV with default settings
python cli.py generate-cv

# Specify style and output file
python cli.py generate-cv --style professional --output tailored_cv.md

# Available styles: professional, creative, modern, minimal
```

### Bio Generation
```bash
# Generate presentation bio
python cli.py generate-bio --context presentation --length medium

# Generate LinkedIn summary
python cli.py generate-bio --context linkedin --output linkedin_summary.txt

# Generate elevator pitch
python cli.py generate-bio --context elevator

# Available contexts: presentation, linkedin, executive, elevator
# Available lengths: short, medium, long
```

### Utility Commands
```bash
# Check configuration and status
python cli.py status

# Get help for any command
python cli.py [command] --help
```

## Profile File Format

Your profile should be a JSON file with this structure:

```json
{
  "personal_info": {
    "full_name": "Your Name",
    "email": "your.email@example.com",
    "phone": "+1-555-0123",
    "location": "City, State",
    "linkedin": "linkedin.com/in/yourname",
    "portfolio": "yourwebsite.com",
    "github": "github.com/yourusername"
  },
  "professional_summary": "Brief summary of your professional background...",
  "technical_skills": {
    "programming": ["Python", "JavaScript", "Java"],
    "frameworks": ["React", "Django", "FastAPI"],
    "tools": ["Docker", "Git", "AWS"],
    "databases": ["PostgreSQL", "MongoDB"]
  },
  "soft_skills": ["Leadership", "Communication", "Problem-solving"],
  "work_experience": [
    {
      "company": "Company Name",
      "position": "Your Title",
      "start_date": "2020-01-01",
      "end_date": "2023-12-01",
      "description": "What you did in this role...",
      "achievements": [
        "Specific achievement with metrics",
        "Another accomplishment"
      ],
      "technologies": ["Python", "AWS", "PostgreSQL"]
    }
  ],
  "education": [
    {
      "institution": "University Name",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "start_date": "2016-09-01",
      "end_date": "2020-05-01",
      "gpa": "3.8"
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "description": "What the project does...",
      "technologies": ["Python", "React", "PostgreSQL"],
      "url": "https://github.com/you/project",
      "start_date": "2022-01-01",
      "end_date": "2022-06-01"
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
```

## Example Workflow

1. **Setup**:
   ```bash
   # Create and customize your profile
   python cli.py create-sample my_profile.json
   # Edit my_profile.json with your information
   
   # Load your profile
   python cli.py load-profile my_profile.json
   ```

2. **Job Analysis**:
   ```bash
   # Save job posting to a text file, then:
   python cli.py analyze-job --file job_posting.txt
   ```

3. **Generate Content**:
   ```bash
   # Generate tailored CV
   python cli.py generate-cv --style professional --output cv_for_job.md
   
   # Generate bio for presentation
   python cli.py generate-bio --context presentation --output bio_slide.txt
   ```

4. **Review and Refine**:
   - Review the generated content
   - Adjust your profile if needed
   - Re-run generation commands to get updated results

## Tips

- **Job Analysis**: The more detailed the job posting, the better the analysis and tailoring
- **Profile Details**: Include specific achievements with metrics for better CV generation
- **Multiple Runs**: Try different styles and contexts to see various approaches
- **Iterative Process**: Update your profile based on results and regenerate content

## Troubleshooting

- **"GitHub token not configured"**: Add your GitHub Personal Access Token to the `.env` file
- **"Profile not loaded"**: Use `load-profile` command before generating CVs or bios
- **"Job analysis not available"**: Use `analyze-job` command before generating tailored content
- **Network errors**: Check your internet connection for job URL analysis
- **JSON errors**: Validate your profile JSON file format

## Getting Help

```bash
# General help
python cli.py --help

# Help for specific commands
python cli.py generate-cv --help
python cli.py analyze-job --help
```