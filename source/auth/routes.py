from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from .schemas import UserCreate, UserOut, UserLogin, UserBookModel, EmailModel, PasswordResetRequestModel, PasswordRequestConfirmModel
from .services import UserService
from source.db.main import get_sessiion
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import (
    create_acces_token,
    decode_token,
    verify_password,
    generate_hash_password,
    create_url_safe_token,
    decode_url_safe_token,
)
from datetime import timedelta, datetime, timezone
from fastapi.responses import JSONResponse
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from source.db.redis import add_jti_to_blocklist
from source.errors import (
    UserAlreadyExists,
    UserNotFound,
    InvalidCredentials,
    InvalidToken,
)
from source.mail import mail, create_message
from source.config import Config

from source.celery_task import send_email

REFRESH_TOKEN_EXPIRY = 2

refresh_token_beaer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])
auth_router = APIRouter()
user_service = UserService()


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses

    html = "<h1>Welcome to the app</h1>"
    subject="Welcome to our app"
    send_email.delay(emails, subject,html)
    return {"message": "Email sent successfully"}


@auth_router.post("/signup")
async def create_user_account(
    user_data: UserCreate, bg_tasks:BackgroundTasks,session: AsyncSession = Depends(get_sessiion)
):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
    emails=[email]
    subject = "Verify your email"
    send_email.delay(emails, subject, html_message)
    #await mail.send_message(meassage)
    # bg_tasks.add_task(mail.send_message, meassage)

    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user,
    }


@auth_router.get("/verify/{token}")
async def verufy_user_account(
    token: str, session: AsyncSession = Depends(get_sessiion)
):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {"isverified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )
    
    return JSONResponse(
        content={"message":"Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


@auth_router.post("/login")
async def login_user(
    login_data: UserLogin, session: AsyncSession = Depends(get_sessiion)
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
    if user:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_acces_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                }
            )

            refresh_token = create_acces_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login sucessful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "user_uid": str(user.uid)},
                }
            )
    raise InvalidCredentials()


@auth_router.get("/refresh_token")
async def generate_new_access_token(token_detail: dict = Depends(refresh_token_beaer)):
    expiry_time_stamp = token_detail["exp"]

    if datetime.fromtimestamp(expiry_time_stamp, tz=timezone.utc) > datetime.now(
        timezone.utc
    ):
        new_access_token = create_acces_token(user_data=token_detail["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken()


@auth_router.get("/logout")
async def revooke_token(token_details: dict = Depends(access_token_bearer)):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out successfully"}, status_code=status.HTTP_200_OK
    )


@auth_router.get("/me", response_model=UserBookModel)
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    return user

@auth_router.post("/password-reset-request")
async def password_reset_request(email_data:PasswordResetRequestModel):
    email = email_data.email
    
    token = create_url_safe_token({"email":email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    
    html_message = f"""
    <h1>Reset your password</h1>
    <p>Please click this <a href="{link}">link</a> to Rest your password</p>
    """
    
    message = create_message(
        recipients=[email], subject="Reset Your password", body=html_message    
    )
    
    await mail.send_message(message)
    
    return JSONResponse(
        content={
        "message":"Please check your email for instructions to reset your password"
        },
        status_code=status.HTTP_200_OK
    )
    
@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(token:str, passwords:PasswordRequestConfirmModel, session:AsyncSession=Depends(get_sessiion)):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_password
    
    if new_password != confirm_password:
        raise HTTPException(
            detail="Password do not match", status_code=status.HTTP_400_BAD_REQUEST
        )
        
    token_data = decode_url_safe_token(token)

    if not token_data:
        raise HTTPException(
        status_code=400,
        detail="Invalid or expired token."
    )
        
    user_email = token_data.get("email")
    if user_email:
        user =  await user_service.get_user_by_email(user_email, session)
        
        if not user:
            raise UserNotFound()
        
        password_hash = generate_hash_password(new_password)
        await user_service.update_user(user, {"password_hash":password_hash}, session)
        return JSONResponse(
            content={"message":"Password reset successfully"},
            status_code=status.HTTP_200_OK     
        )
        
    return JSONResponse(
        content={"message":"Error occured during password reset"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )