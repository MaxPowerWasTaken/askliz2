import lancedb

from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from lancedb.rerankers import  CrossEncoderReranker
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Dict, Any

from src.backend.config import embedding_model, tokenizer, reranker, CORPUS_PATH, DB_PATH
from src.backend.document_processor import get_document_chunks

# Our Data Model/Schema for the document chunks we'll store in our db
class DocumentChunkTxtInput(LanceModel):
    text: str

class DocumentChunkLanceRecord(LanceModel):
    text: str = embedding_model.SourceField()
    vector: Vector(embedding_model.ndims()) = embedding_model.VectorField()

class ChatResponse(LanceModel):
    text: str
    relevance_score: float

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

def query_documents(tbl: lancedb.table,
                    query: str, 
                    num_results_retrieved: int = 10,
                    num_results_presented: int = 3, 
                    source_file: str = None) -> List[Dict[str, Any]]:
    """Query the document database."""
    results = (tbl.search(query, query_type="hybrid")
               .limit(num_results_retrieved)  # Retrieve more initially for reranking
               .rerank(reranker=reranker)
               )
    # TODO: implement source_file filtering (first source_file needs to be added as attribute to DocChunk Schema)

    return results.to_list()[:num_results_presented]

def chat_with_documents(tbl:lancedb.table, context: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Chat function using the document database."""
    user_query = context[-1]["content"]
    response = query_documents(tbl, user_query, num_results_presented=1)[0]  # Simplify to 1 response per chat turn
    return ChatResponse(text=response['text'], relevance_score=response["_relevance_score"])
