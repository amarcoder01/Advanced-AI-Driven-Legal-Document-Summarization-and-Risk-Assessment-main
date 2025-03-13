# RAG Integration with Gemini and LangChain

A modular implementation of Retrieval Augmented Generation (RAG) using Google's Gemini model, Hugging Face embeddings, and LangChain.

## Features

- **Document Processing**: Support for PDF, TXT, CSV, and Markdown files
- **Modular Architecture**: Clean separation of components
- **Multiple Vector Stores**: Support for both FAISS and Chroma
- **Flexible Embeddings**: Uses Hugging Face's sentence transformers
- **Advanced RAG**: Implements sophisticated retrieval and answer generation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API keys:
   - Create a `.streamlit/secrets.toml` file with:
   ```toml
   [api]
   GOOGLE_API_KEY = "your-google-api-key"
   HUGGINGFACE_API_KEY = "your-huggingface-api-key"
   ```
   Or use environment variables:
   ```bash
   export GOOGLE_API_KEY="your-google-api-key"
   export HUGGINGFACE_API_KEY="your-huggingface-api-key"
   ```

## Usage

```python
from rag_integration.rag_pipeline import RAGPipeline

# Initialize the pipeline
rag = RAGPipeline()

# Initialize with documents
rag.initialize()

# Add documents
rag.add_documents(["path/to/document.pdf"])

# Query the system
result = rag.query("Your question here")
print(result["answer"])
```

## Project Structure

```
rag_integration/
├── __init__.py
├── config.py           # Configuration settings
├── document_loader.py  # Document processing
├── embeddings.py      # Embedding management
├── gemini_integration.py  # Gemini model integration
└── rag_pipeline.py    # Main RAG pipeline
```

## Configuration

Key settings in `config.py`:
- Model names and parameters
- Chunk size and overlap
- Number of documents to retrieve
- Vector database settings

## Requirements

- Python 3.8+
- Google API key (for Gemini)
- Hugging Face API key (optional)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

# AI Legal Document Assistant

A powerful AI-powered application for analyzing, understanding, and working with legal documents. Built with Streamlit and powered by Google's Gemini AI model.

## Features

- **Document Upload**: Support for PDF and TXT files
- **Document Analysis**: Get comprehensive summaries and key insights
- **Risk Assessment**: Identify and analyze potential risks in legal documents
- **Compliance Checking**: Verify compliance with various regulatory frameworks
- **Interactive Chat**: Ask questions about your documents and get AI-powered responses
- **Document Comparison**: Compare multiple legal documents for similarities and differences
- **Export Options**: Download analysis results in PDF, DOCX, or TXT formats

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-legal-assistant.git
cd ai-legal-assistant
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided URL (typically http://localhost:8501)

3. Upload a legal document and use the various features through the intuitive interface

## Project Structure

```
ai-legal-assistant/
├── app.py                 # Main application file
├── modules/
│   ├── chat_handler.py    # Chat functionality
│   ├── compliance_checker.py # Compliance checking
│   ├── document_analyzer.py # Document analysis
│   ├── document_comparer.py # Document comparison
│   ├── export_handler.py    # Export functionality
│   └── risk_analyzer.py     # Risk analysis
├── utils/
│   ├── file_processor.py    # File handling utilities
│   └── state_management.py  # Session state management
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## Dependencies

- streamlit: Web application framework
- google-generativeai: Gemini AI model integration
- PyPDF2: PDF file processing
- python-docx: DOCX file handling
- fpdf: PDF generation
- plotly: Data visualization
- And more (see requirements.txt)

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Risk Visualizer View
elif st.session_state.risk_view == "visualizer":
    if st.button("← Back to Dashboard"):
        st.session_state.risk_view = "main"
        st.rerun()
    
    if st.session_state.get("risks"):
        visualize_risks_streamlit(st.session_state.risks)
    else:
        st.info("Please analyze the document first.")



