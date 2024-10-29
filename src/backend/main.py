import lancedb

from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from lancedb.rerankers import  CrossEncoderReranker
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Dict, Any

from src.backend.config import embedding_model, tokenizer, reranker, g_llm, CORPUS_PATH, DB_PATH
from src.backend.document_processor import get_document_chunks

# Our Data Model/Schema for the document chunks we'll store in our db
class DocumentChunkTxtInput(LanceModel):
    text: str

class DocumentChunkLanceRecord(LanceModel):
    text: str = embedding_model.SourceField()
    vector: Vector(embedding_model.ndims()) = embedding_model.VectorField()


def get_or_setup_db(reindex:bool = False):
    """Prepares the document database by chunking and storing documents."""
    ldb = lancedb.connect(DB_PATH)
    if not reindex:
        tbl = ldb.open_table("document_chunks")
    else:
        txt_chunks = get_document_chunks(
            CORPUS_PATH,
            tokenizer,
            txt_parsing_eng='unstructuredio',
            txt_chunking_alg='default',
            chunk_len_tok=500,
            chunk_frac_overlap=0.2
        )
        doc_chunks = [DocumentChunkTxtInput(text=txt_chunk) for txt_chunk in txt_chunks]

        # Create or overwrite the table based on the mode
        tbl = ldb.create_table("document_chunks", schema=DocumentChunkLanceRecord, mode="overwrite")
        tbl.add(doc_chunks)
        tbl.create_fts_index("text", replace=True)

    return tbl


def craft_llm_response(query: str, reranked_results: List[Dict[str, Any]], debug=False) -> str:
    """
    Generate a response using the Gemini LLM based on the query and retrieved context.
    
    Parameters:
    -----------
    query : str
        The user's original question
    reranked_results : List[Dict[str, Any]]
        The reranked results from the vector database
        
    Returns:
    --------
    str : The generated response from the LLM
    """
    # Prepare the context from reranked results
    context = "\n\n".join([f"Context {i+1}:\n{result['text']}" 
                          for i, result in enumerate(reranked_results)])
    
    # Construct the prompt
    prompt = f"""Based on the following context, please answer the question. 
    Use only the information provided in the context. If you cannot answer the question 
    based on the context alone, please say so. The context will not be shown to the user,
    so do not say things like 'based on the provided context', but please do feel free to 
    quote from the context, or characterize it and then include a foot-note like [1] ...
    [1]..."quote a relevant passage from one of the chunks of context"

    Context:
    {context}

    Question: {query}

    Answer:"""
    if debug:
        print(f"FULL PROMPT SUBMITTED TO FINAL LLM:\n\n{prompt}")

    # Generate response
    response = g_llm.generate_content(prompt)
    
    return response.text

def query_documents(tbl: lancedb.table,
                    query: str, 
                    num_results_retrieved: int = 10,
                    num_results_presented: int = 3, 
                    source_file: str = None) -> List[Dict[str, Any]]:
    """Query the document database."""
    results = (tbl.search(query, query_type="hybrid")
               .limit(num_results_retrieved)  # Retrieve more initially for reranking
               .rerank(reranker=reranker)
               ).to_list()[:num_results_presented]

    final_response = craft_llm_response(query, results, debug=False)

    return final_response

def chat_with_documents(tbl:lancedb.table, context: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Chat function using the document database."""
    user_query = context[-1]["content"]
    response = query_documents(tbl, user_query, num_results_presented=1)[0]  # Simplify to 1 response per chat turn
    return response
