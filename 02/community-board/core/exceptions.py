"""HTTP와 무관한 도메인 에러들"""

class DomainError(Exception):
    """모든 도메인 에러의 super class"""
    pass

# 사용자 관련 에러
class UserNotFound(DomainError):
    pass

class EmailAlreadyExists(DomainError):
    pass

# 게시글 관련 에러
class PostNotFound(DomainError):
    pass

# 댓글 관련 에러
class CommentNotFound(DomainError):
    pass

class CommentNotInPost(DomainError):
    pass