from lancedb.pydantic import LanceModel, Vector
from src.backend.config import embedding_model

class DocumentChunk(LanceModel):
    text: str = embedding_model.SourceField()

class DocumentChunkLanceRecord(DocumentChunk):
    """LanceDB will create our vector embeddings for us, as long as we 
       provide a LanceModel schema which defines a 'vector' attr w/ a 
       suitable embedding model & ndims"""
    vector: Vector(embedding_model.ndims()) = embedding_model.VectorField()
