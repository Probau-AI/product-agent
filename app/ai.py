import os

from dotenv import load_dotenv
from openai import OpenAI

from app.models import Filters


load_dotenv()


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_KEY"),
)


PROMPT = """
Extract parameters from the users sentence. Convert units to cm. integers and put into output. 
Leave fields as None if not specified. If user includes some product name, brand also include category in product_name
Like if it asks 'Give me sofas names JENNY', then product_name must be 'sofas JENNY'.
As for material, shape, style, textile, delivery and pattern please look into Enums and match values to those
enums. If color provided pattern must stay None
"""


def get_filters_from_sentence(sentence: str) -> Filters:
    completion = client.beta.chat.completions.parse(
        model="google/gemini-flash-1.5",
        messages=[
            {"role": "system","content": PROMPT},
            {"role": "user", "content": sentence},
        ],
        response_format=Filters,
    )

    message = completion.choices[0].message
    if message.refusal:
        raise ValueError(message.refusal)

    return message.parsed



if __name__ == '__main__':
    sentence = "Give sofas from JENNY with width 1.6 meters white color"
    filters = get_filters_from_sentence(sentence)
    print(filters)
