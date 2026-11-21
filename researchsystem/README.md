LangChain Multi-Agent Research System
A powerful multi-agent research system built with LangChain that autonomously researches topics, gathers information, writes comprehensive reports, and evaluates their quality using AI-powered agents.

🔬 Research Automation • 🤖 Multi-Agent Orchestration • 📝 Intelligent Report Generation

🌟 Features
Multi-Agent Architecture: Specialized agents for searching, reading, writing, and critiquing
Automated Web Research: Intelligent web search with Tavily API
Smart Content Extraction: Advanced web scraping with multiple fallback strategies
AI-Powered Report Generation: Automatically generates structured research reports
Quality Evaluation: Built-in critic agent for report validation and scoring
Interactive UI: Streamlit-based user interface for easy interaction
Pipeline Orchestration: Seamless coordination of multiple agents
🏗️ Architecture
┌─────────────────────────────────────────────────────┐
│           Streamlit UI (app.py)                     │
│      Multi-Agent Research Assistant Interface       │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│      Research Pipeline (pipeline.py)                │
│        Orchestrates multi-agent workflow            │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐    ┌────▼─────┐   ┌───▼────┐
│Search │    │   Reader  │   │ Writer │
│Agent  │    │   Agent   │   │ Chain  │
└───┬───┘    └────┬─────┘   └───┬────┘
    │             │             │
    │  ┌──────────▼─────────┐   │
    └─▶│  Tools Layer       │◀──┘
       │                    │
       │ • web_search      │
       │ • scrape_url      │
       │                    │
       └────────┬───────────┘
                │
            ┌───▼────────┐
            │ Critic     │
            │ Chain      │
            └────────────┘
Agent Responsibilities
Search Agent: Discovers relevant information across the web using Tavily
Reader Agent: Extracts clean, readable content from URLs
Writer Chain: Composes structured, professional research reports
Critic Chain: Evaluates reports and provides improvement suggestions
🛠️ Technologies Used
Technology	Purpose
LangChain	Multi-agent orchestration and chain management
OpenAI GPT-4o-mini	Language model for agents and chains
Streamlit	Interactive web UI
Tavily API	Web search and information retrieval
BeautifulSoup4	HTML parsing and content extraction
Trafilatura	Web content extraction
Readability-lxml	Article content extraction
Python-dotenv	Environment configuration management
Rich	Terminal output formatting