import json
from scene_loader import load_scenes, get_formal_scenes, get_practice_scene
from encoder import encode_all
from scoring import compute_scores, classify
from reporter import generate_report
from self_report_scoring import score_self_report, demo_answers


def run_survey():
    scenes = load_scenes()
    practice = get_practice_scene(scenes)
    formal = get_formal_scenes(scenes)

    print("=" * 60)
    print("练习场景")
    print("=" * 60)
    print("图片：", practice["image"])
    print("指导语：", practice["instruction"])
    for i, q in enumerate(practice["questions"], 1):
        print(f"Q{i}: {q}")
    print("提示：", practice["hint"])
    print()

    for s in formal:
        print("=" * 60)
        print(f"正式场景 {s['id']}：{s['title']}")
        print("=" * 60)
        print("图片：", s["image"])
        print("指导语：", s["instruction"])
        for i, q in enumerate(s["questions"], 1):
            print(f"Q{i}: {q}")
        print("提示：", s["hint"])
        print("自评题：")
        for j, item in enumerate(s["self_report"], 1):
            print(f"  {j}. {item['text']}  [{item['dim']}]")
        print()


def main():
    run_survey()

    with open("data/sample_input.json", encoding="utf-8") as f:
        data = json.load(f)

    narratives = data["叙述"]
    state = data["状态自评"]
    ecr = data["ECR"]

    print("正在计算自评题得分...")
    scenes = load_scenes()
    answers = demo_answers()
    self_scores = score_self_report(scenes, answers)
    print("自评维度分：", json.dumps(self_scores, ensure_ascii=False))

    print("正在编码叙事...")
    narrative_results = encode_all(narratives)

    print("正在计分...")
    scores = compute_scores(narrative_results, state, ecr)
    scores["类型"] = classify(scores)
    scores.update(self_scores)

    print("正在生成报告...")
    path = generate_report(scores)

    print("完成！报告已生成：", path)
    print(json.dumps(scores, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()