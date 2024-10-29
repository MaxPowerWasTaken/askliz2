from typing import List, Dict, Any
import lancedb
from src.backend.config import N_RESULTS_RETRIEVED, N_RESULTS_PRESENTED, reranker, g_llm
from src.backend.llm import generate_response

def query_documents(tbl: lancedb.table,
                   query: str, 
                   num_results_retrieved: int = N_RESULTS_RETRIEVED,
                   num_results_presented: int = N_RESULTS_PRESENTED, 
                   source_file: str = None) -> List[Dict[str, Any]]:
    """Query the document database."""
    results = (tbl.search(query, query_type="hybrid")
               .limit(num_results_retrieved)
               .rerank(reranker=reranker)
               ).to_list()[:num_results_presented]

    final_response = generate_response(query, results, model=g_llm, debug=False)

    return final_response
