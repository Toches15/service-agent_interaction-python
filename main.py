"""
Main entry point for the FastAPI application.

This module serves as the primary entry point and can be used to run
the FastAPI application or other application components.
"""

if __name__ == "__main__":
    try:
        import uvicorn

        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
        )
    except ImportError:
        print("uvicorn is not installed. Install it with: pip install uvicorn")
        raise
