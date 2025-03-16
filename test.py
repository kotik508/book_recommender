import asyncio
from website.text_generation import init_genai

genai_client = init_genai()

async def get_answers(prompt):

    response = await genai_client.aio.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents = prompt
    )

    return response

async def question():
    summaries = {}

    summaries[0], summaries[1], summaries[2], summaries[3] = await asyncio.gather(
        get_answers("What is the name of the first Harry Potter book"),
        get_answers("What is the name of the second Harry Potter book"),
        get_answers("What is the name of the third Harry Potter book"),
        get_answers("What is the name of the fourth Harry Potter book")
    )

    print(summaries)
