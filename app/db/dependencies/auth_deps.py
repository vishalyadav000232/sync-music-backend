from app.db.repositories.interface.user import UserRepositoryInterface
from fastapi import Depends
from app.db.dependencies.user_deps import get_user_repository
from app.core.security import JWTTokenService , TokenServiceInterface
from app.db.dependencies.token_deps import get_token_service
from app.services.auth.auth_service import AuthService






def get_auth_service(
    user_repo: UserRepositoryInterface = Depends(get_user_repository),
    token_service: TokenServiceInterface = Depends(get_token_service)
) -> AuthService:

    return AuthService(user_repo=user_repo, token=token_service)