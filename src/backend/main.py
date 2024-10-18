import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from lancedb.rerankers import  CrossEncoderReranker CrossEncoderReranker

# Load the bi-encoder embedding model
model = get_registry().get("sentence-transformers").create(name="BAAI/bge-small-en-v1.5")

# Our Data Model/Schema for the document chunks we'll store in our db
class DocumentChunk(LanceModel):
    text: str = model.SourceField()
    vector: Vector(384) = model.VectorField()
    category: str

# load db
db = lancedb.connect("src/backend/lancedb")
tbl = db.create_table("document_chunks", schema=DocumentChunk)

# Embed the documents and store them in the db
tbl.add(docs)

# Generate the full-text (tf-idf) search index
tbl.create_fts_index("text")

# Initialize the cross-encoder reranker
reranker = CrossEncoderReranker()

# Query the documents
query = "What were some of the key revelations from Cassidy Hutchinson?"
results = (tbl.search(query, query_type="hybrid"),
            #.where("category = 'some_category'", prefilter=True)
            .limit(10)
            .rerank(reranker=reranker)
            )

