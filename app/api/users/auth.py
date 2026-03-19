from fastapi import APIRouter, Depends , status , HTTPException , Request , Response
from app.services.auth.auth_service import AuthService
from app.db.dependencies.auth_deps import get_auth_service
from app.api.users.scemas import LoginRequest, RegisterRequest , RegisterResponse , LoginResponse , UserResponse
from app.api.deps import get_current_user
from app.db.models.users import User
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import r







router = APIRouter()

@router.post("/login" , status_code=status.HTTP_200_OK )
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    
    
                ):
    
    
    payload = LoginRequest(
        email=form_data.username,
        password=form_data.password
    )
    
    data = await auth_service.login(payload)
    response.set_cookie(
        key="refresh_token",
        value=data["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*7
    )

    return {
        "access_token" : data["access_token"],
        "type":"bearer"
    }

@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse
)
async def signup(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    created_user = await auth_service.register(payload)

    return RegisterResponse(
        success=True,
        message="User successfully registered",
        data=created_user
    )
@router.get("/me" , status_code=status.HTTP_200_OK , response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
   
    refresh_token_cookie = request.cookies.get("refresh_token")
    print("cookies rfresh token " , refresh_token_cookie)

    if not refresh_token_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    try:
        
        access_token, new_refresh_token = await auth_service.refresh(
            refresh_token_cookie
        )

        # Set new refresh token in cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=False,  
            samesite="lax",
            max_age=60*60*24*7,
            path="/"
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )