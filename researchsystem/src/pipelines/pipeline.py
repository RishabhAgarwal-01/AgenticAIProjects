from tenacity import retry, wait_exponential, stop_after_attempt
from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

@retry(wait=wait_exponential(multiplier=2, min=5, max=20), stop=stop_after_attempt(4), reraise=True)
def invoke_with_retry(agent, payload, yield_func=None, step_name=""):
    try:
        return agent.invoke(payload)
    except Exception as e:
        if yield_func:
            yield_func({"step": step_name, "status": "info", "message": f"⚠️ API Error / Rate limit hit. Waiting to retry..."})
        raise e

def extract_langgraph_response(result_state, fallback_text):
    """Safely extracts text from a LangGraph state dictionary."""
    if "messages" in result_state and result_state["messages"]:
        content = result_state["messages"][-1].content
        if content.strip():
            return content
            
        # Fallback: If the LLM didn't synthesize a final response, grab the raw tool outputs
        tool_msgs = [m.content for m in result_state["messages"] if m.type == "tool"]
        if tool_msgs:
            return "\n\n".join(tool_msgs)
            
    return fallback_text


def run_research_pipeline(topic: str):
    
    # ── Step 1: Search ──
    yield {"step": "search", "status": "running"}
    yield {"step": "search", "status": "info", "message": f"Thinking: Formulating search query for '{topic}'..."}
    
    search_agent = build_search_agent()
    
    sr = invoke_with_retry(search_agent, {
        "messages": [("user", f"Find recent, reliable information about: {topic}. Ensure you list the URLs.")] 
    })
    
    search_content = extract_langgraph_response(sr, "No data found.")
        
    yield {"step": "search", "status": "info", "message": f"Observation: Received search results. Moving to Reader."}
    yield {"step": "search", "status": "done", "data": search_content}

    # ── Step 2: Reader ──
    yield {"step": "reader", "status": "running"}
    yield {"step": "reader", "status": "info", "message": "Thinking: Analyzing search results to find the best URL..."}
    
    reader_agent = build_reader_agent()
    safe_search_results = search_content[:3000]
    
    rr = invoke_with_retry(reader_agent, {
        "messages": [(
            "user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\nSearch Results:\n{safe_search_results}"
        )]
    })
    
    reader_content = extract_langgraph_response(rr, "No data scraped.")
        
    yield {"step": "reader", "status": "info", "message": "Observation: Scraping successful. Data extracted."}
    yield {"step": "reader", "status": "done", "data": reader_content}

    # ── Prepare Combined Research ──
    safe_scraped_content = reader_content[:4000]
    research_combined = f"SEARCH RESULTS:\n{safe_search_results}\n\nSCRAPED CONTENT:\n{safe_scraped_content}"

    # ── Step 3 & 4: Writer/Critic Loop ──
    max_revisions = 3
    current_attempt = 1
    passed = False
    current_feedback = "None yet - this is the first draft."
    final_report, final_critic = "", ""

    while current_attempt <= max_revisions and not passed:
        yield {"step": "writer", "status": "running", "attempt": current_attempt}
        yield {"step": "writer", "status": "info", "message": f"Thinking: Drafting report structure (Attempt {current_attempt})..."}
        
        final_report = invoke_with_retry(writer_chain, {"topic": topic, "research": research_combined, "feedback": current_feedback})
        
        yield {"step": "writer", "status": "info", "message": f"Action: Draft {current_attempt} complete. Sending to Critic."}
        yield {"step": "writer", "status": "done", "data": final_report}

        yield {"step": "critic", "status": "running", "attempt": current_attempt}
        yield {"step": "critic", "status": "info", "message": f"Thinking: Evaluating draft against quality standards..."}
        
        final_critic = invoke_with_retry(critic_chain, {"report": final_report})
        
        if "Verdict: PASS" in final_critic.upper() or "VERDICT: PASS" in final_critic.upper():
            yield {"step": "critic", "status": "info", "message": "Observation: Report passed quality check."}
            passed = True
        else:
            yield {"step": "critic", "status": "info", "message": f"Observation: Draft rejected. Sending feedback to writer."}
            current_attempt += 1
            current_feedback = final_critic
            
        yield {"step": "critic", "status": "done", "data": final_critic}

    yield {"step": "complete"}