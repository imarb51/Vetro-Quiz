import os
import requests
import jwt
import json
from fastapi import HTTPException, status
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

class GoogleAuth:
    """Simplified Google OAuth authentication handler."""
    
    @staticmethod
    def verify_google_token(token: str) -> Dict:
        """Verify Google ID token using Google's tokeninfo endpoint."""
        try:
            # Use Google's tokeninfo endpoint to verify the token
            response = requests.get(
                f'https://oauth2.googleapis.com/tokeninfo?id_token={token}',
                timeout=10
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            token_info = response.json()
            
            # Check if the token is for our app
            if token_info.get('aud') != GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid audience"
                )
            
            # Check if token is expired
            import time
            if int(token_info.get('exp', 0)) < time.time():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            
            # Extract user information
            user_info = {
                'google_id': token_info.get('sub', ''),
                'email': token_info.get('email', ''),
                'name': token_info.get('name', ''),
                'picture': token_info.get('picture', ''),
                'email_verified': token_info.get('email_verified', 'false').lower() == 'true'
            }
            
            # Check if email is verified
            if not user_info['email_verified']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google email not verified"
                )
            
            return user_info
            
        except ValueError as e:
            # Invalid token
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Google authentication failed: {str(e)}"
            )
    
    @staticmethod
    def get_user_info_from_token(token: str) -> Optional[Dict]:
        """Extract user info from Google token without verification (for testing)."""
        try:
            return GoogleAuth.verify_google_token(token)
        except HTTPException:
            return None