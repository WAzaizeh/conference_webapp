import os
from dotenv import load_dotenv
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"

class Settings:
    def __init__(self):
        # Determine environment
        self.environment = os.getenv('ENVIRONMENT', Environment.DEVELOPMENT)
        
        # Load appropriate .env file
        if self.environment == Environment.DEVELOPMENT:
            load_dotenv('.env.dev')
        elif self.environment == Environment.PRODUCTION:
            load_dotenv('.env.prod')
        elif self.environment == Environment.TEST:
            load_dotenv('.env.test')
        
        # Load settings
        self.port = int(os.getenv('PORT', 8080))
        self.host = os.getenv('HOST', '0.0.0.0')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.database_url = os.getenv('DATABASE_URL')
        self.admin_username = os.getenv('ADMIN_USERNAME')
        self.admin_password = os.getenv('ADMIN_PASSWORD')
        
        # Validate required settings
        self._validate()
    
    def _validate(self):
        """Validate required environment variables"""
        required = ['DATABASE_URL', 'ADMIN_USERNAME', 'ADMIN_PASSWORD']
        missing = [var for var in required if not getattr(self, var.lower())]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
    
    def is_development(self):
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self):
        return self.environment == Environment.PRODUCTION
    
    def is_test(self):
        return self.environment == Environment.TEST

# Global settings instance
settings = Settings()