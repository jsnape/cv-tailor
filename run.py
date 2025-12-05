#!/usr/bin/env python3
"""
CV Tailor Agent - Startup Script

This script handles the initialization and startup of the CV Tailor Agent application.
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.utils.config import settings
from src.database.init_db import create_tables


async def startup_checks():
    """Perform startup checks and initialization."""
    print(f"🚀 Starting {settings.app_name} v{settings.version}")
    print(f"📁 Project root: {project_root}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🗄️ Database: {settings.database_url}")
    
    # Check GitHub token
    if not settings.github_token or settings.github_token.startswith('ghp_your_'):
        print("❌ GitHub token not configured!")
        print("   Please set GITHUB_TOKEN in your .env file")
        return False
    else:
        print("✅ GitHub token configured")
    
    # Initialize database
    try:
        await create_tables()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    return True


def main():
    """Main startup function."""
    import uvicorn
    
    # Run startup checks
    if not asyncio.run(startup_checks()):
        print("\n❌ Startup failed. Please fix the issues above and try again.")
        sys.exit(1)
    
    print("\n🎯 All checks passed! Starting the application...")
    print(f"📡 API will be available at: http://localhost:8000")
    print(f"📖 API documentation: http://localhost:8000/docs")
    print(f"🔍 Alternative docs: http://localhost:8000/redoc")
    print("\nPress Ctrl+C to stop the server")
    
    # Start the server
    try:
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.debug,
            log_level="info" if settings.debug else "warning"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()