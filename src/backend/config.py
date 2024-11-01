import google.generativeai as genai
import streamlit as st

from sentence_transformers import SentenceTransformer
import lancedb
from lancedb.rerankers import CrossEncoderReranker
from lancedb.embeddings import get_registry


EMBEDDING_MODEL = ("sentence-transformers", "BAAI/bge-small-en-v1.5")
LOCAL_DB_PATH = "src/backend/lancedb"
CLOUD_DB_URI = "db://askliz-doc-db-8qjgop"
CORPUS_PATH = "corpus/j6c_final_report/FINAL_REPORT.html"
N_RESULTS_RETRIEVED = 10  # Number of results retrieved for re-ranking
N_RESULTS_PRESENTED = 3   # Number of top results from re-ranker to present to user (via LLM)

# Load secrets
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
LANCEDB_API_KEY = st.secrets["lancedb"]["api_key"]

# Load embedding model
embedding_model = get_registry().get(EMBEDDING_MODEL[0]).create(name=EMBEDDING_MODEL[1])
tokenizer = SentenceTransformer(EMBEDDING_MODEL[1]).tokenizer

# Load Reranker
reranker = CrossEncoderReranker()

# Load & Configure LLM to craft final response to user ('G' in RAG):
FINAL_LLM_MODEL = "gemini-1.5-pro"
generation_config = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 2048,
}

genai.configure(api_key=GEMINI_API_KEY)
g_llm = genai.GenerativeModel(FINAL_LLM_MODEL, generation_config=generation_config)

# DB connection  (updated to lancedb cloud)
ldb_conn = lancedb.connect(CLOUD_DB_URI, api_key=LANCEDB_API_KEY)