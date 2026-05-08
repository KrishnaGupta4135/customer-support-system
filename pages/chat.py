import uuid
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from langraph_rag_backend import (
    chatbot,
    ingest_pdf,
    retrieve_all_threads,
    thread_document_metadata,
)

# ---------------- PAGE CONFIG ----------------

st.set_page_config(page_title="Cortex AI Chat", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display:none;}
</style>
""", unsafe_allow_html=True)

# ================= URL → SESSION SYNC =================

params = st.query_params

if "token" in params:
    st.session_state["token"] = params["token"]

if "thread_id" in params:
    st.session_state["thread_id"] = params["thread_id"]

# ================= Utilities =================

def generate_thread_id():
    return str(uuid.uuid4())


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def reset_chat():

    if len(st.session_state.get("message_history", [])) == 0:
        return

    thread_id = generate_thread_id()

    st.session_state["thread_id"] = thread_id
    st.session_state["message_history"] = []

    add_thread(thread_id)

    st.query_params.update({
        "token": st.session_state.get("token"),
        "thread_id": thread_id
    })


def load_conversation(thread_id):

    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    return state.values.get("messages", [])


# ================= SESSION INIT =================

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}

# remove duplicates
st.session_state["chat_threads"] = list(dict.fromkeys(st.session_state["chat_threads"]))

add_thread(st.session_state["thread_id"])

thread_key = str(st.session_state["thread_id"])

st.query_params.update({
    "token": st.session_state.get("token"),
    "thread_id": thread_key
})

thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})

threads = [
    t for t in st.session_state["chat_threads"]
    if load_conversation(t)
][::-1]

selected_thread = None


# ================= SIDEBAR =================
if st.sidebar.button("⬅ Back to Dashboard"):
    st.switch_page("dashboard.py")
    
st.sidebar.markdown("## 🧠 Cortex AI")
st.sidebar.caption("AI powered knowledge & document assistant")

st.sidebar.divider()

if st.sidebar.button("➕ New Chat", use_container_width=True):
    reset_chat()
    st.rerun()

st.sidebar.divider()

# -------- PDF STATUS --------

if thread_docs:

    latest_doc = list(thread_docs.values())[-1]

    st.sidebar.success(
        f"📄 {latest_doc.get('filename')}\n\n"
        f"Chunks: {latest_doc.get('chunks')}\n"
        f"Pages: {latest_doc.get('documents')}"
    )

else:
    st.sidebar.info("No PDF indexed yet")

# -------- FILE UPLOAD --------

uploaded_pdf = st.sidebar.file_uploader(
    "Upload PDF for RAG",
    type=["pdf"]
)

if uploaded_pdf:

    if uploaded_pdf.name in thread_docs:
        st.sidebar.info(f"{uploaded_pdf.name} already indexed")

    else:

        with st.sidebar.status("Indexing document...", expanded=True) as status_box:

            summary = ingest_pdf(
                uploaded_pdf.getvalue(),
                thread_id=thread_key,
                filename=uploaded_pdf.name,
            )

            thread_docs[uploaded_pdf.name] = summary

            status_box.update(
                label="✅ Document Indexed",
                state="complete",
                expanded=False
            )

st.sidebar.divider()

# -------- CHAT HISTORY --------

st.sidebar.subheader("💬 Chat History")

if not threads:
    st.sidebar.write("No conversations yet")

else:

    for i, thread_id in enumerate(threads):

        if st.sidebar.button(
            f"Chat {thread_id[:8]}",
            key=f"thread-{thread_id}-{i}"
        ):
            selected_thread = thread_id
st.sidebar.divider()

with st.sidebar:
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.query_params.clear()
        st.switch_page("app.py")
        st.rerun()



# ================= MAIN UI =================

st.title("🧠 Cortex AI Chat")

st.caption(
    "Ask questions, analyze documents, and run AI tools using LangGraph agents."
)

# -------- CHAT HISTORY --------

for message in st.session_state["message_history"]:

    with st.chat_message(message["role"]):
        st.text(message["content"])


# -------- CHAT INPUT --------

user_input = st.chat_input(
    "Ask Cortex AI anything or query your documents..."
)

if user_input:

    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {
        "configurable": {"thread_id": thread_key},
        "metadata": {"thread_id": thread_key},
        "run_name": "chat_turn",
    }

    # ================= ASSISTANT RESPONSE =================

    with st.chat_message("assistant"):

        status_holder = {"box": None}

        def ai_stream():

            for message_chunk, _ in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):

                # TOOL STATUS
                if isinstance(message_chunk, ToolMessage):

                    tool_name = getattr(message_chunk, "name", "tool")

                    if status_holder["box"] is None:

                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}`...",
                            expanded=True
                        )

                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}`...",
                            state="running",
                            expanded=True,
                        )

                # STREAM RESPONSE
                if isinstance(message_chunk, AIMessage):

                    if message_chunk.content:
                        yield message_chunk.content

        with st.spinner("Thinking..."):

            ai_message = st.write_stream(ai_stream())

        if status_holder["box"] is not None:

            status_holder["box"].update(
                label="✅ Tool Finished",
                state="complete",
                expanded=False
            )

    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })

    doc_meta = thread_document_metadata(thread_key)

    if doc_meta:

        st.caption(
            f"📄 Document: {doc_meta.get('filename')} | "
            f"Chunks: {doc_meta.get('chunks')} | "
            f"Pages: {doc_meta.get('documents')}"
        )

st.divider()

# ================= THREAD SWITCH =================

if selected_thread:

    st.session_state["thread_id"] = selected_thread

    st.query_params.update({
        "token": st.session_state.get("token"),
        "thread_id": selected_thread
    })

    messages = load_conversation(selected_thread)

    temp_messages = []

    for msg in messages:

        role = "user" if isinstance(msg, HumanMessage) else "assistant"

        temp_messages.append({
            "role": role,
            "content": msg.content
        })

    st.session_state["message_history"] = temp_messages

    st.session_state["ingested_docs"].setdefault(selected_thread, {})

    st.rerun()