import lancedb
from src.backend.config import DB_PATH, CORPUS_PATH, tokenizer
from src.backend.schemas import DocumentChunk, DocumentChunkLanceRecord
from src.backend.document_processor import get_document_chunks
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
        doc_chunks = [DocumentChunk(text=txt_chunk) for txt_chunk in txt_chunks]

        # Create or overwrite the table based on the mode
        tbl = ldb.create_table("document_chunks", schema=DocumentChunkLanceRecord, mode="overwrite")
        tbl.add(doc_chunks)
        tbl.create_fts_index("text", replace=True)

    return tbl
