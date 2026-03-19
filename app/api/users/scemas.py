from typing import Annotated, Generic, TypeVar
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None


class RegisterRequest(BaseModel):

    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            description="Enter your name",
            examples=["Vishal Yadav"],
        ),
    ]

    username: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            description="Unique username",
            examples=["vishal07"],
        ),
    ]

    email: Annotated[
        EmailStr,
        Field(
            description="User email",
            examples=["user@gmail.com"],
        ),
    ]

    password: Annotated[
        str,
        Field(
            min_length=8,   
            description="Secure password",
            examples=["Password#123"],
        ),
    ]


class LoginRequest(BaseModel):

    email: Annotated[
        EmailStr,
        Field(
            description="User email",
            examples=["user@gmail.com"],
        ),
    ]

    password: Annotated[
        str,
        Field(
            min_length=8,
            description="Secure password",
        ),
    ]


class LoginData(BaseModel):
    access_token: Annotated[
        str,
        Field(
            ...,
            examples=[
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNzA4MzQ1MTIzLCJleHAiOjE3MDgzNTUxMjN9."
                "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            ],
            description="JWT access token"
        )
    ]
    refresh_token: Annotated[
        str,
        Field(
            ...,
            examples=[
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNzA4MzQ1MTIzLCJleHAiOjE3MDgzNTUxMjN9."
                "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            ],
            description="JWT access token"
        )
    ]
    token_type : str


class RegisterData(BaseModel):
    id: UUID
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)


class RegisterResponse(ApiResponse[RegisterData]):
    pass
class LoginResponse(ApiResponse[LoginData]):
    pass



class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    profile_pic_url: Optional[str] = None
    is_verified: bool
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

    