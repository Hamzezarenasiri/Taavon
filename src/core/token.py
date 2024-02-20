import asyncio
from datetime import datetime, timedelta
from datetime import timezone
from typing import List, Optional, Tuple

from fastapi.encoders import jsonable_encoder
from jose import ExpiredSignatureError, JWSError, JWTError, jws, jwt

from src.apps.user.crud import users_crud
from src.core.common import exceptions
from src.core.common.enums import RoleEnum
from src.core.common.models.token import AuthToken, TokenPayload
from src.core.mixins import DB_ID
from src.core.utils import get_random_string
from src.main.config import jwt_settings
from src.services import global_services


class _Token(object):
    def __init__(
        self,
        secret: str,
        algorithm: Optional[str] = None,
    ):
        self.alg = algorithm
        self.secret = secret

    async def create_token(
        self, payload: dict, expiry: Optional[timedelta] = None
    ) -> str:
        if expiry is not None:
            payload["exp"] = datetime.now(timezone.utc) + expiry
        return jwt.encode(payload, key=self.secret, algorithm=self.alg)

    async def verify_token(self, token: str) -> TokenPayload:
        try:
            decode_token = jwt.decode(token, key=self.secret, algorithms=self.alg)
            return TokenPayload(**decode_token)
        except ExpiredSignatureError as e:
            raise exceptions.auth.TokenExpired from e
        except JWTError as e:
            raise exceptions.auth.InvalidTokenProvided from e

    def hash_string(self, s: str) -> str:
        return jws.sign(payload=s.encode(), key=self.secret, algorithm=self.alg)

    def dehash_string(self, s: str) -> str:
        try:
            return jws.verify(token=s, key=self.secret, algorithms=self.alg)
        except JWSError as e:
            raise exceptions.auth.InvalidTokenProvided from e


# ======================== VARIABLES ========================
_access_token_expiry = jwt_settings.ACCESS_TOKEN_LIFETIME_SECONDS
_refresh_token_expiry = jwt_settings.REFRESH_TOKEN_LIFETIME_SECONDS
token_helper = _Token(jwt_settings.SECRET_KEY, jwt_settings.ALGORITHM)


# ======================== UTILITIES ========================
def _encode_refresh_token(user_id: Optional[str] = None, sep: str = "*") -> str:
    """Get a user_id and encode it with the followinig formula:
    user_id + sep + random_string
    The reverse functions should also decode it like so.
    """
    if user_id:
        raw_refresh = user_id + sep + get_random_string(16)
    else:
        raw_refresh = sep + get_random_string(16)
    return token_helper.hash_string(raw_refresh)


def _decode_refresh_token(token: str, sep: str = "*") -> str:
    """Get a refresh token, decode it and return the usesrname."""
    raw_refresh = (token_helper.dehash_string(token)).decode()
    # john.doe.randomstring turns into john.doe
    return "".join(raw_refresh.split(sep)[:-1])


def _encode_user_info(user_id: str) -> str:
    return f"{user_id}"


def _decode_user_info(encoded_string: str) -> List[str]:
    return encoded_string


async def _generate_and_save_token(
    user_id: Optional[DB_ID] = None,
    encrypted_values: Optional[str] = None,
    limited: Optional[bool] = None,
) -> Tuple[str, str]:
    """Generate a refresh & access token & save it to memory"""
    token_payload = TokenPayload(
        user_id=user_id,
        encrypted_values=encrypted_values,
        limited=limited,
    )
    payload = jsonable_encoder(token_payload, exclude_none=True)
    access_token = await token_helper.create_token(
        payload=payload,
        expiry=timedelta(seconds=_access_token_expiry),
    )
    #  because they are not refreshable
    refresh_token = _encode_refresh_token(payload.get("user_id"))

    # we refresh token by storing it in the memory to be used later
    await global_services.CACHE.set(
        refresh_token,
        _encode_user_info(payload.get("user_id")),
        _refresh_token_expiry,
    )

    return access_token, refresh_token


# ======================== CONTROLLER ========================
async def generate_token(
    user_id: Optional[str] = None,
    encrypted_values: Optional[str] = None,
    limited: Optional[bool] = None,
) -> AuthToken:
    access, refresh = await _generate_and_save_token(
        user_id=user_id,
        encrypted_values=encrypted_values,
        limited=limited,
    )
    return AuthToken(access_token=access, refresh_token=refresh)


async def generate_refresh_token(old_refresh_token: str) -> AuthToken:
    encoded_string = await global_services.CACHE.get(old_refresh_token)
    if not encoded_string:
        raise exceptions.RefreshTokenExpired
    user_id = encoded_string.decode()
    payload = TokenPayload(user_id=user_id)
    if user_id is None:
        raise exceptions.InvalidTokenProvided
    token_user_id = _decode_refresh_token(old_refresh_token)

    # just in case
    if token_user_id != user_id:
        raise exceptions.InvalidTokenProvided

    # read from db so that if the role is updated, the new token is affected
    user_db = await users_crud.get_object(criteria={"_id": payload.user_id})

    access_token, refresh_token = (
        await asyncio.gather(
            _generate_and_save_token(
                user_id=user_db.id,
            ),
            global_services.CACHE.delete(old_refresh_token),
        )
    )[0]
    return AuthToken(access_token=access_token, refresh_token=refresh_token)
