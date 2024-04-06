from passlib.context import CryptContext


_crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _crypt_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return _crypt_context.verify(password, hashed_password)
