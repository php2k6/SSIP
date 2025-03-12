import os
import time
from pdf2image import convert_from_path  # Install via: pip install pdf2image
import g4f
import g4f.Provider
#PARAMETERS
#poppler path (required for pdf2image)
poppler_path = r'C:\poppler-24.08.0\Library\bin'
#use g4f.Provider.Blackbox , g4f.Provider.PollinationsAI	
input_provider = g4f.Provider.Blackbox 
#gpt-4o, gpt-4o-mini, gpt-4 (crosscheck with the provider)
input_model= "gpt-4o"



def convert_pdf_to_images(pdf_path : str) -> list[str]:
    """
    Converts a PDF file into a list of JPEG image file paths.
    Temporary image files are created in the current directory.
    """
    try:
        pages = convert_from_path(pdf_path, poppler_path=poppler_path)
        image_paths = []
        for i, page in enumerate(pages):
            image_file = f"temp_{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{i}.jpg"
            page.save(image_file, 'JPEG')
            image_paths.append(image_file)
        return image_paths
    except Exception as e:
        print(f"Error converting PDF {pdf_path}: {e}")
        return []

def chat_completion(prompt : str, image_file : str, max_retries=5) -> str:
    """
    Calls the LLM via g4f with a system prompt for OCR and retries on rate limits.
    """
    client = g4f.Client(provider=input_provider)
    
    system_prompt = (
        "You are an OCR engine. Extract all text from the provided image as accurately as possible. "
        "Do not include any additional commentary or text (only ocr)."
    )

    retries = 0
    while retries < max_retries:
        try:
            with open(image_file, "rb") as img_file:
                images = [[img_file, os.path.basename(image_file)]]
                model = input_model
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                response = client.chat.completions.create(messages, model, images=images)
                return response.choices[0].message.content  # Return extracted text

        except g4f.errors.ResponseStatusError as e:
            if "429 Too Many Requests" in str(e):
                wait_time = (5 + retries * 2)  # Increase delay gradually (5s, 7s, 9s, etc.)
                print(f"Rate limit hit. Retrying in {wait_time} seconds... ({retries+1}/{max_retries})")
                time.sleep(wait_time)
                retries += 1
            else:
                raise  # Raise other errors immediately

    raise Exception("Failed after multiple retries due to rate limits.")

def ocr_extraction(file_list : list[str], prompt="Extract text from image") -> str:
    """
    For a list of file paths (images or PDFs), this function extracts text using LLM OCR.
    Returns the concatenated extracted text.
    """
    full_text = ""
    for file_path in file_list:
        ext = os.path.splitext(file_path)[1].lower()
        image_files = []
        if ext == ".pdf":
            image_files = convert_pdf_to_images(file_path)
        elif ext in [".jpg", ".jpeg", ".png"]:
            image_files = [file_path]
        else:
            print(f"Unsupported file type: {file_path}")
            continue

        for image in image_files:
            print(f"Processing image: {image}")
            extracted_text = chat_completion(prompt, image)
            full_text += extracted_text + "\n"

            # Remove temporary image files if created during PDF conversion
            if file_path.lower().endswith(".pdf") and image.startswith("temp_"):
                try:
                    os.remove(image)
                except Exception as e:
                    print(f"Error removing temporary file {image}: {e}")
                    
    return full_text

if __name__ == "__main__":
    files = [""]
    result = ocr_extraction(files)
    print("Extracted Text:\n", result)
