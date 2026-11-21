import uuid
import streamlit as st
from agent import get_agent

# 1. Page Configuration
st.set_page_config(page_title="Weather & Search Agent", page_icon="🌤️")
st.title("🌤️ Weather & Search Agent")
st.caption("A LangGraph agent equipped with Google Search and Weather tools.")

# 2. Initialize the Agent (Cached so the InMemorySaver persists across UI reruns)
@st.cache_resource
def init_agent():
    return get_agent()

agent = init_agent()

# 3. Initialize Session State for Memory and UI
# We need a unique thread_id per user session for LangGraph's checkpointer
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# We keep a list of messages just to render the chat bubbles on the screen
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Draw the Chat History on the Screen
for msg in st.session_state.messages:
    # Filter out tool-call data so the UI only shows clean User vs AI messages
    if msg["role"] in ["user", "assistant"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 5. Handle New User Input
if prompt := st.chat_input("Ask about the weather or search the web..."):
    
    # Display the user's prompt instantly
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Setup the AI's response container
    with st.chat_message("assistant"):
        
        # Use an expanding status container to hide the raw tool logs
        with st.status("🧠 Agent is thinking...", expanded=True) as status:
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            final_answer = ""
            
            # Stream the LangGraph execution exactly like the terminal version
            for event in agent.stream({"messages": [{"role": "user", "content": prompt}]}, config=config, stream_mode="updates"):
                
                for node_name, node_state in event.items():
                    latest_message = node_state["messages"][-1]
                    
                    # A. Did the AI call a tool?
                    if hasattr(latest_message, "tool_calls") and latest_message.tool_calls:
                        for tool in latest_message.tool_calls:
                            st.write(f"🛠️ **Calling Tool:** `{tool['name']}`")
                            st.write(f"📥 **Inputs:** `{tool['args']}`")
                    
                    # B. Did the tool finish executing?
                    elif latest_message.type == "tool":
                        st.write(f"✅ **Tool Success:** Fetched data using `{latest_message.name}`")
                        
                    # C. Did the AI generate the final text?
                    elif latest_message.type == "ai" and latest_message.content:
                        final_answer = latest_message.content
            
            # Close the status container once the agent finishes
            status.update(label="✅ Agent finished thinking!", state="complete", expanded=False)
        
        # Render the final answer outside the status box so it's easy to read
        st.markdown(final_answer)
        
        # Save the final answer to session state to survive reruns
        st.session_state.messages.append({"role": "assistant", "content": final_answer})