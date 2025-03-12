from g4f.client import Client
import g4f
import g4f.Provider
from ocr_extraction import ocr_extraction
from text_cleanup import clean_text
client = Client()
#PARAMETERS
#use g4f.Provider.Blackbox , g4f.Provider.PollinationsAI, etc
test_provider =g4f.Provider.FreeGpt			
#gpt-4o, gpt-4o-mini, gpt-4 (crosscheck with the provider),etc
test_model = "gemini-1.5-pro"
test_prompt = "language english what model are you"

response = client.chat.completions.create(
    model=test_model,
    messages=[{"role": "user", "content": test_prompt}],
    web_search=False,
    provider=test_provider
)
print(response.choices[0].message.content)