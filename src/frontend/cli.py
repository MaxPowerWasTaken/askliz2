import typer
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from typing import List, Dict, NamedTuple
from src.backend.main import query as backend_query, chat as backend_chat

app = typer.Typer()
console = Console()

class Result(NamedTuple):
    explanation: str
    source: str
    quote: str

@app.command()
def query(
    query: str = typer.Argument(..., help="Your question or query"),
    num_results: int = typer.Option(3, help="Number of results to return"),
    source_file: str = typer.Option(None, help="Specific file to query from")
):
    """Query the document database and get answers with citations."""
    results = backend_query(query, num_results, source_file)
    display_results(results)

@app.command()
def chat():
    """Start an interactive chat session with the document database."""
    history = InMemoryHistory()
    context: List[Dict[str, str]] = []
    
    console.print("[bold]Welcome to the document chat. Type 'exit' to quit.[/bold]")
    
    while True:
        user_input = prompt("You: ", history=history)
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break
        
        context.append({"role": "user", "content": user_input})
        results = backend_chat(context)
        display_results(results)
        
        for result in results:
            context.append({"role": "assistant", "content": result['explanation']})
        
        if len(context) > 10:
            context = context[-10:]

def display_results(results: List[Dict[str, Any]]):
    for result in results:
        console.print(Panel(f"[bold]{result['explanation']}[/bold]\n\nSource: {result['source']}\nQuote: {result['quote']}"))

if __name__ == "__main__":
    app()
