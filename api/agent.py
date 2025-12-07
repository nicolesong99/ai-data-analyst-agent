import os
import json
from typing import Dict, Any

import pandas as pd
from openai import OpenAI

from .prompts import AGENT_PROMPT
from .tools import execute_steps

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_prompt(df: pd.DataFrame, query: str) -> str:
    columns = []
    for col in df.columns:
        columns.append(f"- {col}: {str(df[col].dtype)}")

    schema_str = "\n".join(columns)
    prompt = AGENT_PROMPT.replace("<<COLUMNS>>", schema_str)
    prompt += f"\n\nUser query: {query}\nPlan:"
    return prompt


def call_llm(prompt: str) -> Dict[str, Any]:
    """
    调用 LLM，返回 JSON plan。
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # 可以换成别的模型
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    content = resp.choices[0].message.content
    # content 是 JSON 字符串
    try:
        plan = json.loads(content)
    except json.JSONDecodeError:
        plan = {
            "steps": [
                {
                    "operation": "error",
                    "params": {"reason": "LLM did not respond with valid JSON."},
                }
            ]
        }
    return plan


def run_agent(df: pd.DataFrame, query: str) -> Dict[str, Any]:
    prompt = build_prompt(df, query)
    plan = call_llm(prompt)
    result = execute_steps(df, plan)
    return {
        "plan": plan,
        "result": result,
    }
