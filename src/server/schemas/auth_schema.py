from pydantic import BaseModel, Field


class LoginSchema(BaseModel):
    username: str = Field(example='stivenramireza@gmail.com')
    password: str = Field(min_length=8, example='stivenramireza')


class AccessTokenSchema(BaseModel):
    access_token: str