from ocr_extraction import ocr_extraction
from text_cleanup import clean_text

def main():
    # Extract and clean the question paper
    print("Extracting OCR text from qn_paper.pdf (questions)...")
    raw_question_paper_text = ocr_extraction(["tests/example_qn_paper_mini.pdf"])
    print("Cleaning qn paper")
    cleaned_question_paper = clean_text(question_paper_text=raw_question_paper_text, mode="question_paper")  
    print("raw Answers:\n", raw_question_paper_text)
    print("Cleaned Question Paper:\n", cleaned_question_paper)
    
    # Extract and clean the answer sheet using the question paper
    print("Extracting OCR text from English_core.pdf (answers)...")
    raw_answers_text = ocr_extraction(["example_answer_sheet.pdf"])
    cleaned_answers = clean_text(raw_answers_text, cleaned_question_paper)
    print("raw Answers:\n", raw_answers_text)
    print("Cleaned Answers:\n", cleaned_answers)

if __name__ == "__main__":
    main()
