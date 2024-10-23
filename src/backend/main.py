import lancedb

from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from lancedb.rerankers import  CrossEncoderReranker
from sentence_transformers import SentenceTransformer
from pathlib import Path

from src.backend.document_processor import get_document_chunks

# CONFIG
EMBEDDING_MODEL = ("sentence-transformers", "BAAI/bge-small-en-v1.5")
N_RESULTS_RETRIEVED = 10
N_RETRIEVED_RESULTS_PRESENTED = 3
QUERY = "What were some of the key revelations from Cassidy Hutchinson?"

# Load the bi-encoder embedding model
embedding_model = get_registry().get(EMBEDDING_MODEL[0]).create(name=EMBEDDING_MODEL[1])

# Our Data Model/Schema for the document chunks we'll store in our db
class DocumentChunkTxtInput(LanceModel):
    text: str

class DocumentChunkLanceRecord(LanceModel):
    text: str = embedding_model.SourceField()
    vector: Vector(embedding_model.ndims()) = embedding_model.VectorField()

# Get DocumentChunks for our document(s)
tokenizer = SentenceTransformer(EMBEDDING_MODEL[1]).tokenizer
txt_chunks = get_document_chunks("corpus/j6c_final_report/FINAL_REPORT.html", 
                                 tokenizer, txt_parsing_eng='unstructuredio', 
                                 txt_chunking_alg='default', 
                                 chunk_len_tok=500,
                                 chunk_frac_overlap=0.2)

doc_chunks = [DocumentChunkTxtInput(text=txt_chunk) for txt_chunk in txt_chunks]

# load db
db = lancedb.connect("src/backend/lancedb")
tbl = db.create_table("document_chunks", schema=DocumentChunkLanceRecord, mode="overwrite")

# Embed the documents and store them in the db
tbl.add(doc_chunks)

# Generate the full-text (tf-idf) search index
tbl.create_fts_index("text", replace=True)

# Initialize the cross-encoder reranker
reranker = CrossEncoderReranker()

# Query the documents
results = (tbl.search(QUERY, query_type="hybrid")
            #.where("category = 'some_category'", prefilter=True)
            .limit(N_RESULTS_RETRIEVED)
            .rerank(reranker=reranker)
            ).to_list()

# simple present results
print(f"top {N_RETRIEVED_RESULTS_PRESENTED} results for query: '{QUERY}'")
for i, result in enumerate(results[:N_RETRIEVED_RESULTS_PRESENTED]):
    rel_score = result['_relevance_score']
    txt = result['text']
    print(f"result #{i+1}, relevance-score: {rel_score:.2f}")
    print(txt)
    input("(press any key for next result)\n")