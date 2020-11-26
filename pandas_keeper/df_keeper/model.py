from pydantic import BaseModel


class Model(BaseModel):
    class Config:
        extra = "forbid"
