from pydantic import BaseModel


class PostCreate(BaseModel):
    author_id: int
    title: str
    content: str

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class PostResponse(BaseModel):
    id: int
    author_id: int
    title: str
    content: str
    summary: str | None = None
