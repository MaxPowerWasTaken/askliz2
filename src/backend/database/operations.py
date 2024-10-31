import lancedb
from src.backend.config import ldb_conn, CORPUS_PATH, tokenizer
from src.backend.schemas import DocumentChunk, DocumentChunkLanceRecord
from src.backend.document_processor import get_document_chunks
def get_or_setup_db(tblname:str="document_chunks", reindex:bool = False)->lancedb.table:
    """Prepares the document database by chunking and storing documents."""
    if not reindex and tblname in list(ldb_conn.table_names()):
        print(f"returning already-existing lancedb table {tblname}")
        tbl = ldb_conn.open_table(tblname)
    else:
        print("chunking document and writing to lancedb")
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
        tbl = ldb_conn.create_table(tblname, schema=DocumentChunkLanceRecord, mode="overwrite")
        tbl.add(doc_chunks)
        tbl.create_fts_index("text", replace=True)

    return tbl
