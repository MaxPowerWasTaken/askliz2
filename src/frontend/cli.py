import lancedb
import typer

from lancedb.pydantic import LanceModel
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from typing import List, Dict, Any, NamedTuple

from src.backend.main import query_documents
from src.backend.database.operations import get_or_setup_db
from src.backend.config import DB_PATH, N_RESULTS_RETRIEVED, N_RESULTS_PRESENTED

app = typer.Typer()
console = Console()

@app.command()
def query(
    query: str = typer.Argument(..., help="Your question or query"),
    reindex_docs: bool = typer.Option(False, help="Re-run document ingestion/chunking/indexing pipeline before querying")
):
    """Query the documents and get most-relevant passages."""

    ldb = lancedb.connect(DB_PATH)
    table = get_or_setup_db(reindex_docs)

    """Query the document database and get answers with citations."""
    response = query_documents(table, query, num_results_presented=num_results)
    console.print(Panel(response))
    return None

if __name__ == "__main__":
    app()
