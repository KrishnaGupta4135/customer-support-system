import streamlit as st
import pandas as pd
from database import get_connection


def render_dashboard(user):

    # ---------------- SIDEBAR ----------------

    with st.sidebar:
        st.markdown("## 🧠 Cortex AI")
        if "page_nav" not in st.session_state:
            st.session_state.page_nav = "🏠 Dashboard"

        page = st.sidebar.radio(
            "Navigation",
            ["🏠 Dashboard", "⚙️ Settings"],
            index=["🏠 Dashboard","⚙️ Settings"].index(st.session_state.page_nav)
        )

        st.session_state.page_nav = page
        st.divider()
        st.subheader("Start AI Chat")

        if st.button("💬 Open Chat", use_container_width=True):
            st.switch_page("pages/chat.py")
        
        st.divider()

        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.session_state.token = None
            st.query_params.clear()
            st.rerun()

    # ---------------- PAGE ROUTING ----------------

    if page == "🏠 Dashboard":
        dashboard_home(user=user)

    elif page == "⚙️ Settings":
        settings_page(st.session_state.user)
        
# ---------------- DASHBOARD HOME ----------------

def dashboard_home(user):

    # ---------------- HEADER ----------------

    col1, col2 = st.columns([6,1])

    with col1:
        st.markdown(
            """
            <h1 style='margin-bottom:0'>🧠 Cortex AI</h1>
            <p style='color:#9ca3af'>Next-generation AI productivity platform</p>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
            width=55
        )
        st.caption(f"**{user['name']}**")

    st.divider()

    # ---------------- INTRO ----------------

    st.subheader("🚀 Welcome to Cortex AI")

    st.markdown(
        """
Cortex AI is an advanced **AI assistant platform** designed to bring together
multiple intelligent tools into a single powerful workspace.

The platform enables developers, researchers, and professionals to interact
with modern AI systems through a unified interface.

With Cortex AI you can connect **multiple MCP servers, AI tools,
and data sources** to build intelligent workflows.

The system is capable of handling **search, document reasoning,
video understanding, and knowledge retrieval** using modern LLM
and agentic architectures.

Our platform leverages technologies such as **LangGraph,
FastAPI services, and distributed AI tool integrations**
to deliver scalable AI solutions.

Cortex AI allows you to run **multi-step AI workflows,
automate complex tasks, and build powerful AI copilots**.

Whether you are exploring AI capabilities or building
production AI pipelines, Cortex AI provides the flexibility
and power needed for modern AI applications.
        """
    )

    st.divider()

    # ---------------- TOOL CARDS ----------------

    st.subheader("🧠 AI Tools")

    conn = get_connection()
    tools = conn.execute("SELECT * FROM tools").fetchall()

    images = [
        "https://cdn-icons-png.flaticon.com/512/3039/3039385.png",
        "https://cdn-icons-png.flaticon.com/512/4712/4712027.png",
        "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
        "https://cdn-icons-png.flaticon.com/512/4149/4149673.png"
    ]

    cols = st.columns(3)

    for i, tool in enumerate(tools):

        with cols[i % 3]:

            st.markdown(
                f"""
                <div style="
                padding:25px;
                border-radius:14px;
                background:#111827;
                border:1px solid #1f2937;
                text-align:center;
                margin-bottom:25px;
                transition:0.3s;
                box-shadow:0 6px 18px rgba(0,0,0,0.35);
                ">

                <img src="{images[i % len(images)]}" width="60">

                <h4 style="margin-top:12px;color:white">
                {tool['name']}
                </h4>

                <p style="color:#9ca3af;font-size:14px">
                {tool['description']}
                </p>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    # ---------------- PLATFORM FEATURES ----------------

    st.subheader("⚡ Platform Features")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/4149/4149673.png",
            width=100
        )
        st.markdown("### AI Search")
        st.caption("Search the internet using AI powered reasoning.")

    with c2:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/4248/4248443.png",
            width=100
        )
        st.markdown("### Document Intelligence")
        st.caption("Upload documents and ask questions with RAG.")

    with c3:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
            width=100
        )
        st.markdown("### Video Understanding")
        st.caption("Interact with YouTube and video content using AI.")

    st.divider()

    st.caption("© 2026 Cortex AI Platform")

# ---------------- SETTINGS PAGE ----------------

def settings_page(user):

    st.title("⚙️ Settings")

    st.markdown("Update your profile settings")

    st.write("Name:",user["name"])
    st.write("Email:",user["email"])

    theme = st.selectbox(
        "Theme",
        ["Dark", "Light"]
    )

    if st.button("Save Settings"):
        st.success("Settings saved")
        