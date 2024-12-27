# summarization.py
from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
import os
import json
import logging
import random, time
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from tqdm import tqdm  # Added tqdm for progress tracking
from dotenv import load_dotenv

load_dotenv(override=True)

doc_name = os.getenv('DOCUMENT_TITLE')

def load_document(file_path: str):
    print("starting load...")
    # Get the absolute path to ensure it's correct relative to the root
    root_dir = Path(__file__).resolve().parent.parent
    full_path = f"{root_dir}/{file_path}"
    # Load the document
    loader = PyPDFLoader(full_path)
    documents = loader.load()
    # validate - delete these later
    print(f"Loaded {len(documents)} pages from the PDF")
    return documents

# Configure logging
logging.basicConfig(
    filename='summarization.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def initialize_llm(model_name: str = "gpt-4o-mini", temperature: float = 0.3) -> ChatOpenAI:
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        logging.error("OpenAI API key not found in environment variables.")
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        openai_api_key=openai_api_key,
        request_timeout=30  # Timeout after 30 seconds if no response
    )
    logging.info(f"Initialized OpenAI LLM with model {model_name}.")
    return llm

def get_summary_prompt(section_name: str, author: str, token_limit: int) -> PromptTemplate:
    if isinstance(author, list):
        author_text = f" Section contributors: {', '.join(author)}."
    elif isinstance(author, str):
        author_text = f" Section contributors: {author}."
    else:
        author_text = None

    prompt_text = (
        f"You are a dispassionate assistant helping me create summaries of discrete blocks of content that belong to a larger document. "
        f"Create a summary of the below content that is {token_limit} tokens or less with the following guidelines: "
        f"The summary should start with the name of the section presented as 'This is {doc_name} section: {section_name}'. "
    )

    # Conditionally add the line if `author_text` is not empty or None
    if author_text:
        prompt_text += f"Then you should list the contributors, which are people who helped write it but may not be the main authors, for the section. {author_text} "

    # Continue with the rest of the prompt
    prompt_text += (
        f"You should then briefly summarize the intent and main point of the section in five sentences or less. "
        f"Finally, identify all persons, places, and dates in the content, list them without any special formatting, and provide very brief information about why each is important and relevant to the content or larger document, if you have enough information to understand that larger context. "
        f"\nContent:\n{{text}}"
    )

    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["text"]
    )
    return prompt

def summarize_text(llm: ChatOpenAI, text: str, prompt: PromptTemplate, retries: int = 5, backoff_factor: int = 2, max_delay: int = 60) -> str:
    """
    Summarizes text using the LLM with retry logic and exponential backoff to avoid overwhelming the server.

    Args:
        llm (ChatOpenAI): The initialized LangChain LLM.
        text (str): The text to summarize.
        prompt (PromptTemplate): The prompt template for summarization.
        retries (int): Maximum number of retry attempts.
        backoff_factor (int): Base multiplier for exponential backoff.
        max_delay (int): Maximum delay between retries.

    Returns:
        str: The generated summary.
    """
    for attempt in range(retries):
        try:
            # Use the prompt to generate a formatted prompt string with the actual content
            prompt_text = prompt.format(text=text)
            start_time = time.time()
            logging.info(f"Starting summarization for prompt: {prompt.template[:50]}... with text length: {len(text)}")
            # Generate the summary using the LLM
            summary = llm.invoke(prompt_text)
            end_time = time.time()
            logging.info(f"Completed summarization in {end_time - start_time:.2f} seconds")
            # Extract content if it's an AIMessage-like object
            if hasattr(summary, 'content'):
                return summary.content.strip()
            else:
                return summary.strip()

        except Exception as e:
            # Log the failure and retry, if it's not the last attempt
            logging.warning(f"Attempt {attempt + 1} failed with error: {e}")

            if attempt < retries - 1:
                # Calculate exponential backoff delay with jitter
                delay = min(max_delay, backoff_factor ** attempt + random.uniform(0, 1))
                logging.info(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)  # Delay before retrying
            else:
                logging.error(f"All {retries} attempts failed for summarization.")
                raise e



def process_section(section: Dict, document: List, llm: ChatOpenAI) -> Dict:
    section_name = section['sectionName']
    page_start, page_end = section['pageRange']
    author = section.get('author', None)

    # Calculate number of pages
    num_pages = page_end - page_start + 1

    # Validate the page range before proceeding
    if page_start < 1 or page_end > len(document):
        logging.error(f"Page range for section '{section_name}' is out of bounds. Skipping this section.")
        return section

    try:
        if num_pages <= 5:
            # Concatenate pages by extracting 'page_content' from each document object
            pages_text = " ".join(doc.page_content for doc in document[page_start - 1: page_end])
            # Check if `pages_text` is empty
            if not pages_text.strip():
                logging.warning(f"No content found for section '{section_name}'. Skipping this section.")
                return section
            logging.info(f"Creating prompt for '{section_name}'.")
            prompt = get_summary_prompt(section_name, author, 700)
            logging.info(f"Summarizing '{section_name}'.")
            summary = summarize_text(llm, pages_text, prompt)
        else:
            # Split into groups of 5 pages
            group_summaries = []
            for i in range(page_start, page_end + 1, 5):
                group_end = min(i + 4, page_end)
                if i - 1 >= len(document) or group_end > len(document):
                    logging.error(f"Page range {i} to {group_end} for section '{section_name}' is out of bounds. Skipping this group.")
                    continue

                # Extract 'page_content' from each document object in the group
                group_text = " ".join(doc.page_content for doc in document[i - 1: group_end])
                # Check if `group_text` is empty
                if not group_text.strip():
                    logging.warning(f"No content found for pages {i}-{group_end} in section '{section_name}'. Skipping this group.")
                    continue
                
                logging.info(f"Creating prompt for sub-section of '{section_name}'.")
                prompt = get_summary_prompt(section_name, author, 500)
                logging.info(f"Summarizing for sub-section of '{section_name}'.")
                group_summary = summarize_text(llm, group_text, prompt)
                logging.info(f"Appending to group summary for sub-section of '{section_name}'.")
                group_summaries.append(group_summary)

            # Concatenate group summaries and create final summary
            if group_summaries:
                logging.info(f"Validated that there is a group summary for '{section_name}'.")
                concatenated_summaries = " ".join(group_summaries)
                logging.info(f"Creating prompt after processign sub-sections for '{section_name}'.")
                final_prompt = get_summary_prompt(section_name, author, 700)
                logging.info(f"Summarizing after processign sub-sections for '{section_name}'.")
                summary = summarize_text(llm, concatenated_summaries, final_prompt)
            else:
                logging.warning(f"No valid group summaries generated for section '{section_name}'. Skipping final summary.")
                return section

        # Add summary to section
        section['summary'] = summary

        # Write summary to log file - Remove this later
        summary_log_file = "summaries_log.txt"
        log_text = pages_text if num_pages <= 5 else concatenated_summaries
        with open(summary_log_file, 'a') as log_file:
            log_file.write(f"Section: {section_name} (Text length: {len(log_text)})\n")
            log_file.write(f"Summary:\n{summary}\n")
            log_file.write("=" * 50 + "\n")

        logging.info(f"Summarized section: {section_name}")
        return section
    except Exception as e:
        logging.error(f"Error processing section '{section_name}': {e}")
        raise e


def save_json(data: List[Dict], file_path: str):
    # Get the absolute path to ensure it's correct relative to the root
    root_dir = Path(__file__).resolve().parent.parent
    full_path = f"{root_dir}/{file_path}"
    # Write the contents
    with open(full_path, 'w') as f:
        json.dump(data, f, indent=4)
    logging.info(f"Saved summarized data to {full_path}.")

def save_text(content: str, file_path: str):
    with open(file_path, 'w') as f:
        f.write(content)
    logging.info(f"Saved summary to {file_path}.")

def main():
    # File paths

    input_toc = os.getenv('PRE_PROCESSED_SECTIONS')       # Preprocessed TOC
    pdf_file = os.getenv('DOCUMENT')            # Replace with your actual PDF path
    output_json = os.getenv('SUMMARY')   # Output summaries
    model_name = os.getenv('SUMMARY_MODEL')
    
    # Load PDF
    documents = load_document(pdf_file)

    # Initialize LLM
    llm = initialize_llm(model_name=model_name)
    
    # Load the preprocessed sections
    if not os.path.exists(input_toc):
        logging.error(f"The TOC file {input_toc} does not exist.")
        raise FileNotFoundError(f"The TOC file {input_toc} does not exist.")
    
    with open(input_toc, 'r') as f:
        sections = json.load(f)
    logging.info(f"Loaded {len(sections)} sections from {input_toc}.")
    
    summarized_sections = []

    # Process each section one by one
    for section in tqdm(sections, desc="Processing sections"):
        try:
            summarized_section = process_section(section, documents, llm)
            summarized_sections.append(summarized_section)
        except Exception as e:
            logging.error(f"Error processing section '{section['sectionName']}': {e}")
            print(f"Error processing section '{section['sectionName']}': {e}")
            continue  # Stop processing on error
    
    # Save the summarized sections to docSummary.json
    try:
        save_json(summarized_sections, output_json)
        print(f"Summarized data saved to {output_json}")
    except Exception as e:
        logging.error(f"Error writing data to output json: {e}")
        print(f"Error writing data to output json: {e}")

if __name__ == "__main__":
    main()