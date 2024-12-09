import os
import core.document
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.query import api_router  # Import API router from the query file
from core.openapi import custom_openapi  # Import custom OpenAPI schema override
from core.vectors import split_document_into_chunks, load_summaries_from_json, store_all_chunks_in_chroma
from dotenv import load_dotenv

load_dotenv()

file_name = os.getenv('DOCUMENT')
db_path = os.getenv('CHROMA_PATH')
summary_file_path = os.getenv('SUMMARY')

# Lifespane logic for start and termination
@asynccontextmanager
async def lifespan(app: FastAPI):
    # If the DB exists, do nothing, otherwise load the data
    if os.path.exists(db_path):
        print("Ready to load existing Chroma DB...")
    else:
        # Startup logic: Load the document
        print("STARTING - Loading document...")
        documents = core.document.load_document(file_name)

        # Step 1: Split the main document into chunks
        print("Splitting document into chunks...")
        chunks = split_document_into_chunks(documents)

        # Step 2: Load summaries from docSummary.json
        print("Loading summaries...")
        summary_chunks = load_summaries_from_json(summary_file_path)

        # Step 3: Store all chunks (document + summaries) in Chroma in a unified pass
        print("Storing all chunks (document and summaries) in Chroma DB...")
        store_all_chunks_in_chroma(chunks, summary_chunks, persist_directory=db_path)

    yield

# Initialize the FastAPI app
app = FastAPI(lifespan=lifespan)

# Set the custom OpenAPI schema
app.openapi = custom_openapi  # Use the custom OpenAPI schema

# Include the /api router under the /api path
app.include_router(api_router, prefix="/api")

# Allow specific origins (e.g., frontend URL)
origins = [
    "http://localhost:5173"  # Replace with your frontend's local development URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from these origins
    allow_credentials=True,  # Allows cookies or Authorization headers
    allow_methods=["*"],  # Allows all HTTP methods (e.g., GET, POST)
    allow_headers=["*"],  # Allows all headers (e.g., Content-Type, Authorization)
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the app!"}