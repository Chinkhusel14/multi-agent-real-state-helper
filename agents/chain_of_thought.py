import json
from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate

async def analyze_apartments(user_request: str, apartments: list[str]) -> dict:
    prompt_template = """
User request:
{user_request}

Available apartments:
{apartments}

Please recommend 5 best apartments based on the user request.

Return ONLY JSON in this format :

{{
  "recommendations": [
    {{
      "title": "Apartment title or description from real data",
      "reason": "Why this apartment is recommended in mongolian language"
    }},
    ...
  ]
}}
"""
    prompt = PromptTemplate.from_template(prompt_template)
    apartments_str = "\n".join(apartments)
    formatted_prompt = prompt.format(user_request=user_request, apartments=apartments_str)

    llm = ChatTogether(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        together_api_key="d9364b05d9d35fbb5f21c846b5bcda35fafecd3be705685ead0004450bf3c9b4"
    )

    response_text = await llm.ainvoke(formatted_prompt)
    
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        data = {"error": "LLM did not return valid JSON", "raw": response_text}

    return data
