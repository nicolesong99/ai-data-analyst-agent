# AI Data Analyst Agent

An AI-powered data analysis agent that converts natural-language questions into
structured plans and executes them using pandas, returning tabular results and charts.

## Features

- Upload a CSV file.
- Ask questions in natural language (e.g., "Which class has the highest average score?").
- LLM generates a JSON "plan" (filter / aggregate / sort / describe / visualize).
- Python executes the plan deterministically (no direct code execution from the model).
- Returns a data preview and an optional chart path.

## Tech Stack

- Python, FastAPI
- pandas, matplotlib
- OpenAI API (or any LLM with a chat completion interface)

## Run Locally

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="YOUR_KEY"
uvicorn api.main:app --reload
```
