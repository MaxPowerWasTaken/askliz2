import lancedb
import typer

from lancedb.pydantic import LanceModel
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from typing import List, Dict, Any, NamedTuple

from src.backend.main import query_documents, chat_with_documents, get_or_setup_db
from src.backend.config import DB_PATH

app = typer.Typer()
console = Console()

"""
class Result(NamedTuple):
    explanation: str
    source: str
    quote: str
"""

class ChatResponse(LanceModel):
    text: str
    relevance_score: float

@app.command()
def query(
    query: str = typer.Argument(..., help="Your question or query"),
    num_results: int = typer.Option(3, help="Number of results to return"),
    source_file: str = typer.Option(None, help="Specific file to query from"),
    reindex_docs: bool = typer.Option(False, help="Re-run document ingestion/chunking/indexing pipeline before querying")
):
    """Query the documents and get most-relevant passages."""

    ldb = lancedb.connect(DB_PATH)
    table = get_or_setup_db(reindex_docs)

    """Query the document database and get answers with citations."""
    response = query_documents(table, query, num_results, source_file)
    console.print(Panel(response))

@app.command()
def chat():
    """Start an interactive chat session with the document database."""
    ldb = lancedb.connect(DB_PATH)
    table = get_or_setup_db(reindex=False)

    history = InMemoryHistory()
    context: List[Dict[str, str]] = []
    
    console.print("[bold]Welcome to the document chat. Type 'exit' or 'quit' to quit.[/bold]")
    
    while True:
        user_input = prompt("You: ", history=history)
        if user_input.lower() in ['exit', 'quit']:
            break
        
        context.append({"role": "user", "content": user_input})
        resp = chat_with_documents(table, context)
        display_chat_response(resp)
        
        context.append({"role": "assistant", "content": resp.text})
        
        if len(context) > 10:
            context = context[-10:]

def display_query_results(results: List[Dict[str, Any]]):
    for result in results:
        console.print(Panel(f"[bold]Relevance Score: {result['_relevance_score']}[/bold]\n\n{result['text']}"))
def display_chat_response(resp: ChatResponse):
    console.print(Panel(f"[bold]Relevance Score: {resp.relevance_score}[/bold]\n\n{resp.text}"))


if __name__ == "__main__":
    app()
