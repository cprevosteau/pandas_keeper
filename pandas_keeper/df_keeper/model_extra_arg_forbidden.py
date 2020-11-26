from pydantic import BaseModel


class ModelExtraArgForbidden(BaseModel):
    class Config:
        extra = "forbid"
