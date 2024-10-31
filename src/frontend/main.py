import lancedb
import streamlit as st

from src.backend.main import query_documents
from src.backend.database.operations import get_or_setup_db
from src.backend.config import N_RESULTS_RETRIEVED, N_RESULTS_PRESENTED

def main():
    st.title("Document Query System")

    # Sidebar for configurations
    with st.sidebar:
        reindex_docs = st.checkbox("Re-index documents", 
                                 help="Re-run document ingestion/chunking/indexing pipeline before querying",
                                 value=False
                                 )

    # Main query interface
    query = st.text_input("Enter your question or query")
    
    if query:
        table = get_or_setup_db(reindex=reindex_docs)        
        response = query_documents(table, query, num_results_presented=N_RESULTS_PRESENTED)
        st.write(response)

if __name__ == "__main__":
    main()