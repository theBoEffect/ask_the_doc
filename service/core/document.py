from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path

# Global variable to hold the loaded documents
documents = []

def load_document(file_path: str):
    global documents
    print("starting load...", file_path)
    # Get the absolute path to ensure it's correct relative to the root
    root_dir = Path(__file__).resolve().parent.parent
    full_path = f"{root_dir}/{file_path}"
    # Load the document
    loader = PyPDFLoader(full_path)
    documents = loader.load()
    # validate - delete these later
    print(f"Loaded {len(documents)} pages from the PDF")
    return documents
    