"""
AI가 작성한 frontend 부분
"""
import httpx
import streamlit as st

API = "http://localhost:8000"


# ────────────────────────── API 래퍼 ──────────────────────────
def api_get(path: str):
    r = httpx.get(f"{API}{path}", timeout=120.0)
    return r.status_code, (r.json() if r.content else None)


def api_post(path: str, body: dict):
    r = httpx.post(f"{API}{path}", json=body, timeout=120.0)
    return r.status_code, (r.json() if r.content else None)


def api_patch(path: str, body: dict):
    r = httpx.patch(f"{API}{path}", json=body, timeout=120.0)
    return r.status_code, (r.json() if r.content else None)


def api_delete(path: str):
    r = httpx.delete(f"{API}{path}", timeout=120.0)
    return r.status_code, (r.json() if r.content else None)


def show_error(status: int, body):
    detail = body.get("detail") if isinstance(body, dict) else body
    st.error(f"[{status}] {detail}")


# ────────────────────────── 세션 상태 ──────────────────────────
def init_state():
    st.session_state.setdefault("current_user_id", None)
    st.session_state.setdefault("view", "board")          # board | post_detail | profile | signup
    st.session_state.setdefault("selected_post_id", None)


def get_current_user():
    uid = st.session_state.current_user_id
    if uid is None:
        return None
    status, body = api_get(f"/users/{uid}")
    return body if status == 200 else None


# ────────────────────────── 사이드바 ──────────────────────────
def sidebar():
    st.sidebar.title("📋 Community")

    # 현재 사용자 선택 (인증 없으니 ID 직접 입력으로 흉내)
    st.sidebar.markdown("### 👤 현재 사용자")
    uid_input = st.sidebar.number_input(
        "User ID", min_value=1, step=1,
        value=st.session_state.current_user_id or 1,
        key="uid_input",
    )
    if st.sidebar.button("로그인", use_container_width=True):
        status, body = api_get(f"/users/{uid_input}")
        if status == 200:
            st.session_state.current_user_id = uid_input
            st.session_state.view = "board"
            st.rerun()
        else:
            show_error(status, body)

    user = get_current_user()
    if user:
        st.sidebar.success(f"@{user['nickname']} ({user['email']})")
    else:
        st.sidebar.info("로그인 안 됨")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 메뉴")
    if st.sidebar.button("🏠 게시판", use_container_width=True):
        st.session_state.view = "board"; st.rerun()
    if st.sidebar.button("👤 내 정보", use_container_width=True, disabled=user is None):
        st.session_state.view = "profile"; st.rerun()
    if st.sidebar.button("✍️ 회원가입", use_container_width=True):
        st.session_state.view = "signup"; st.rerun()


# ────────────────────────── 페이지: 회원가입 ──────────────────────────
def view_signup():
    st.header("✍️ 회원가입")
    with st.form("signup_form"):
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        nickname = st.text_input("닉네임")
        submitted = st.form_submit_button("가입하기")
        if submitted:
            status, body = api_post("/users", {
                "email": email, "password": password, "nickname": nickname,
            })
            if status == 201:
                st.success(f"가입 완료! 부여된 ID: {body['id']}")
                st.session_state.current_user_id = body["id"]
                st.info("사이드바에서 ID로 로그인 상태가 됐어요.")
            else:
                show_error(status, body)


# ────────────────────────── 페이지: 내 정보 ──────────────────────────
def view_profile():
    user = get_current_user()
    if not user:
        st.warning("먼저 로그인해주세요.")
        return

    st.header(f"👤 @{user['nickname']}")
    st.write(f"📧 {user['email']}")
    st.write(f"🆔 {user['id']}")

    st.markdown("---")
    st.subheader("정보 수정")
    with st.form("update_form"):
        new_nick = st.text_input("새 닉네임", value=user["nickname"])
        new_pw = st.text_input("새 비밀번호 (변경 시에만)", type="password")
        if st.form_submit_button("수정"):
            payload = {}
            if new_nick != user["nickname"]:
                payload["nickname"] = new_nick
            if new_pw:
                payload["password"] = new_pw
            if not payload:
                st.info("변경 사항이 없어요.")
            else:
                status, body = api_patch(f"/users/{user['id']}", payload)
                if status == 200:
                    st.success("수정 완료")
                    st.rerun()
                else:
                    show_error(status, body)

    st.markdown("---")
    st.subheader("⚠️ 회원 탈퇴")
    if st.button("탈퇴하기", type="primary"):
        status, _ = api_delete(f"/users/{user['id']}")
        if status == 204:
            st.session_state.current_user_id = None
            st.session_state.view = "board"
            st.success("탈퇴 완료")
            st.rerun()
        else:
            show_error(status, _)


# ────────────────────────── 페이지: 게시판 ──────────────────────────
def view_board():
    st.header("🏠 게시판")

    user = get_current_user()
    if user:
        with st.expander("✍️ 새 글 작성", expanded=False):
            with st.form("post_form"):
                title = st.text_input("제목")
                content = st.text_area("내용", height=180)
                if st.form_submit_button("작성"):
                    if not title or not content:
                        st.warning("제목과 내용을 모두 입력해주세요.")
                    else:
                        with st.spinner("AI가 요약을 생성 중... (약 20초)"):
                            status, body = api_post("/posts", {
                                "author_id": user["id"],
                                "title": title, "content": content,
                            })
                        if status == 201:
                            st.success(f"작성 완료 (id={body['id']})")
                            st.rerun()
                        else:
                            show_error(status, body)
    else:
        st.info("글을 작성하려면 사이드바에서 로그인하세요.")

    st.markdown("---")
    status, posts = api_get("/posts")
    if status != 200:
        show_error(status, posts); return
    if not posts:
        st.info("아직 게시글이 없어요."); return

    for p in reversed(posts):
        with st.container(border=True):
            st.markdown(f"### {p['title']}")
            st.caption(f"작성자 #{p['author_id']} · 글 #{p['id']}")
            if p.get("summary"):
                st.markdown(f"🤖 **요약**: {p['summary']}")
            if st.button("자세히 보기 →", key=f"open_{p['id']}"):
                st.session_state.selected_post_id = p["id"]
                st.session_state.view = "post_detail"
                st.rerun()


# ────────────────────────── 페이지: 게시글 상세 ──────────────────────────
def view_post_detail():
    pid = st.session_state.selected_post_id
    if pid is None:
        st.session_state.view = "board"; st.rerun()

    status, post = api_get(f"/posts/{pid}")
    if status != 200:
        show_error(status, post)
        if st.button("← 게시판으로"):
            st.session_state.view = "board"; st.rerun()
        return

    user = get_current_user()
    is_owner = user and user["id"] == post["author_id"]

    if st.button("← 게시판으로"):
        st.session_state.view = "board"; st.rerun()

    st.header(post["title"])
    st.caption(f"작성자 #{post['author_id']} · 글 #{post['id']}")
    if post.get("summary"):
        st.info(f"🤖 **AI 요약**: {post['summary']}")
    st.markdown(post["content"])

    # 본인 글이면 수정·삭제 가능
    if is_owner:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("✏️ 수정"):
                with st.form("post_edit"):
                    new_title = st.text_input("제목", value=post["title"])
                    new_content = st.text_area("내용", value=post["content"], height=180)
                    if st.form_submit_button("저장"):
                        payload = {}
                        if new_title != post["title"]:
                            payload["title"] = new_title
                        if new_content != post["content"]:
                            payload["content"] = new_content
                        if not payload:
                            st.info("변경 없음")
                        else:
                            spinner_msg = "AI 요약 재생성 중..." if "content" in payload else "저장 중..."
                            with st.spinner(spinner_msg):
                                s, b = api_patch(f"/posts/{pid}", payload)
                            if s == 200:
                                st.success("수정 완료"); st.rerun()
                            else:
                                show_error(s, b)
        with col2:
            if st.button("🗑️ 삭제", type="primary"):
                s, b = api_delete(f"/posts/{pid}")
                if s == 204:
                    st.session_state.view = "board"; st.rerun()
                else:
                    show_error(s, b)

    # ────── 댓글 ──────
    st.markdown("---")
    st.subheader("💬 댓글")

    status, comments = api_get(f"/posts/{pid}/comments")
    if status == 200:
        if not comments:
            st.caption("아직 댓글이 없어요.")
        for c in comments:
            with st.container(border=True):
                cols = st.columns([5, 1])
                with cols[0]:
                    st.markdown(f"**#{c['author_id']}**: {c['content']}")
                    if c.get("summary"):
                        st.caption(f"🤖 {c['summary']}")
                with cols[1]:
                    if user and user["id"] == c["author_id"]:
                        if st.button("삭제", key=f"del_{c['id']}"):
                            s, b = api_delete(f"/posts/{pid}/comments/{c['id']}")
                            if s == 204:
                                st.rerun()
                            else:
                                show_error(s, b)
    else:
        show_error(status, comments)

    if user:
        with st.form("comment_form", clear_on_submit=True):
            new_comment = st.text_area("댓글 작성", height=80)
            if st.form_submit_button("등록"):
                if not new_comment.strip():
                    st.warning("내용을 입력해주세요.")
                else:
                    with st.spinner("AI가 요약 생성 중..."):
                        s, b = api_post(f"/posts/{pid}/comments", {
                            "author_id": user["id"],
                            "content": new_comment,
                        })
                    if s == 201:
                        st.rerun()
                    else:
                        show_error(s, b)
    else:
        st.info("댓글을 달려면 사이드바에서 로그인하세요.")


# ────────────────────────── 메인 ──────────────────────────
def main():
    st.set_page_config(page_title="Community Board", layout="wide")
    init_state()
    sidebar()

    view = st.session_state.view
    if view == "signup":
        view_signup()
    elif view == "profile":
        view_profile()
    elif view == "post_detail":
        view_post_detail()
    else:
        view_board()


if __name__ == "__main__":
    main()
