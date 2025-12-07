from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

from .agent import run_agent

app = FastAPI()

# 方便你以后接前端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...), query: str = Form(...)):
    """
    接收：
      - CSV 文件
      - 自然语言 query

    返回：
      - LLM 生成的 plan
      - 执行结果（表格预览 + 可选图表路径）
    """
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    res = run_agent(df, query)
    return res


@app.get("/")
def healthcheck():
    return {"status": "ok"}
