import pdfplumber
import re
from typing import List, Dict

def parse_quiz_pdf(pdf_path: str) -> List[Dict]:
    """
    Parse a PDF file containing quiz questions in the format:
    
    Q1. Question text?
    A) Option 1
    B) Option 2
    C) Option 3
    D) Option 4
    Answer: A
    """
    questions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    
    # Split by question numbers (Q1, Q2, etc.)
    question_blocks = re.split(r'\n(?=Q\d+\.)', text.strip())
    
    for block in question_blocks:
        if not block.strip():
            continue
            
        try:
            # Extract question text
            question_match = re.search(r'Q\d+\.\s*(.+?)(?=\n[A-D]\))', block, re.DOTALL)
            if not question_match:
                continue
            
            question_text = question_match.group(1).strip()
            
            # Extract options
            options = []
            for letter in ['A', 'B', 'C', 'D']:
                option_match = re.search(rf'{letter}\)\s*(.+?)(?=\n[A-D]\)|\nAnswer:)', block, re.DOTALL)
                if option_match:
                    options.append(option_match.group(1).strip())
            
            # Extract correct answer
            answer_match = re.search(r'Answer:\s*([A-D])', block)
            if not answer_match:
                continue
            
            correct_letter = answer_match.group(1)
            correct_option = ord(correct_letter) - ord('A')  # Convert A->0, B->1, C->2, D->3
            
            if len(options) == 4:
                questions.append({
                    'question_text': question_text,
                    'options': options,
                    'correct_option': correct_option
                })
        
        except Exception as e:
            print(f"Error parsing question block: {e}")
            continue
    
    return questions


def parse_quiz_pdf_from_bytes(pdf_bytes: bytes) -> List[Dict]:
    """
    Parse quiz questions from PDF bytes (for file upload).
    """
    import io
    questions = []
    
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    print(f"=== EXTRACTED TEXT FROM PDF ===")
    print(text[:1000])  # Print first 1000 chars
    print(f"=== END EXTRACTED TEXT ===")
    
    # Split by question numbers (Q1, Q2, etc.) - more flexible pattern
    question_blocks = re.split(r'(?=Q\d+\.)', text.strip())
    
    print(f"Found {len(question_blocks)} question blocks")
    
    for block in question_blocks:
        if not block.strip():
            continue
        
        print(f"\n=== Processing block ===")
        print(block[:200])
            
        try:
            # Extract question text - more flexible pattern
            question_match = re.search(r'Q\d+\.\s*(.+?)(?=[A-D]\))', block, re.DOTALL)
            if not question_match:
                print("Could not match question text")
                continue
            
            question_text = question_match.group(1).strip()
            print(f"Question: {question_text}")
            
            # Extract options - more flexible
            options = []
            for letter in ['A', 'B', 'C', 'D']:
                # Try multiple patterns
                option_match = re.search(rf'{letter}\)\s*(.+?)(?=(?:[A-D]\)|Answer:|Q\d+\.|$))', block, re.DOTALL)
                if option_match:
                    option_text = option_match.group(1).strip()
                    options.append(option_text)
                    print(f"Option {letter}: {option_text}")
            
            # Extract correct answer - more flexible
            answer_match = re.search(r'Answer:\s*([A-D])', block, re.IGNORECASE)
            if not answer_match:
                print("Could not match answer")
                continue
            
            correct_letter = answer_match.group(1).upper()
            correct_option = ord(correct_letter) - ord('A')  # Convert A->0, B->1, C->2, D->3
            print(f"Correct answer: {correct_letter} (index: {correct_option})")
            
            if len(options) >= 2:  # Allow at least 2 options
                # Pad with empty strings if less than 4 options
                while len(options) < 4:
                    options.append('')
                
                questions.append({
                    'question_text': question_text,
                    'options': options[:4],  # Take only first 4
                    'correct_option': correct_option
                })
                print(f"✓ Successfully parsed question")
        
        except Exception as e:
            print(f"Error parsing question block: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n=== TOTAL QUESTIONS PARSED: {len(questions)} ===")
    return questions
