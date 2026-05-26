from pydantic import BaseModel


class CommentCreate(BaseModel):
    author_id: int
    content: str

class CommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    content: str
    summary: str | None = None