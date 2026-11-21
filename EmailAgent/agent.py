import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from tools import fetch_email_summaries, fetch_full_email

load_dotenv()
MODEL = os.getenv("MODEL_GROQ", "llama3-8b-8192")

@tool
def search_inbox(sender: str = None, keyword: str = None, unread_only: bool = False) -> str:
    """Searches the inbox for recent emails.
    Args:
        sender: specific email address or name to look for (optional).
        keyword: specific word to search for in the subject (optional).
        unread_only: True if looking ONLY for unread/new emails. False to include already read emails.
    Returns:
        A list of email IDs, senders, and subjects.
    """
    return fetch_email_summaries(sender, keyword, unread_only)

@tool
def read_email(email_id: str) -> str:
    """Provide an email ID to read the full context and body of that specific email."""
    return fetch_full_email(email_id)

# Update your tools list and the tool map
tools = [search_inbox, read_email]
tool_map = {t.name: t for t in tools}

system_prompt = """You are an AI Email Assistant. 
You can check the user's inbox and read specific emails to help them manage their communications.

CRITICAL INSTRUCTION FOR DRAFTING EMAILS:
If the user asks you to reply to an email OR compose a brand new email, you must draft the email directly in your response. 
You DO NOT have a tool to send emails. Instead, you must output your draft wrapped exactly in these tags so the system can catch it:

<DRAFT>
TO: example@email.com
SUBJECT: Your Subject Here
BODY:
Write the actual email body here.
</DRAFT>"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
])

# Bind the tools directly to the Groq model
llm = ChatGroq(model=MODEL).bind_tools(tools)
chain = prompt | llm

# We build our own executor loop to stream steps live to the UI
class email_agent_executor:
    @staticmethod
    def stream(inputs: dict):
        messages = inputs.get("chat_history", []).copy()
        
        for _ in range(5):
            ai_msg = chain.invoke({"chat_history": messages})
            messages.append(ai_msg)
            
            if not ai_msg.tool_calls:
                yield {"type": "final", "content": ai_msg.content}
                return
                
            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Yield the tool intent to the UI
                yield {"type": "tool_call", "name": tool_name, "args": tool_args}
                
                selected_tool = tool_map[tool_name]
                tool_output = selected_tool.invoke(tool_args)
                
                # Yield the completion status to the UI
                yield {"type": "tool_result", "name": tool_name}
                
                messages.append(ToolMessage(
                    content=str(tool_output), 
                    tool_call_id=tool_call["id"]
                ))
                
        yield {"type": "final", "content": "Agent stopped after reaching the maximum step limit."}