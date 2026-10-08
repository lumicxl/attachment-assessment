import json
import os
from openai import OpenAI

client = OpenAI(
    api_key="sk-daab2437aec74722aae94e11647a6899",
    base_url="https://api.deepseek.com/v1"
)

MODEL = "deepseek-chat"


def load_prompt():
    with open("prompt.txt", encoding="utf-8") as f:
        return f.read()


def encode_narrative(img_id: int, text: str) -> dict:
    prompt = load_prompt().replace("{id}", str(img_id)).replace("{text}", text)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2
    )
    return json.loads(resp.choices[0].message.content)


def encode_all(narratives: list) -> list:
    results = []
    for item in narratives:
        result = encode_narrative(item["图片编号"], item["文本"])
        results.append(result)
    return results