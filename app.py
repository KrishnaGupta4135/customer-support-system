import streamlit as st
from auth import authenticate_user, create_user
from dashboard import render_dashboard
from database import init_db
from pathlib import Path
from database import get_connection
import uuid
init_db()

st.set_page_config(
    page_title="Cortex AI",
    layout="wide",
)



    
# ---------------- SESSION INIT ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "login"

if "token" not in st.session_state:
    st.session_state.token = None


# ---------------- RESTORE TOKEN FROM URL ----------------

params = st.query_params

if "token" in params and st.session_state.token is None:
    st.session_state.token = params["token"]

if "token" in st.session_state:
    st.query_params["token"] = st.session_state.token


# ---------------- RESTORE USER FROM TOKEN ----------------

if st.session_state.token and st.session_state.user is None:

    conn = get_connection()

    session = conn.execute(
        """
        SELECT users.*
        FROM sessions
        JOIN users ON sessions.user_id = users.id
        WHERE sessions.session_token=?
        """,
        (st.session_state.token,)
    ).fetchone()

    if session:
        st.session_state.user = dict(session)
# ---------------- STYLE ----------------

if st.session_state.user is None:

    # LOGIN / SIGNUP PAGE (sidebar hidden)

    st.markdown("""
    <style>

    [data-testid="stSidebar"] {
        display: none;
    }
    .main {
        background: linear-gradient(135deg,#0f172a,#020617);
    }

    .auth-container{
        width:900px;
        margin:auto;
        margin-top:80px;
        display:flex;
        background:#111827;
        border-radius:12px;
        overflow:hidden;
        box-shadow:0px 10px 40px rgba(0,0,0,0.6);
    }

    .auth-left{
        width:50%;
        background:#1e293b;
        display:flex;
        align-items:center;
        justify-content:center;
    }

    .auth-right{
        width:50%;
        padding:40px;
    }

    .login-btn button{
        width:100%;
        background:#2563eb;
        color:white;
        border-radius:8px;
    }

    button[kind="secondary"] {
        border-radius:10px;
    }

    button[kind="primary"] {
        border-radius:10px;
    }

    .auth-left{
        width:50%;
        background-image: url("images/cortex.png");
        background-size: cover;
        background-position: center;
        position: relative;
    }

    .auth-left::after{
        content:"";
        position:absolute;
        inset:0;
        background: linear-gradient(
            90deg,
            rgba(2,6,23,0.8),
            rgba(2,6,23,0.4)
        );
    }

    </style>
    """, unsafe_allow_html=True)

else:

    # DASHBOARD PAGE (sidebar visible)

    st.markdown("""
    <style>

    .main {
        background: linear-gradient(135deg,#020617,#020617);
    }

    [data-testid="stSidebar"] {
        background:#020617;
        border-right:1px solid #1e293b;
    }
    [data-testid="stSidebarNav"] {
        display: none;
    }

    </style>
    """, unsafe_allow_html=True)


    
    
image_path = Path("images/cortex.png")

# ---------------- DASHBOARD ----------------

if st.session_state.user is not None:

    def logout():
        conn = get_connection()
        conn.execute(
            "DELETE FROM sessions WHERE session_token=?",
            (st.session_state.token,)
        )
        conn.commit()
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    render_dashboard(st.session_state.user)
    # st.button("Logout", on_click=logout)


# ---------------- AUTH PAGE ----------------

else:

    col1, col2 = st.columns([1,1])

    with col1:
        
        st.markdown("""
            <div style='position:relative;margin-top:40px'>
            <div style='position:absolute;inset:0;background:rgba(0,0,0,0.6)'></div>
            <div style='position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding-top:40px'>  
                <h2 style='color:white;text-align:center;padding:10px'>
                Welcome to Cortex AI Assistant<br/>
                Your Gateway to Powerful AI Tools
                </h2>
            </div>

            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top:30px'></div>", unsafe_allow_html=True)

        st.image(image_path)
    
    with col2:
        st.title("Cortex AI Assistant")
        st.divider()

        # Toggle buttons
        c1,c2 = st.columns(2)

        with c1:
            if st.button("Login",use_container_width=True):
                st.session_state.page="login"

        with c2:
            if st.button("Signup",use_container_width=True):
                st.session_state.page="signup"

        # st.divider()

        # LOGIN FORM
        if st.session_state.page == "login":

            st.subheader("Login")

            email = st.text_input("Email",key="login_email")
            password = st.text_input("Password",type="password",key="login_pass")

            if st.button("Login",key="login_btn"):

                user = authenticate_user(email,password)

                if user:
                    conn = get_connection()
                    token = str(uuid.uuid4())
                    conn.execute(
                        "INSERT INTO sessions (user_id, session_token) VALUES (?,?)",
                        (user["id"], token)
                    )
                    conn.commit()
                    st.session_state.user = dict(user)
                    st.session_state.token = token
                    st.query_params["token"] = token
                    st.rerun()
                else:
                    st.error("Invalid credentials")

            st.markdown(
                "Don't have an account? **Signup above**"
            )


        # SIGNUP FORM
        else:

            st.subheader("Create Account")

            name = st.text_input("Name",key="signup_name")
            email = st.text_input("Email",key="signup_email")
            password = st.text_input("Password",type="password",key="signup_pass")

            if st.button("Create account",key="signup_btn"):

                create_user(name,email,password)

                st.success("Account created")

                st.session_state.page="login"
                st.rerun()