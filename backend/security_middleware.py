from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
from typing import Dict
import re

class SecurityMiddleware:
    """Simple security middleware for rate limiting and validation."""
    
    def __init__(self):
        # Simple in-memory rate limiting (for production, use Redis)
        self.rate_limit_storage: Dict[str, list] = defaultdict(list)
        self.rate_limit_window = 60  # 1 minute
        self.rate_limit_max_requests = 60  # 60 requests per minute
    
    async def rate_limit_check(self, request: Request) -> bool:
        """Check if request exceeds rate limit."""
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Clean old requests
        self.rate_limit_storage[client_ip] = [
            req_time for req_time in self.rate_limit_storage[client_ip]
            if current_time - req_time < self.rate_limit_window
        ]

        # Check if limit exceeded
        if len(self.rate_limit_storage[client_ip]) >= self.rate_limit_max_requests:
            return False

        # Add current request
        self.rate_limit_storage[client_ip].append(current_time)
        return True

    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Simple email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Simple password validation - at least 6 characters."""
        return len(password) >= 6
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 500) -> str:
        """Sanitize string input."""
        if not text:
            return ""
        # Remove potentially dangerous characters and limit length
        sanitized = re.sub(r'[<>\"\'%;()&+]', '', text)
        return sanitized[:max_length].strip()

# Global security instance
security = SecurityMiddleware()

async def security_middleware(request: Request, call_next):
    """Security middleware for all requests."""
    
    # Rate limiting check
    if not await security.rate_limit_check(request):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )
    
    # Add security headers to response
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response