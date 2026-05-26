# DB 연산(select, insert, delete 등)만 관리
from . import user as user_repo
from . import post as post_repo
from . import comment as comment_repo

__all__ = ["user_repo", "post_repo", "comment_repo"]