
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from abc import abstractmethod , ABC
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
import uuid
import redis
from app.db.dependencies.refresh_deps import get_refresh_service
from app.services.refresh_token_service import RefreshTokenService
from fastapi import HTTPException , status


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

class TokenServiceInterface(ABC):

    @abstractmethod
    async def create_access_token(self, user_id: str) -> str:
        pass

    @abstractmethod
    async def create_refresh_token(self, user_id: str) -> str:
        pass

    @abstractmethod
    async def verify_access_token(self, token: str) -> str:
        pass

    @abstractmethod
    async def verify_refresh_token(self, token: str) -> str:
        pass
    @abstractmethod
    async def revoke_refresh_token(self, token: str) -> None:
        pass





class JWTTokenService(TokenServiceInterface):

    def __init__(
        self,
        refresh_service : RefreshTokenService,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 7,
    ):
        self.secret_key = settings.JWT_SECRET
        if not self.secret_key:
            raise ValueError("secrete key does not have")
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.refresh_service= refresh_service

    async def create_access_token(self, user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(
            minutes=self.access_token_expire_minutes
        )

        payload = {
            "sub": user_id,
            "type": "access",
            "exp": expire,
        }

        

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    async def create_refresh_token(self, user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(
            days=self.refresh_token_expire_days
        )
        jti = str(uuid.uuid4())

        payload = {
            "sub": user_id,
            "type": "refresh",
            "jti" : jti,
            "exp": expire,
        }
        refres_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        # save in db jti 
        
        await self.refresh_service.create_token(user_id=user_id , jti=jti)   
        
        
        r.set(f"refresh:{jti}", user_id , ex = int(timedelta(days=self.refresh_token_expire_days).total_seconds()))

        return refres_token

    async def verify_access_token(self, token: str) -> str:
        payload = self.verify_token(token, expected_type="access")
        return payload["sub"]
    
    
    

    async def verify_refresh_token(self, token: str):

        payload = self.verify_token(token, expected_type="refresh")

        jti = payload.get("jti")

        
        if not r.get(f"refresh:{jti}"):
            raise ValueError("Refresh token revoked or expired")

        
        is_valid = await self.refresh_service.validate_token(jti)

        if not is_valid:
            raise ValueError("Refresh token revoked in database")

        return payload["sub"], jti
    
    
    
    

    def verify_token(self, token: str, expected_type: str) -> str:
        
        try:
            payload =  jwt.decode(
                token=token,
                key=self.secret_key,
                algorithms=self.algorithm
            )
            

            if payload.get("type") != expected_type:
                raise ValueError("Invalid token type")

            return payload

        

        except JWTError:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired"
    )
       
        
    async def revoke_refresh_token(self, token: str)-> tuple[str, str]:
        payload = self.verify_token(token, expected_type="refresh")
        jti = payload.get("jti")


        r.delete(f"refresh:{jti}")

    
        await self.refresh_service.revoke_token(jti)
    


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)