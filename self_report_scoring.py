def score_self_report(scenes, answers):
    dim_scores = {
        "焦虑": [], "回避": [], "安全": [],
        "亲近": [], "他人可获得性": [], "心智化": []
    }

    for s in scenes:
        if s["type"] != "formal":
            continue
        sid = s["id"]
        if sid not in answers:
            continue
        for item, score in zip(s["self_report"], answers[sid]):
            dim = item["dim"]
            if "焦虑" in dim:
                dim_scores["焦虑"].append(score)
            if "回避" in dim:
                dim_scores["回避"].append(score)
            if "安全" in dim:
                dim_scores["安全"].append(score)
            if "亲近" in dim:
                dim_scores["亲近"].append(score)
            if "他人可获得性" in dim:
                dim_scores["他人可获得性"].append(score)
            if "心智化" in dim:
                dim_scores["心智化"].append(score)

    return {k: round(sum(v) / len(v), 2) if v else 0 for k, v in dim_scores.items()}