import streamlit as st
import re
from langchain_core.messages import HumanMessage, AIMessage
from agent import email_agent_executor
from tools import send_email_smtp

st.set_page_config(page_title="Conversational Email Agent", page_icon="💬", layout="wide")
st.title("💬 Conversational Email Agent")

# Initialize Chat Memory and Draft State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_draft" not in st.session_state:
    st.session_state.pending_draft = None

# Render Chat History
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# Render Pending Draft Approval UI
if st.session_state.pending_draft:
    draft = st.session_state.pending_draft
    st.warning("⚠️ **Review Pending Email Draft**")
    
    with st.form("draft_review_form"):
        to_address = st.text_input("To:", value=draft.get("TO", ""))
        subject = st.text_input("Subject:", value=draft.get("SUBJECT", ""))
        body = st.text_area("Body:", value=draft.get("BODY", "").strip(), height=200)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Approve & Send", use_container_width=True)
        with col2:
            reject = st.form_submit_button("❌ Reject", use_container_width=True)
            
        if submit:
            with st.spinner("Sending email..."):
                result = send_email_smtp(to_address, subject, body)
            st.success(result)
            st.session_state.pending_draft = None
            st.rerun()
            
        if reject:
            st.info("Draft discarded.")
            st.session_state.pending_draft = None
            st.rerun()

# Handle New User Input
if prompt := st.chat_input("Ask me to check your inbox or draft an email..."):
    if st.session_state.pending_draft:
        st.error("Please approve or reject the pending draft first.")
        st.stop()
        
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        output_text = ""
        
        # Live streaming status container
        with st.status("🧠 Agent thinking...", expanded=True) as status:
            for chunk in email_agent_executor.stream({"chat_history": st.session_state.messages}):
                if chunk["type"] == "tool_call":
                    status.write(f"🛠️ **Executing Tool:** `{chunk['name']}`")
                    status.write(f"📥 **Input:** `{chunk['args']}`")
                elif chunk["type"] == "tool_result":
                    status.write(f"✅ **Result received from:** `{chunk['name']}`")
                elif chunk["type"] == "final":
                    status.update(label="Task completed!", state="complete", expanded=False)
                    output_text = chunk["content"]
        
        # Intercept the draft tag
        draft_match = re.search(r"<DRAFT>\s*TO:\s*(.*?)\s*SUBJECT:\s*(.*?)\s*BODY:\s*(.*?)</DRAFT>", output_text, re.DOTALL)
        
        if draft_match:
            st.session_state.pending_draft = {
                "TO": draft_match.group(1).strip(),
                "SUBJECT": draft_match.group(2).strip(),
                "BODY": draft_match.group(3).strip()
            }
            display_text = output_text.replace(draft_match.group(0), "\n*I have prepared a draft for your review below.*")
        else:
            display_text = output_text

        st.markdown(display_text)
        st.session_state.messages.append(AIMessage(content=display_text))
        
        if draft_match:
            st.rerun() # Force a UI refresh to show the approval form