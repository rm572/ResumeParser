"""Configuration settings for Resume Parser."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings."""

    # AWS Bedrock Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_SESSION_TOKEN: str = os.getenv("AWS_SESSION_TOKEN", "")
    BEDROCK_MODEL: str = os.getenv("BEDROCK_MODEL", "amazon.titan-text-lite-v1")

    # FastAPI Configuration
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "127.0.0.1")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8000"))

    # Streamlit Configuration
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))

    # DynamoDB Configuration (Optional)
    USE_DYNAMODB: bool = os.getenv("USE_DYNAMODB", "false").lower() == "true"
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    DYNAMODB_TABLE: str = os.getenv("DYNAMODB_TABLE", "resume_results")

    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS: list = ["pdf"]

    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings are configured."""
        if not cls.BEDROCK_MODEL:
            raise ValueError("BEDROCK_MODEL not set in environment")

        return True


# Create settings instance
settings = Settings()
