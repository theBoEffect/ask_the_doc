import os, json
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.schema import Document  # Import the Document class
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")
db_path = os.getenv('CHROMA_PATH')

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-large")

# DB exists, loading it only
def load_chroma(persist_directory):
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vectorstore

# Step 1: Load and split the document into chunks
def split_document_into_chunks(documents, chunk_size=1500, overlap=500):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,  # Define the chunk size
        chunk_overlap=overlap,  # Define the overlap between chunks
        length_function=len  # Use length of characters to determine the chunk size
    )
    return text_splitter.split_documents(documents)

# Step 2: Load summaries from docSummary.json and create chunks
def load_summaries_from_json(file_path):
    # Determine the absolute path to the summary file
    root_dir = Path(__file__).resolve().parent.parent
    print('sum doc', file_path)
    summary_file_path = f"{root_dir}/{file_path}"
    print('sum path', summary_file_path)
    # Check if the file exists
    if not os.path.exists(summary_file_path):
        print(f"Warning: The file {summary_file_path} does not exist.")
        return []

    # Attempt to load summaries from the file
    try:
        with open(summary_file_path, 'r') as f:
            summaries = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON from {summary_file_path}: {e}")
        return []

    # Create Document objects from summaries
    summary_chunks = []
    for summary in summaries:
        # Creating a Document object with page_content and metadata
        summary_chunk = Document(
            page_content=summary['summary'],
            metadata={
                'section_name': summary['sectionName'],
                'page_range': str(summary['pageRange']),  # Convert list to string to comply with metadata requirements
                'authors': summary.get('author') if isinstance(summary.get('author'), (str, int, float, bool)) else str(summary.get('author')),
                'page': f"Data from pages: {str(summary['pageRange'])}"
            }
        )
        summary_chunks.append(summary_chunk)

    return summary_chunks

# Step 3: Unified storage of document chunks and summaries in Chroma
def store_all_chunks_in_chroma(doc_chunks, summary_chunks, persist_directory=db_path):
    # Combine document chunks and summary chunks
    all_chunks = doc_chunks + summary_chunks

    # Create or load vectorstore
    if os.path.exists(persist_directory):
        vectorstore = load_chroma(persist_directory)
        vectorstore.add_documents(documents=all_chunks)
    else:
        vectorstore = Chroma.from_documents(
            documents=all_chunks,  # List of all chunk objects
            embedding=embeddings,
            persist_directory=persist_directory  # Path to save Chroma data
        )

    return vectorstore

# Query the vector store
def query_vector_store(vectorstore, query):
    results = vectorstore.similarity_search_with_score(query, k=7)
    return results
