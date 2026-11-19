import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- CONCEPT 1: Model Fallbacks (Resilience) ---
# If the main model fails or hits a rate limit, LCEL automatically reroutes to the fallback.
primary_llm = ChatGroq(model="openai/gpt-oss-20b")
fallback_llm = ChatGroq(model="llama3-8b-8192")
llm = primary_llm.with_fallbacks([fallback_llm])

HUMAN_STYLE = """Write like a person, not like an AI:
- Vary your sentence length. Some short. Others longer, with a clause that earns its place.
- Use contractions (it's, don't, you'll) and talk straight to the reader as "you".
- Replace vague claims with a concrete example, a number, or a small story.
- Having an opinion is fine. Saying "I" is fine.
- Never use these words and phrases: "in today's fast-paced world", "delve", "moreover",
  "furthermore", "unlock", "leverage", "robust", "seamless", "game-changer",
  "it's worth noting", "navigate the landscape", "at the end of the day".
- Do not start every section the same way.
- Only use a bullet list when the content really is a list. Prefer paragraphs.
- Do not end with a summary of what you just said. End with one useful thought."""

OUTLINE_PROMPT = ChatPromptTemplate.from_template(
    "Write a short outline for a blog post.\n\nTopic: {topic}\nTone: {tone}\n\nGive me:\n- one opening line that makes the reader curious\n- 4 section headings\n- 5 key points the post must cover\n\nJust the outline. Do not write the post."
)

DRAFT_PROMPT = ChatPromptTemplate.from_template(
    "Write a blog post from this outline.\n\n{outline}\n\n" + HUMAN_STYLE + "\n\nTone: {tone}\nOutput markdown, with the section headings as ###.\nMake it as long or as short as the topic actually needs."
)

POLISH_PROMPT = ChatPromptTemplate.from_template(
    "Improve this blog post without changing what it says.\n\n" + HUMAN_STYLE + "\n\nAlso:\n- add a good # title at the top\n- keep the markdown\n\nReply with the improved post only, no commentary.\n\n{draft}"
)

# --- CONCEPT 2: The Revision Chain ---
# A fourth chain to allow the user to tweak the final output
REVISION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an expert editor. Revise the provided blog post based strictly on the user's instructions. Keep the markdown formatting.\n\nCurrent Blog Post:\n{current_blog}"),
    ("user", "{instructions}")
])

outline_chain = OUTLINE_PROMPT | llm | StrOutputParser()
draft_chain = DRAFT_PROMPT | llm | StrOutputParser()
final_chain = POLISH_PROMPT | llm | StrOutputParser()
revision_chain = REVISION_PROMPT | llm | StrOutputParser()

## UI design 
st.subheader("📝✍️ AI BLOG GENERATOR")
st.caption("Outline --> Draft --> Polish. Three prompts, three chains.")

# --- CONCEPT 3: Session State (Memory) ---
# Streamlit reruns the script on every click. We must save the generated data in session_state so it survives the rerun.
if "final_blog" not in st.session_state:
    st.session_state.final_blog = None
    st.session_state.outline = None
    st.session_state.draft = None

topic = st.text_input("Blog Title", "Why we have to learn Gen-AI in 2026?")
tone = st.selectbox("Tone", ["direct", "normal", "friendly"])

import time # Add this to your imports at the top

if st.button("Generate", type="primary"):
    
    # 1. Instantiate the progress bar right above the thought process
    progress_bar = st.progress(0, text="Initializing Pipeline...")
    
    with st.status("🧠 AI Thought Process...", expanded=True) as status:
        
        # --- MILESTONE 1: OUTLINE ---
        progress_bar.progress(10, text="Milestone 1: Generating Outline...")
        st.write("📝 **Step 1: Outlining the structure...**")
        
        st.session_state.outline = outline_chain.invoke({"topic": topic, "tone": tone})
        st.info(st.session_state.outline)
        
        progress_bar.progress(33, text="Milestone 1 Complete!")
        
        # --- MILESTONE 2: DRAFT ---
        progress_bar.progress(50, text="Milestone 2: Drafting Content...")
        st.write("✍️ **Step 2: Drafting the initial content...**")
        
        st.session_state.draft = draft_chain.invoke({"outline": st.session_state.outline, "tone": tone})
        st.info(st.session_state.draft[:300] + "...\n\n*(Draft truncated for readability)*")
        
        progress_bar.progress(66, text="Milestone 2 Complete!")
        
        # --- MILESTONE 3: POLISH ---
        progress_bar.progress(85, text="Milestone 3: Polishing Final Blog...")
        st.write("✨ **Step 3: Polishing formatting and tone...**")
        
        st.session_state.final_blog = final_chain.invoke({"draft": st.session_state.draft})
        
        progress_bar.progress(100, text="✅ Pipeline Complete!")
        status.update(label="✅ Blog generation complete!", state="complete", expanded=False)
        
    # 2. Briefly pause so the user sees "100%", then delete the progress bar to declutter the UI
    time.sleep(1)
    progress_bar.empty()
    
    # The script will now continue down to render the final blog from st.session_state

# Only render the blog and revision UI if a blog has been generated
if st.session_state.final_blog:
    # UX Upgrade: Hide the intermediate steps in expanders to keep the UI clean
    with st.expander("📄 View AI Outline", expanded=False):
        st.markdown(st.session_state.outline)
    with st.expander("✍️ View First Draft", expanded=False):
        st.markdown(st.session_state.draft)
    
    # Display the final polished blog
    st.markdown(st.session_state.final_blog)
    
    with st.expander("Raw Blog (Markdown)", expanded=False):
        st.code(st.session_state.final_blog)
        
    st.divider()
    
    # The Revision Interface
    st.subheader("💬 Tweak the Output")
    st.caption("Ask the AI to change the tone, expand a section, or rewrite the intro.")
    
    if revision_instruction := st.chat_input("E.g., 'Make the introduction punchier'"):
        with st.spinner("Revising blog..."):
            # Pass the currently saved blog and the user's instructions to the revision chain
            updated_blog = revision_chain.invoke({
                "current_blog": st.session_state.final_blog,
                "instructions": revision_instruction
            })
            # Overwrite the old blog with the new one in session state
            st.session_state.final_blog = updated_blog
            # Force Streamlit to instantly redraw the screen with the new text
            st.rerun()