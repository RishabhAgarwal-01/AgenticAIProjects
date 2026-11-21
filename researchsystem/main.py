import re
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from dotenv import load_dotenv

# Import your agent builders and chains
from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

load_dotenv()
console = Console()

def run_cli_pipeline(topic: str):
    console.print(Panel.fit(f"[bold cyan]Research Topic:[/bold cyan] {topic}", border_style="cyan"))
    
    # ── Step 1: Search ──
    with console.status("[bold blue]🔍 Search Agent is scouring the web...", spinner="dots"):
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}. Ensure you list the URLs.")]
        })
        search_content = search_result['messages'][-1].content
        
    console.print("[bold green]✓ Search complete.[/bold green]")
    # Uncomment to debug raw search: console.print(search_content)

    # ── Step 2: Reader ──
    with console.status("[bold blue]📄 Reader Agent is scraping the top resource...", spinner="dots"):
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [(
                "user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{search_content}"
            )]
        })
        scraped_content = reader_result['messages'][-1].content

    console.print("[bold green]✓ Scraping complete.[/bold green]")
    
    # Combine research context
    research_combined = (
        f"SEARCH RESULTS:\n{search_content}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{scraped_content}"
    )

    # ── Step 3 & 4: Writer/Critic Loop ──
    max_revisions = 3
    current_attempt = 1
    passed = False
    current_feedback = "None yet - this is the first draft."
    final_report = ""

    while current_attempt <= max_revisions and not passed:
        console.print(f"\n[bold magenta]--- Drafting Attempt {current_attempt} ---[/bold magenta]")
        
        # Writer
        with console.status("[bold magenta]✍️ Writer is drafting the report...", spinner="bouncingBar"):
            final_report = writer_chain.invoke({
                "topic": topic,
                "research": research_combined,
                "feedback": current_feedback
            })
        console.print("[bold green]✓ Draft completed.[/bold green]")

        # Critic
        with console.status("[bold yellow]🧐 Critic is reviewing the draft...", spinner="bouncingBar"):
            current_feedback = critic_chain.invoke({
                "report": final_report
            })
        
        # Parse Critic Score
        score_match = re.search(r"Score:\s*(\d+)/10", current_feedback)
        if score_match:
            score = int(score_match.group(1))
            console.print(f"[bold yellow]Critic Score:[/bold yellow] {score}/10")
            
            if score >= 8:
                console.print("[bold green]✅ Report passed quality check![/bold green]")
                passed = True
            else:
                console.print(f"[bold red]⚠️ Score too low. Sending feedback back to Writer...[/bold red]")
                console.print(Panel(current_feedback, title="Critic Feedback", border_style="red"))
                current_attempt += 1
        else:
            console.print("[bold yellow]⚠️ Could not parse a numeric score from critic. Approving current draft to prevent infinite loop.[/bold yellow]")
            passed = True

    # ── Final Output ──
    console.print("\n[bold cyan]================ FINAL REPORT ================[/bold cyan]\n")
    console.print(Markdown(final_report))
    
    # Optional: Save to file automatically
    filename = f"research_report_{topic.replace(' ', '_')[:20]}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_report)
    console.print(f"\n[bold green]💾 Saved to {filename}[/bold green]")


if __name__ == "__main__":
    console.rule("[bold cyan]Agentic AI Research System[/bold cyan]")
    user_topic = Prompt.ask("\n[bold white]Enter a topic to research[/bold white]")
    
    if user_topic.strip():
        start_time = time.time()
        run_cli_pipeline(user_topic)
        end_time = time.time()
        console.print(f"\n[dim]Pipeline finished in {end_time - start_time:.2f} seconds.[/dim]")
    else:
        console.print("[bold red]Topic cannot be empty. Exiting.[/bold red]")