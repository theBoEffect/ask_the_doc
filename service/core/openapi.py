from openapi_core.spec.paths import Spec
from openapi_core.contrib.fastapi.middlewares import FastAPIOpenAPIMiddleware
from fastapi import Request
import yaml, os
from dotenv import load_dotenv

load_dotenv()

open_api = os.getenv('OPENAPI_SPEC')

# Load the OpenAPI spec using PyYAML
with open(open_api, "r") as file:
    spec_dict = yaml.safe_load(file)  # Parse the YAML spec
spec = Spec.from_dict(spec_dict)

# Override FastAPI's OpenAPI schema to use the custom OpenAPI spec
def custom_openapi():
    return spec_dict  # Returning the loaded YAML as JSON for Swagger UI

# Create a wrapper around the FastAPIOpenAPIMiddleware for OpenAPI validation
def openapi_validation_dependency(request: Request):
    middleware = FastAPIOpenAPIMiddleware(request.app, openapi=spec)
    return middleware
