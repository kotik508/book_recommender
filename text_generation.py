from google import genai


def init_genai():
    return genai.Client(api_key="AIzaSyABaUtCViwGVH6PRWOKZxPjfAkyqdO-_Fo")

def create_prompt(book_descs: list):
    prompt = ('I need you to describe in two sentences this group of books defined by descriptions in the format: '
              '"Book 1: description 1". Do not mention any of the book names')

    for i, desc in enumerate(book_descs, 1):
        prompt += f"\nBook {i}: {desc}"

    return prompt

def get_description(client, prompt: list):
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents = prompt
    )
    return response.text