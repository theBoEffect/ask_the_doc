import json, os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

def load_tos_summary(file_path: str) -> List[Dict]:
    with open(file_path, 'r') as f:
        return json.load(f)

def merge_overlapping_sections(sections: List[Dict]) -> List[Dict]:
    # Sort sections by starting page
    sections = sorted(sections, key=lambda x: x['pageRange'][0])
    merged_sections = []
    
    for section in sections:
        if not merged_sections:
            merged_sections.append(section)
            continue
        
        last = merged_sections[-1]
        # Check for overlap
        if section['pageRange'][0] <= last['pageRange'][1]:
            # Merge the two sections
            merged_page_start = min(last['pageRange'][0], section['pageRange'][0])
            merged_page_end = max(last['pageRange'][1], section['pageRange'][1])
            
            # Consolidate authors
            merged_authors = set()
            if last['author']:
                if isinstance(last['author'], list):
                    merged_authors.update(last['author'])
                else:
                    merged_authors.add(last['author'])
            if section['author']:
                if isinstance(section['author'], list):
                    merged_authors.update(section['author'])
                else:
                    merged_authors.add(section['author'])
            merged_authors = list(merged_authors) if merged_authors else None
            
            merged_section = {
                'sectionName': f"{last['sectionName']} + {section['sectionName']}",
                'pageRange': [merged_page_start, merged_page_end],
                'author': merged_authors
            }
            merged_sections[-1] = merged_section
        else:
            merged_sections.append(section)
    
    return merged_sections

def preprocess_sections(input_file: str, output_file: str) -> List[Dict]:
    sections = load_tos_summary(input_file)
    merged_sections = merge_overlapping_sections(sections)
    
    # Save the preprocessed sections to a new file
    with open(output_file, 'w') as f:
        json.dump(merged_sections, f, indent=4)
    
    return merged_sections

# Example usage
if __name__ == "__main__":
    print("STARTING")
    input_json = f"./{os.getenv('SECTIONS')}"
    output_json = f"./{os.getenv('PRE_PROCESSED_SECTIONS')}"
    preprocessed_sections = preprocess_sections(input_json, output_json)
    print(f"Preprocessed {len(preprocessed_sections)} sections.")