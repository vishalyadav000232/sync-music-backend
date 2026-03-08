from app.db.repositories.interface.user import UserRepositoryInterface
from app.core.security import TokenServiceInterface, hash_password, verify_password
from app.api.users.scemas import RegisterRequest, LoginRequest
from fastapi import HTTPException, status
from app.db.models.users import User

class AuthService:
    
    def __init__(self, user_repo: UserRepositoryInterface, token: TokenServiceInterface):
        self.user_repo = user_repo
        self.token = token
        
    async def register(self, user: RegisterRequest) -> User:
        
        existing_user = await self.user_repo.get_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists!"
            )
        
        
        existing_user = await self.user_repo.get_by_username(user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken!"
            )
        
        user_dict = {
            "email": user.email,
            "username": user.username,
            "password_hash": hash_password(user.password)
        }
        
        return await self.user_repo.create(user_dict)
    
    async def login(self, payload: LoginRequest) -> dict:
        
        user = await self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
      
        access_token = await self.token.create_access_token(str(user.id))
        refresh_token = await self.token.create_refresh_token(str(user.id))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
            
        }
        
    async def refresh(self , refresh_token : str):
        
        try:
            user_id , jti = await self.token.verify_refresh_token(token=refresh_token)
        
            #  revoke the jwt token and delete the redis from the redis 
            
            await self.token.revoke_refresh_token(refresh_token)
            
            #  create and store the jwt refresh token
            
            new_refresh_token = await self.token.create_refresh_token(user_id)
    
            access_token = await self.token.create_access_token(user_id)
            
            return access_token, new_refresh_token
        
        except Exception as e :
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        
        
        
        
        