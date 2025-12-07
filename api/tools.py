import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Dict, Any, List

# 确保图像不弹窗显示
plt.switch_backend("Agg")

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def execute_steps(df: pd.DataFrame, plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    按照 plan["steps"] 顺序执行操作，返回结果和（可选）图表路径。
    """
    steps: List[Dict[str, Any]] = plan.get("steps", [])
    current_df = df.copy()
    chart_path = None

    for step in steps:
        op = step.get("operation")
        params = step.get("params", {})

        if op == "filter":
            current_df = op_filter(current_df, params)
        elif op == "aggregate":
            current_df = op_aggregate(current_df, params)
        elif op == "sort":
            current_df = op_sort(current_df, params)
        elif op == "describe":
            # describe 会覆盖 current_df 为 summary，这里简单实现
            current_df = op_describe(current_df, params)
        elif op == "visualize":
            chart_path = op_visualize(current_df, params)
        elif op == "error":
            return {"error": params.get("reason", "Unknown error")}
        else:
            return {"error": f"Unsupported operation: {op}"}

    # 返回信息：表格数据 + 图表路径
    return {
        "data_preview": current_df.head(50).to_dict(orient="records"),
        "chart_path": chart_path,
    }


def op_filter(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    """
    支持两种用法：
    1) 列过滤: { "column": "score", "op": ">", "value": 90 }
    2) 行过滤: { "condition": "row_index == 0" }
    """

    # 用例 2：LLM 选择 Top 1 / First row
    if "condition" in params:
        cond = params["condition"]
        if cond == "row_index == 0":
            return df.head(1)
        # 更多条件可以继续加
        return df

    # 用例 1：普通列过滤
    col = params.get("column")
    op = params.get("op")
    val = params.get("value")

    if col not in df.columns:
        return df

    if op == ">":
        return df[df[col] > val]
    elif op == "<":
        return df[df[col] < val]
    elif op == "==":
        return df[df[col] == val]
    elif op == ">=":
        return df[df[col] >= val]
    elif op == "<=":
        return df[df[col] <= val]
    else:
        return df


def op_aggregate(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    """
    params:
      { "group_by": "class", "agg_column": "score", "agg_func": "mean" }
    """
    group_by = params.get("group_by")
    agg_column = params.get("agg_column")
    agg_func = params.get("agg_func", "mean")

    if group_by not in df.columns or agg_column not in df.columns:
        return df

    grouped = df.groupby(group_by)[agg_column]
    if agg_func == "mean":
        res = grouped.mean().reset_index()
    elif agg_func == "sum":
        res = grouped.sum().reset_index()
    elif agg_func == "max":
        res = grouped.max().reset_index()
    elif agg_func == "min":
        res = grouped.min().reset_index()
    else:
        # 默认 mean
        res = grouped.mean().reset_index()

    # 统一把 agg_column 的列名保持为原名
    res.rename(columns={agg_column: agg_column}, inplace=True)
    return res


def op_sort(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    """
    params:
      { "by": "score", "ascending": false }
    """
    by = params.get("by")
    ascending = params.get("ascending", True)
    if by not in df.columns:
        return df
    return df.sort_values(by=by, ascending=ascending)


def op_describe(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    """
    params:
      { "columns": ["score"] }  # 可选
    """
    cols = params.get("columns")
    if cols:
        valid_cols = [c for c in cols if c in df.columns]
        if not valid_cols:
            return df
        return df[valid_cols].describe().reset_index()
    else:
        return df.describe().reset_index()


def op_visualize(df: pd.DataFrame, params: Dict[str, Any]) -> str:
    """
    params:
      { "type": "bar", "x": "class", "y": "score" }
    """
    chart_type = params.get("type", "bar")
    x = params.get("x")
    y = params.get("y")

    if x not in df.columns or y not in df.columns:
        return None

    plt.figure(figsize=(6, 4))
    if chart_type == "bar":
        plt.bar(df[x], df[y])
    elif chart_type == "line":
        plt.plot(df[x], df[y])
    else:
        plt.bar(df[x], df[y])

    plt.xlabel(x)
    plt.ylabel(y)
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "chart.png")
    plt.savefig(path)
    plt.close()
    return path
