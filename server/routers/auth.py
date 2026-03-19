"""登录接口"""

from fastapi import APIRouter, HTTPException
from server.schemas import LoginRequest, LoginResponse
from server.auth import verify_login, create_token

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    if not verify_login(req.username, req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_token(req.username)
    return LoginResponse(token=token, username=req.username)
