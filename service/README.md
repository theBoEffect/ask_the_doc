# Document LLM Q&A Service

This project processes a large document into a vectorstore database (ChromaDB) and allows an LLM to answer questions about that document. This requires the following steps:

1. Define your .env and install dependencies
2. Pick and place your document
3. Define sections as a json document.
4. Process your json document into summaries to be included in the vectorstore
5. Run the service

## 1. Define .env, venv, and pip install

```
OPENAI_API_KEY=sk-proj-KEY
OPENAPI_SPEC=openapi.yaml
DOCUMENT_TITLE=Document Title Here
DOCUMENT=data/document.pdf
SUMMARY=data/docSummary.json
CHROMA_PATH=./chroma_db
SUMMARY_MODEL=gpt-4o-mini
LLM_MODEL=gpt-4o-mini
SECTIONS=tos.json
PRE_PROCESSED_SECTIONS=preprocessed_tos.json
```
* creeate .env in ./service with the above
* define and activate your local python venv
* pip install --no-cache-dir -r requirements.txt

## 2. Pick Your Document

* Select a document you'd like to process and save it to the data director of this service section (./service/data) as document.pdf
* You can use ./service/example/proj2025/document.pdf if you wish.
* If you decide you want to use a different name than "document", you just need to update the .env value as well

## 3. Define Sections

You'll want to define a JSON document that includes the following structure and represent your document sections.
```
[
    { "sectionName": "NAME HERE", "pageRange": [1, 10], "author": "STRING OR NULL" },
    ...
]
```
* You can see an example of this in ./service/examples/proj2025/tos_example.json
* Once you've created the doc, move it over to ./service/processing/tos.json
* You'll notice that it is referenced through a .env as tos.json, but you could pick a different name

## 4. Process Sections

1. We will first clean up and combine overlapping sections in tos.json.
2. Then we will build a summarization of the sections from the document.pdf file. This may take 15 to 20 minutes.
3. Finally we need to move the resulting JSON (docSummary.json according to .env) to the data director of the project, ./service/data

Note that you will see 2 log files which can help you follow whats happening: summaries_log.txt and summarization.log. You can delete these afterwards if things work as expected. It's easiest to move into the processing directory to do all this.

* cd ./processing
* python preprocessing.py
* python summarize.py
* cd ..
* cp ./processing/docSummary.json ./data/docSummary.json

# 5. Run the Service

At this point, everything is in place. When you start the service, it will check to see if ./chroma_db (from .env) is present or not. If not, it will build the vectorstore and start the service to process queries. If chroma is there, it will simply start the service.

* uvicorn app:app --reload
* localhost:8000/docs (this is swagger)

### Docker with GCP and Google Run

* You'll want to run it locally once to build ./chroma_db before building the container - its a todo to move this into a build step
* Also make sure you've gone to ./ui and run "yarn build" to get the static UI files over here
* docker build --platform=linux/amd64 --no-cache -t gcr.io/YOUR-PROJECT/ask_the_doc .
* docker push gcr.io/YOUR-PROJECT/ask_the_doc

```
gcloud run deploy ask-the-doc \
    --image gcr.io/YOUR-PROJECT/ask_the_doc:latest \
    --platform managed \
    --region us-east4 \
    --allow-unauthenticated \
    --update-secrets "OPENAI_API_KEY=YOUR_SECRET_IN_GCP:latest" \
    --set-env-vars "DOCUMENT=data/document.pdf,SUMMARY=data/docSummary.json,CHROMA_PATH=./chroma_db,SUMMARY_MODEL=gpt-4o-mini,LLM_MODEL=gpt-4o-mini,SECTIONS=tos.json,PRE_PROCESSED_SECTIONS=preprocessed_tos.json"
```