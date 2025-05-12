from google import genai
from flask import current_app
import configparser
import asyncio
import time


def init_genai():

    config = configparser.ConfigParser()
    config.read('../config.ini')
    return genai.Client(api_key=config['GOOGLE_API_KEY'])

def run_async_process(coroutines):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(asyncio.gather(*coroutines))
    finally:
        loop.close()

async def get_description(books):

    genai_client = init_genai()

    def create_prompt():
        base_prompt = (
            "I need you to describe in a few phrases this group of books defined by descriptions in the format: "
            '"Book 1: description 1". The answer cannot be longer than 400 characters or contain special characters. '
            "Do not mention any of the book names. Separate the phrases by a comma and limit it to 3 phrases."
        )
        return base_prompt + "".join(f"\nBook {i}: {book.description[:300]}" for i, book in enumerate(books))

    async def generate_with_model(genai_client):
        try:
            return await genai_client.aio.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
        except Exception as e:
            current_app.logger.error(f"GenAI prompt error with {"gemini-2.0-flash-lite"}: {e}")
            return None

    now = time.time()
    prompt = create_prompt()

    response = await generate_with_model(genai_client)
    if response and response.text and len(response.text) <= 400:
        current_app.logger.info(f"Generated text with model {"gemini-2.0-flash-lite"} in {round(time.time() - now, 4)} seconds")
        return response.text

    current_app.logger.error("Attempt failed. No response generated.")
    return ""
