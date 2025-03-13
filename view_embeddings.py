"""
Script to visualize and explore embeddings.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import streamlit as st
from rag_pipeline import RAGPipeline
from rag_document_loader import DocumentProcessor

def ensure_directories():
    """Ensure all necessary directories exist."""
    directories = ["./documents", "./vector_db"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        st.sidebar.success(f"✓ Directory ready: {directory}")

def get_api_key():
    """Get the Google API key from secrets."""
    try:
        # Try to get from api section first
        api_key = st.secrets.api.GOOGLE_API_KEY
    except:
        try:
            # Try to get from root section
            api_key = st.secrets.GOOGLE_API_KEY
        except:
            return None
    return api_key

def plot_embeddings(embeddings, labels=None):
    """Plot embeddings in 2D using PCA."""
    # Reduce dimensions to 2D
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings)
    
    # Create the plot
    plt.figure(figsize=(10, 10))
    scatter = plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1])
    
    if labels:
        for i, label in enumerate(labels):
            plt.annotate(label[:30] + "...", (embeddings_2d[i, 0], embeddings_2d[i, 1]))
    
    plt.title("Document Embeddings Visualization")
    plt.xlabel("First Principal Component")
    plt.ylabel("Second Principal Component")
    return plt

def main():
    st.title("Document Embeddings Viewer")
    
    # Setup sidebar
    st.sidebar.title("Setup Status")
    
    # Ensure directories exist
    ensure_directories()
    
    # Check for API keys
    api_key = get_api_key()
    if not api_key:
        st.error("Google API Key not found in Streamlit secrets. Please check your secrets.toml file.")
        st.info("The API key should be set as either:\n- secrets.api.GOOGLE_API_KEY\n- secrets.GOOGLE_API_KEY")
        return
    else:
        st.sidebar.success("✓ API key found")
    
    try:
        # Initialize RAG pipeline with explicit settings
        rag = RAGPipeline(
            document_dir="./documents",
            vector_db_path="./vector_db",
            temperature=0.2
        )
        st.sidebar.success("✓ RAG pipeline initialized")
        
        # File uploader
        st.write("### Upload Documents")
        st.write("Supported formats: PDF, TXT, CSV, Markdown")
        uploaded_files = st.file_uploader(
            "Choose files to analyze",
            accept_multiple_files=True,
            type=['pdf', 'txt', 'csv', 'md']
        )
        
        if uploaded_files:
            st.info("Processing documents...")
            
            # Save uploaded files temporarily
            temp_paths = []
            for file in uploaded_files:
                temp_path = os.path.join("./documents", file.name)
                with open(temp_path, "wb") as f:
                    f.write(file.getvalue())
                temp_paths.append(temp_path)
                st.sidebar.info(f"✓ Loaded: {file.name}")
            
            try:
                # Initialize and process documents
                with st.spinner("Initializing RAG pipeline..."):
                    rag.initialize(force_reload=True)
                
                if rag.documents:
                    # Get embeddings for each document chunk
                    embeddings = []
                    texts = []
                    
                    with st.spinner("Generating embeddings..."):
                        for i, doc in enumerate(rag.documents):
                            # Show progress
                            progress = (i + 1) / len(rag.documents)
                            st.progress(progress)
                            
                            # Get embedding for the document chunk
                            embedding = rag.embedding_manager.embeddings.embed_query(doc.page_content)
                            embeddings.append(embedding)
                            texts.append(doc.page_content)
                    
                    # Convert to numpy array
                    embeddings_array = np.array(embeddings)
                    
                    # Plot embeddings
                    st.subheader("Document Embeddings Visualization")
                    st.write("This plot shows how different parts of your documents relate to each other in 2D space.")
                    fig = plot_embeddings(embeddings_array, texts)
                    st.pyplot(fig)
                    
                    # Show similarity matrix
                    st.subheader("Document Chunk Similarity Matrix")
                    st.write("This matrix shows how similar different chunks of text are to each other.")
                    similarity_matrix = np.dot(embeddings_array, embeddings_array.T)
                    fig_matrix, ax = plt.subplots(figsize=(10, 10))
                    im = ax.matshow(similarity_matrix)
                    plt.colorbar(im)
                    st.pyplot(fig_matrix)
                    
                    # Display some statistics
                    st.sidebar.subheader("Analysis Stats")
                    st.sidebar.write(f"Total chunks: {len(rag.documents)}")
                    st.sidebar.write(f"Embedding dimensions: {embeddings_array.shape[1]}")
                    
                else:
                    st.warning("No documents were processed. Please check the file formats.")
            
            except Exception as e:
                st.error(f"Error processing documents: {str(e)}")
                st.error("Full error:", exc_info=True)
            
            finally:
                # Clean up temporary files
                for path in temp_paths:
                    if os.path.exists(path):
                        os.remove(path)
        
        else:
            st.info("👆 Please upload some documents to visualize their embeddings.")
    
    except Exception as e:
        st.error(f"Error initializing RAG pipeline: {str(e)}")
        st.error("Full error:", exc_info=True)

if __name__ == "__main__":
    main() 