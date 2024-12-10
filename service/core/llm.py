import os, json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from core.vectors import load_chroma, query_vector_store
from dotenv import load_dotenv

load_dotenv(override=True)

doc_name = os.getenv('DOCUMENT_TITLE')
db_path = os.getenv('CHROMA_PATH')

def initialize_llm(model_name: str = "gpt-4o", temperature: float = 0.4) -> ChatOpenAI:
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OpenAI API key not found.")
    
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        openai_api_key=openai_api_key,
        request_timeout=30  # Timeout after 30 seconds if no response
    )
    
    return llm

def get_summary_prompt() -> PromptTemplate:
    prompt_text = (
        f"You are a helpful and dispassionate resource to answer the provided question(s) pertaining to the document titled {doc_name} using only the information provided below 'Context'. "
        f"Do not directly reference the fact that there is 'context' or say things like 'based on the provided context'. Simply, respond to the question. "
        f"The question to be answered can be found below under 'Question'. "
        f"If the question is obviously not pertaining to {doc_name} or the context, explain that this agent is designed to answer questions about {doc_name} and ask that they ask a question about that topic. "
        f"Review the context thoroughly and if you notice any conflicting or contradictory information, do your best to reconcile and respond while making it clear that the user should check your response with the document. "
        f"If the context does not provide enough information to answer the question, clearly state 'I'm not sure, but that doesn't mean the answer is not in the document. My responses are not perfect.' "
        f"Do not attempt to infer or make assumptions beyond the provided information. "
        f"If the question is too ambiguous, do your best to answer, but then also suggest a different wording to the question for clarification that they could use to ask you for a better response. "
        f"When responding, be sure to cite the relevant sections or page numbers of the source material ({doc_name}) as provided whenever possible. "
        
        f"\nQuestion:\n{{question}}"
        f"\nContext:\n{{context}}"
    )
    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["question", "context"]
    )
    return prompt

def askLLM(question: str) -> str:
    try:
        llm = initialize_llm()
        vectorstore = load_chroma(db_path)
        
        # Retrieve Context
        context_results = query_vector_store(vectorstore=vectorstore, query=question)
        
        # Extract context - assuming context_results is a list of tuples (document, score)
        context_list = []
        for result, score in context_results:
            page_num = result.metadata.get('page')
            section = result.metadata.get("section_name") or "See reference below for section details"
            context_text = result.page_content

            # Create a JSON-like structured object
            context_entry = {
                "Section": section,
                "Page(s)": page_num,
                "Reference": context_text
            }
            context_list.append(context_entry)
        
        # Convert the list of context entries into a JSON-like string
        context = json.dumps(context_list, indent=2)
        prompt = get_summary_prompt()
        prompt_text = prompt.format(question=question,context=context)

        response = llm.invoke(prompt_text)
        # Extract content if it's an AIMessage-like object
        if hasattr(response, 'content'):
            return { "response": response.content.strip(), "context": context_list}
        else:
            return { "response": response.strip(), "context": context_list}
    except Exception as e:
        raise e