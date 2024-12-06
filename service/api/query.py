from fastapi import APIRouter, Depends
from core.openapi import openapi_validation_dependency  # Import the dependency
from core.llm import askLLM

# Create a new router for /api endpoints
api_router = APIRouter()

# Example endpoint for /api/query, applying the OpenAPI validation dependency via Depends
@api_router.post("/query", dependencies=[Depends(openapi_validation_dependency)])
async def query(data: dict):
    response = askLLM(data['query'])
    return response