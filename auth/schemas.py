from pydantic import BaseModel, EmailStr, constr

# Model for user registration
class UserRegister(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6)

# Model for user login
class UserLogin(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)

# Model for token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
