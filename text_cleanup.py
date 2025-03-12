import g4f
import g4f.Provider
import time
#PARAMETERS
#use g4f.Provider.Blackbox , g4f.Provider.PollinationsAI	
input_provider = g4f.Provider.Blackbox	
#gpt-4o, gpt-4o-mini, gpt-4 (crosscheck with the provider)
input_model = "deepseek-v3"
def clean_text(ocr_text: str = None , question_paper_text: str =None , mode="answer_sheet", max_retries : int = 5) -> str:
    """
    Cleans and formats text based on provided instructions.
    
    Parameters:
    - ocr_text (str): The raw text output from OCR (only required in "answer_sheet" mode).
    - question_paper_text (str): The text of the question paper, used to match answers (only in "answer_sheet" mode).
    - mode (str): "answer_sheet" for cleaning answer sheets or "question_paper" for extracting clean questions.
    - max_retries (int): Maximum number of retries in case of rate limits or network issues.

    Returns:
    - cleaned_text (str): The processed and formatted text.
    """
    client = g4f.Client(provider=input_provider)
    model = input_model

    # Ensure required parameters are provided based on the mode
    if mode == "answer_sheet":
        if not ocr_text:
            raise ValueError("Missing 'ocr_text' for answer_sheet mode.")
        if not question_paper_text:
            raise ValueError("Missing 'question_paper_text' for answer_sheet mode.")

        system_prompt = (
            "You are an assistant that cleans and structures OCR-extracted answer sheets. Follow these rules:\n"
            "- Do not merge two different answers.\n"
            "- Leave exactly one blank line after each question but *no* extra lines for sub-questions.\n"
            "- Remove any markdown formatting like *bold* or _italic_.\n"
            "- Use the question paper to match answers correctly, ensuring numbering is accurate.\n"
            "- Be very careful with formulas, equations, and tables to keep formatting correct.\n"
            "- Add number markers if none are available by checking question and answer.\n"
            "- Include question/answer pairs in the output.\n"
            "-*Do not include any additional commentary or text (only clean text)*.\n"
            "-for subquestions - group them into one entire answer\n"
            "if number are missing use qnpaper to give it a number by checking ans context and qn context\n"
            "-dont get confused with subquestion or OR questions. for that look into qn paper first then answer sheet\n"
            "-include mcqs also "
        )

        user_prompt = (
            f"Question Paper:\n{question_paper_text}\n\n"
            f"OCR Text:\n{ocr_text}\n\n"
            "Please clean and format the OCR text based on the above instructions."
        )

    elif mode == "question_paper":
        if not question_paper_text:
            raise ValueError("Missing 'question_paper_text' for question_paper mode.")

        system_prompt = (
            "You are an assistant that extracts only the questions and marks from a given question paper.\n"
            "- Remove all instructions, headings, and unnecessary text.\n"
            "- Keep only question numbers, question text, and the marks assigned to each question.\n"
            "- Ensure formatting is clean and structured.\n"
            "-Do not include any additional commentary or text (only clean text)\n"
            "-Remove any formatting like *bold* or _italic_. \n"
            "- Be very careful with formulas, equations, and tables to keep formatting correct.\n"
            "-include mcqs also, append marks at the end of qn in brackets (marks-)\n"
            "-include all QUESTIONS DONT FORGET any. carefull with subquestions"
        )

        user_prompt = f"Extract and clean the questions and marks from the following:\n\n{question_paper_text}"

    else:
        raise ValueError("Invalid mode. Choose either 'answer_sheet' or 'question_paper'.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    retries = 0
    while retries < max_retries:
        try:
            response = client.chat.completions.create(messages=messages, model=model)
            return response.choices[0].message.content  # Return cleaned text

        except g4f.errors.ResponseStatusError as e:
            if "429 Too Many Requests" in str(e):
                wait_time = 5 + retries * 2  # Keep wait time as 5s, 7s, 9s, etc.
                print(f"Rate limit hit. Retrying in {wait_time} seconds... ({retries+1}/{max_retries})")
                time.sleep(wait_time)
                retries += 1
            else:
                print(f"Unexpected API error: {e}")
                raise  # Raise other errors immediately

        except (ConnectionError, TimeoutError) as e:
            wait_time = 5 + retries * 2  # Retry on network failures with same delay strategy
            print(f"Network issue ({e}). Retrying in {wait_time} seconds... ({retries+1}/{max_retries})")
            time.sleep(wait_time)
            retries += 1

        except Exception as e:
            print(f"Unexpected error: {e}")
            raise  # Stop execution for unknown issues

    raise Exception("Failed after multiple retries due to rate limits or network issues.")