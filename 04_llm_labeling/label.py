# -*- coding: utf-8 -*-
"""
用大模型自动打标签 Demo（无需 API Key 的模拟版）
流程：读取 data.csv -> 调用分类函数 -> 对比真实标签算准确率 -> 保存 result.csv
拿到 API Key 后，只需把 mock_classify 换成 call_qwen_api（见第 2 部分）
"""
import csv
import time

DATA_FILE = "data.csv"
RESULT_FILE = "result.csv"

# ========== 1. 模拟大模型（关键词计分，复现模型的典型行为和失败模式） ==========
POSITIVE_WORDS = ["masterpiece", "perfect", "laughed", "cried", "heartwarming",
                  "enjoy", "recommended", "best", "blew my mind", "brilliant",
                  "glued", "fantastic", "stunning"]
NEGATIVE_WORDS = ["boring", "predictable", "no sense", "wooden", "insulting",
                  "asleep", "disaster", "never get back"]

def mock_classify(text):
    """模拟模型输出。和真实模型一样：会被表面关键词误导（反讽/转折句会判错）"""
    t = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in t)
    neg = sum(1 for w in NEGATIVE_WORDS if w in t)
    time.sleep(0.3)  # 模拟 API 网络延迟
    return "正面。" if pos >= neg else "负面。"  # 平局默认正面（第10条会因此误判）

# ========== 2. 真实 API 版本（参考，需 pip install dashscope + API Key） ==========
def call_qwen_api(text):
    """
    真实调用通义千问的代码长这样（拿到 key 后取消注释即可）：

    import dashscope
    dashscope.api_key = "sk-你的key"
    prompt = (f"请判断以下影评的情感倾向，只回答'正面'或'负面'，"
              f"不要输出任何其他内容。\\n影评：{text}")
    resp = dashscope.Generation.call(
        model="qwen-turbo",
        prompt=prompt,
        temperature=0,   # 分类任务用低温，输出更稳定
    )
    return resp.output.text
    """
    raise NotImplementedError("当前为模拟模式")

# ========== 3. 输出清洗（真实模型常返回多余内容，需规整为固定标签） ==========
def clean_output(raw):
    if "正面" in raw:
        return "正面"
    if "负面" in raw:
        return "负面"
    return "未知"

# ========== 4. 主流程 ==========
def main():
    with open(DATA_FILE, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    results, correct = [], 0
    for i, row in enumerate(rows, 1):
        raw = mock_classify(row["review"])      # ← 有 key 后换成 call_qwen_api
        pred = clean_output(raw)
        is_correct = (pred == row["true_label"])
        correct += is_correct
        results.append({**row, "prediction": pred, "is_correct": is_correct})
        mark = "√" if is_correct else "×"
        print(f"[{i}/{len(rows)}] 预测: {pred} | 真实: {row['true_label']} | {mark}")

    print(f"\n准确率: {correct}/{len(rows)} = {correct / len(rows):.0%}")

    with open(RESULT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "review", "true_label",
                                               "prediction", "is_correct"])
        writer.writeheader()
        writer.writerows(results)
    print(f"已保存 {RESULT_FILE}")

if __name__ == "__main__":
    main()