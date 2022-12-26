from pydantic import BaseModel


class Token(BaseModel):
    file_name: str = None
    file_path: str = None