# Community Board — API Design
## 자원(Resource)
- `users` — 사용자
- `posts` — 게시글
  - `comments` — 댓글
## 엔드포인트
- 기능
- 메서드
- 경로
- 요청 본문(내용)
- 응답
### 사용자
| 기능 | 메서드 | 경로 | 요청 본문 | 응답 |
|---|---|---|---|---|
| 회원 가입 | `POST` | `/users` | 이메일(ID), 비밀번호, 닉네임 | `201` |
| 조회 | `GET` | `/users/{user_id}` | - | `200` |
| 수정 | `PATCH` | `/users/{user_id}` | 새로운 {비밀번호, 닉네임} | `200` |
| 회원 탈퇴 | `DELETE` | `/users/{user_id}` | - | `204` |
### 게시글
| 기능 | 메서드 | 경로 | 요청 본문 | 응답 |
|---|---|---|---|---|
| 전체 조회 | `GET` | `/posts` | - | `200` |
| 생성 | `POST` | `/posts` | 사용자 ID, 제목, 내용 | `201` |
| 조회 | `GET` | `/posts/{post_id}` | - | `200` |
| 수정 | `PATCH` | `/posts/{post_id}` | 제목, 내용 | `200` |
| 삭제 | `DELETE` | `/posts/{post_id}` | - | `204` |
<!-- | AI 요약 | `POST` | `/posts/{post_id}/summary` |  -->
### 댓글
| 기능 | 메서드 | 경로 | 요청 본문 | 응답 |
|---|---|---|---|---|
| 전체 조회 | `GET` | `/posts/{post_id}/comments` | - | `200` |
| 생성 | `POST` | `/posts/{post_id}/comments` | 사용자 ID, 내용 | `201` |
| 조회 | `GET` | `/posts/{post_id}/comments/{comment_id}` | - | `200` |
| 삭제 | `DELETE` | `/posts/{post_id}/comments/{comment_id}` | - | `204` |