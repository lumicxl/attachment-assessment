import numpy as np


def compute_scores(narrative_results: list, state: dict, ecr: dict) -> dict:
    d1 = np.mean([x["各维度评分"]["1_分离痛苦"]["分数"] for x in narrative_results])
    d2 = np.mean([x["各维度评分"]["2_亲近寻求"]["分数"] for x in narrative_results])
    d3 = np.mean([x["各维度评分"]["3_他人可获得性信念"]["分数"] for x in narrative_results])
    d4 = np.mean([x["各维度评分"]["4_心智化水平"]["分数"] for x in narrative_results])
    d5 = np.mean([x["各维度评分"]["5_结局整合与恢复"]["分数"] for x in narrative_results])
    d6a = np.mean([x["各维度评分"]["6_防御加工"]["6a_去激活"]["分数"] for x in narrative_results])
    d6b = np.mean([x["各维度评分"]["6_防御加工"]["6b_认知断开"]["分数"] for x in narrative_results])
    d6c = np.mean([x["各维度评分"]["6_防御加工"]["6c_分离系统"]["分数"] for x in narrative_results])
    d6 = (d6a + d6b + d6c) / 3

    anxiety = 0.4 * ecr["焦虑"] + 0.3 * (d1 + d6c) / 2 + 0.3 * state["状态焦虑"]
    avoidance = 0.4 * ecr["回避"] + 0.3 * (d6a + d6b) / 2 + 0.3 * state["状态回避"]
    safety = 0.4 * state["状态安全"] + 0.3 * d3 + 0.3 * d5
    fear = 0.5 * (anxiety + avoidance) - 0.3 * safety

    return {
        "分离痛苦": round(d1, 2),
        "亲近寻求": round(d2, 2),
        "他人可获得性": round(d3, 2),
        "心智化": round(d4, 2),
        "结局整合": round(d5, 2),
        "防御加工": round(d6, 2),
        "焦虑分": round(anxiety, 2),
        "回避分": round(avoidance, 2),
        "安全分": round(safety, 2),
        "恐惧分": round(fear, 2)
    }


def classify(scores: dict) -> str:
    a, v = scores["焦虑分"], scores["回避分"]
    if a < 3 and v < 3:
        return "安全型"
    elif a >= 3 and v < 3:
        return "焦虑型"
    elif a < 3 and v >= 3:
        return "回避型"
    else:
        return "恐惧型"