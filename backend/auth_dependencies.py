from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from auth_utils import verify_token
from database import get_user_by_id
from auth_models import User

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Get current authenticated user (optional - for backward compatibility)."""
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials, "access")
        user_id = payload.get("sub")
        
        if user_id is None:
            return None
            
        user_data = get_user_by_id(user_id)
        if user_data is None:
            return None
            
        return User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            phone=user_data["phone"],
            address=user_data["address"],
            is_active=user_data["is_active"],
            is_admin=user_data["is_admin"],
            created_at=user_data["created_at"]
        )
        
    except HTTPException:
        return None

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active authenticated user (required)."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current admin user (required)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user

# Optional authentication for backward compatibility
async def get_optional_user(current_user: Optional[User] = Depends(get_current_user)) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for backward compatibility)."""
    return current_user