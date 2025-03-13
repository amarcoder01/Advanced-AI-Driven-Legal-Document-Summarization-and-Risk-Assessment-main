"""
Example script demonstrating how to use the RAG integration.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if required API keys are set
if not os.getenv("GOOGLE_API_KEY"):
    print("Please set the GOOGLE_API_KEY environment variable in a .env file")
    print("Example: GOOGLE_API_KEY=your_api_key_here")
    exit(1)

from rag_pipeline import RAGPipeline

def main():
    """Main example function."""
    # Create the documents directory if it doesn't exist
    if not os.path.exists("./documents"):
        os.makedirs("./documents")
        print("Created documents directory. Please add some documents to ./documents/")
        print("Supported formats: PDF, TXT, CSV, MD")
        exit(0)
    
    # Initialize the RAG pipeline
    print("Initializing RAG pipeline...")
    rag = RAGPipeline()
    rag.initialize()
    
    if not rag.documents:
        print("No documents found. Please add some documents to ./documents/")
        exit(0)
    
    # Interactive query loop
    print("\n" + "="*50)
    print("RAG Query System")
    print("Type 'exit' to quit")
    print("="*50 + "\n")
    
    while True:
        query = input("\nEnter your query: ")
        if query.lower() in ("exit", "quit", "q"):
            break
            
        print("\nSearching for relevant information...")
        result = rag.query(query)
        
        print("\nAnswer:")
        print(result["answer"])
        
        print("\nSources:")
        for i, doc in enumerate(result["source_documents"][:3], 1):
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "")
            page_info = f" (Page {page})" if page else ""
            print(f"{i}. {source}{page_info}")
            if len(doc.page_content) > 200:
                print(f"   {doc.page_content[:200]}...")
            else:
                print(f"   {doc.page_content}")
        
        print("\n" + "-"*50)

if __name__ == "__main__":
    main() 