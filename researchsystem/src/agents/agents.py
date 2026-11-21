import os
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search, scrape_web
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model=os.getenv("MODEL_GROQ"), temperature=0)

def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
    )



def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_web],
    )

# writer prompt and chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Critic Feedback to Apply (if any):
{feedback}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])
writer_chain = writer_prompt | llm | StrOutputParser()



# critic prompt
critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below strictly.

Report:
{report}

Respond in this exact format:
Strengths:
- ...
Areas to Improve:
- ...
Verdict: [PASS or FAIL]
"""),
])
critic_chain = critic_prompt | llm | StrOutputParser()