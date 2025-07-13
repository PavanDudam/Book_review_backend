from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
import jwt
from source.config import Config
import uuid
import logging
from itsdangerous import URLSafeTimedSerializer

password_context = CryptContext(schemes=["bcrypt"])

ACCESS_TOKEN_EXPIRY = 3600


def generate_hash_password(password: str) -> str:
    hash = password_context.hash(password)
    return hash


def verify_password(plain_password: str, hash_password) -> bool:
    return password_context.verify(plain_password, hash_password)


def create_acces_token(user_data: dict, expiry: timedelta=None, refresh:bool=False):
    payload = {}
    payload["user"] = user_data
    payload["exp"] = datetime.now(timezone.utc) + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    
    payload['jti']  = str(uuid.uuid4())
    payload['refresh'] = refresh
    
    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM
    )

    return token

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            key=Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        logging.warning("⚠️ JWT token has expired")
        return None
    except jwt.DecodeError:
        logging.warning("❌ JWT token is invalid or malformed")
        return None
    except jwt.PyJWTError as e:
        logging.exception("❌ Unexpected JWT error")
        return None

serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET_KEY, salt="email-configuration"
)

def create_url_safe_token(data:dict):
    token = serializer.dumps(data)
    
    return token

def decode_url_safe_token(token:str):
    try:
        token_data=serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(f"Invalid token:{e}")
        return None

