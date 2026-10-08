import json
from jinja2 import Template


# ================== 人物库 ==================
FIGURE_LIBRARY = {
    "安全型": [
        {"name": "达西先生《傲慢与偏见》", "keywords": "克制、忠诚、能修复关系",
         "match": {"安全分": 3, "结局整合": 2, "他人可获得性": 2}},
        {"name": "卢娜·洛夫古德《哈利·波特》", "keywords": "独立、信任朋友、不随波逐流",
         "match": {"安全分": 3, "他人可获得性": 3}},
        {"name": "贾母《红楼梦》", "keywords": "情感厚实、家族锚点",
         "match": {"安全分": 3, "心智化": 2}},
        {"name": "阿甘《阿甘正传》", "keywords": "单纯、忠诚、不记恨",
         "match": {"安全分": 3, "分离痛苦": 0}},
        {"name": "山姆·甘姆吉《指环王》", "keywords": "忠诚、陪伴、稳定",
         "match": {"安全分": 3, "亲近寻求": 2}},
        {"name": "伊丽莎白·班纳特《傲慢与偏见》", "keywords": "自尊、清醒、能沟通",
         "match": {"安全分": 3, "心智化": 3}},
        {"name": "阿蒂克斯·芬奇《杀死一只知更鸟》", "keywords": "公正、稳定、有原则",
         "match": {"安全分": 3, "心智化": 2}},
        {"name": "莫妮卡《老友记》", "keywords": "温暖、照顾人、稳定",
         "match": {"安全分": 3, "亲近寻求": 2}},
        {"name": "陈芸《浮生六记》", "keywords": "温柔、信任、能共处",
         "match": {"安全分": 3, "结局整合": 2}},
        {"name": "特蕾莎修女（历史人物）", "keywords": "稳定、利他、信任",
         "match": {"安全分": 3, "他人可获得性": 3}},
    ],
    "焦虑型": [
        {"name": "林黛玉《红楼梦》", "keywords": "敏感、在意回应、易波动",
         "match": {"焦虑分": 3, "分离痛苦": 3, "亲近寻求": 2}},
        {"name": "希斯克利夫《呼啸山庄》", "keywords": "执念、分离痛苦极强",
         "match": {"焦虑分": 3, "分离痛苦": 3}},
        {"name": "盖茨比《了不起的盖茨比》", "keywords": "理想化、反复追寻",
         "match": {"焦虑分": 3, "亲近寻求": 3}},
        {"name": "安娜·卡列尼娜《安娜·卡列尼娜》", "keywords": "热烈、害怕失去",
         "match": {"焦虑分": 3, "分离系统": 2}},
        {"name": "罗密欧《罗密欧与朱丽叶》", "keywords": "冲动、热烈、依恋强",
         "match": {"焦虑分": 3, "亲近寻求": 3}},
        {"name": "奥菲莉亚《哈姆雷特》", "keywords": "依恋、脆弱、易被忽视",
         "match": {"焦虑分": 3, "分离痛苦": 2}},
        {"name": "白流苏《倾城之恋》", "keywords": "反复试探、需要确认",
         "match": {"焦虑分": 3, "他人可获得性": 1}},
        {"name": "钱德勒《老友记》", "keywords": "自嘲、怕被抛弃、用幽默掩饰",
         "match": {"焦虑分": 3, "防御加工": 2}},
        {"name": "晴雯《红楼梦》", "keywords": "敏感、要强、在意回应",
         "match": {"焦虑分": 3, "分离痛苦": 2}},
    ],
    "回避型": [
        {"name": "圣地亚哥《老人与海》", "keywords": "孤独、坚忍、独自承受",
         "match": {"回避分": 3, "亲近寻求": 0}},
        {"name": "布鲁斯·韦恩《蝙蝠侠》", "keywords": "情感克制、独自承担",
         "match": {"回避分": 3, "去激活": 3}},
        {"name": "薛宝钗《红楼梦》", "keywords": "理性、克制、保持距离",
         "match": {"回避分": 3, "认知断开": 2}},
        {"name": "斯内普《哈利·波特》", "keywords": "压抑、隐忍、不表达",
         "match": {"回避分": 3, "去激活": 3}},
        {"name": "达西先生（前期）《傲慢与偏见》", "keywords": "疏离、克制、不轻易靠近",
         "match": {"回避分": 3, "心智化": 2}},
        {"name": "简·爱（前期）《简·爱》", "keywords": "自尊、防御、保持距离",
         "match": {"回避分": 3, "认知断开": 2}},
        {"name": "福尔摩斯《福尔摩斯》", "keywords": "理性、疏离、独自思考",
         "match": {"回避分": 3, "心智化": 3}},
        {"name": "谢尔顿《生活大爆炸》", "keywords": "情感迟钝、需要空间",
         "match": {"回避分": 3, "认知断开": 3}},
        {"name": "妙玉《红楼梦》", "keywords": "孤高、疏离、保持距离",
         "match": {"回避分": 3, "去激活": 2}},
        {"name": "海明威（历史人物）", "keywords": "硬汉、独立、情感内敛",
         "match": {"回避分": 3, "去激活": 3}},
    ],
    "恐惧型": [
        {"name": "凯瑟琳·恩肖《呼啸山庄》", "keywords": "既爱又逃、撕裂",
         "match": {"焦虑分": 3, "回避分": 3}},
        {"name": "直子《挪威的森林》", "keywords": "渴望亲密又无法承受",
         "match": {"焦虑分": 3, "回避分": 3}},
        {"name": "哈姆雷特《哈姆雷特》", "keywords": "犹豫、自我拉扯",
         "match": {"焦虑分": 2, "回避分": 3}},
        {"name": "拉斯柯尔尼科夫《罪与罚》", "keywords": "孤立又渴望连接",
         "match": {"焦虑分": 3, "回避分": 2}},
        {"name": "格里高尔《变形记》", "keywords": "被弃感+自我隔离",
         "match": {"焦虑分": 3, "回避分": 3}},
        {"name": "大庭叶藏《人间失格》", "keywords": "恐惧亲密、自我否定",
         "match": {"焦虑分": 3, "回避分": 3}},
        {"name": "曹七巧《金锁记》", "keywords": "渴望爱又伤害爱",
         "match": {"焦虑分": 3, "回避分": 2}},
        {"name": "程蝶衣《霸王别姬》", "keywords": "投入又怕受伤、身份拉扯",
         "match": {"焦虑分": 3, "回避分": 3}},
        {"name": "豪斯医生《豪斯医生》", "keywords": "推开人又需要人",
         "match": {"焦虑分": 2, "回避分": 3}},
    ],
}


# ================== 工具 ==================
def classify(scores):
    a, v = scores["焦虑分"], scores["回避分"]
    if a < 3 and v < 3:
        return "安全型"
    elif a >= 3 and v < 3:
        return "焦虑型"
    elif a < 3 and v >= 3:
        return "回避型"
    else:
        return "恐惧型"


def describe(val):
    if val == "未测":
        return "未测"
    if val < 3:
        return f"{val}（偏低）"
    elif val < 5:
        return f"{val}（中等）"
    else:
        return f"{val}（偏高）"


def match_figures(scores, top_n=3):
    atype = classify(scores)
    candidates = FIGURE_LIBRARY[atype]

    def score_figure(fig):
        s = 0
        for k, weight in fig["match"].items():
            s += weight * scores.get(k, 0)
        return s

    ranked = sorted(candidates, key=score_figure, reverse=True)
    return atype, ranked[:top_n]


# ================== 报告模板 ==================
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>状态性依恋画像报告</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body { font-family: "Microsoft YaHei", sans-serif; max-width: 800px; margin: 40px auto; color: #2c3e50; }
h1 { color: #2c3e50; }
.card { background: #f8f9fa; border-radius: 12px; padding: 20px; margin: 16px 0; }
.figure { margin: 8px 0; padding: 10px; background: #fff; border-left: 4px solid #4a90d9; }
canvas { max-width: 100%; }
.small { color: #7f8c8d; font-size: 0.9em; }
</style>
</head>
<body>
<h1>你的状态性依恋画像</h1>

<div class="card">
  <h2>核心模式：{{ type }}</h2>
  <p>{{ type_desc }}</p>
</div>

<div class="card">
  <h2>与你相似的人物</h2>
  {% for fig in figures %}
  <div class="figure">
    <strong>{{ fig.name }}</strong><br>
    <span>{{ fig.keywords }}</span>
  </div>
  {% endfor %}
  <p class="small"><em>匹配理由：你的{{ match_reason }}。</em></p>
</div>

<div class="card">
  <h2>六维度雷达</h2>
  <canvas id="narrativeRadar" height="300"></canvas>
</div>

<div class="card">
  <h2>效标雷达</h2>
  <canvas id="criteriaRadar" height="300"></canvas>
</div>

<div class="card">
  <h2>声学特征</h2>
  {% if acoustics %}
  <table style="width:100%; border-collapse: collapse;">
    <tr><th align="left">场景</th><th align="right">时长(s)</th><th align="right">F0均值</th><th align="right">F0波动</th><th align="right">语速</th><th align="right">停顿次数</th></tr>
    {% for a in acoustics %}
    <tr>
      <td>{{ a.scene }}</td>
      <td align="right">{{ a.duration }}</td>
      <td align="right">{{ a.f0_mean }}</td>
      <td align="right">{{ a.f0_sd }}</td>
      <td align="right">{{ a.speech_rate }}</td>
      <td align="right">{{ a.pause_count }}</td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p class="small">本次未采集到声学特征。</p>
  {% endif %}
</div>

<div class="card">
  <h2>效标指标</h2>
  {% for name, val in criteria.items() %}
  <p>{{ name }}：{{ val }}</p>
  {% endfor %}
</div>

<div class="card">
  <h2>建议</h2>
  <ul>
    <li>{{ tip1 }}</li>
    <li>{{ tip2 }}</li>
    <li>{{ tip3 }}</li>
  </ul>
</div>

<script>
const narrativeCtx = document.getElementById('narrativeRadar');
new Chart(narrativeCtx, {
  type: 'radar',
  data: {
    labels: {{ narrative_labels | safe }},
    datasets: [{
      label: '叙事维度',
      data: {{ narrative_values | safe }},
      backgroundColor: 'rgba(74, 144, 217, 0.2)',
      borderColor: 'rgba(74, 144, 217, 1)',
      borderWidth: 2
    }]
  },
  options: { scales: { r: { min: 0, max: 3, ticks: { stepSize: 1 } } } }
});

const criteriaCtx = document.getElementById('criteriaRadar');
new Chart(criteriaCtx, {
  type: 'radar',
  data: {
    labels: {{ criteria_labels | safe }},
    datasets: [{
      label: '效标指标',
      data: {{ criteria_values | safe }},
      backgroundColor: 'rgba(217, 144, 74, 0.2)',
      borderColor: 'rgba(217, 144, 74, 1)',
      borderWidth: 2
    }]
  },
  options: { scales: { r: { min: 0, max: 7, ticks: { stepSize: 1 } } } }
});
</script>
</body>
</html>
"""


TYPE_DESC = {
    "安全型": "你能靠近，也能独处；关系波动后能较快回稳。",
    "焦虑型": "你很在意回应，容易在关系里反复确认“你还在吗”。",
    "回避型": "你习惯自己扛，靠近太快时反而想退一步。",
    "恐惧型": "你既渴望靠近，又害怕受伤，关系像潮水一样忽近忽远。"
}

TIPS = {
    "安全型": [
        "继续保持开放沟通，你的稳定是关系里的锚。",
        "在对方波动时，你的平静本身就是支持。",
        "记得照顾自己的需要，不必总是做那个稳住的人。"
    ],
    "焦虑型": [
        "识别焦虑信号：反复确认时，先给自己10分钟。",
        "练习稳定动作：写下“我此刻需要什么”。",
        "关系沟通：用“我感到……我需要……”代替“你为什么……”。"
    ],
    "回避型": [
        "识别退缩信号：想退一步时，先告诉自己“我可以待一会儿再决定”。",
        "练习小步靠近：从分享一件小事开始。",
        "关系沟通：用“我需要一点空间，但我还在”代替沉默。"
    ],
    "恐惧型": [
        "识别拉扯信号：想追又想逃时，先停下来呼吸。",
        "练习安全节奏：靠近一点，退一点，找到自己的速度。",
        "关系沟通：告诉对方“我有时会想退，但那不代表我不在乎”。"
    ]
}


# ================== 主函数 ==================
def generate_report(scores, acoustics_data=None, out_path="report.html"):
    atype, figures = match_figures(scores)
    scores["类型"] = atype

    reason_map = {
        "安全型": "安全分、结局整合、他人可获得性较高",
        "焦虑型": "焦虑分、分离痛苦、亲近寻求较高",
        "回避型": "回避分、去激活较高，亲近寻求较低",
        "恐惧型": "焦虑分与回避分同时较高，分离系统与认知断开明显",
    }

    criteria = {
        "社会赞许性": describe(scores.get("社会赞许性", "未测")),
        "认知重评": describe(scores.get("认知重评", "未测")),
        "表达抑制": describe(scores.get("表达抑制", "未测")),
        "拒绝敏感性": describe(scores.get("拒绝敏感性", "未测")),
        "神经质": describe(scores.get("神经质", "未测")),
    }

    narrative_labels = ["分离痛苦", "亲近寻求", "他人可获得性", "心智化", "结局整合", "防御加工"]
    narrative_values = [
        scores.get("分离痛苦", 0), scores.get("亲近寻求", 0),
        scores.get("他人可获得性", 0), scores.get("心智化", 0),
        scores.get("结局整合", 0), scores.get("防御加工", 0)
    ]

    criteria_labels = ["社会赞许性", "认知重评", "表达抑制", "拒绝敏感性", "神经质"]
    criteria_values = [
        scores.get("社会赞许性", 0), scores.get("认知重评", 0),
        scores.get("表达抑制", 0), scores.get("拒绝敏感性", 0),
        scores.get("神经质", 0)
    ]

    acoustics = []
    if acoustics_data:
        scene_names = {
            1: "亲密接触", 2: "未来见面", 3: "车站告别",
            4: "困境求助", 5: "人际冲突", 6: "社交旁观"
        }
        for sid, feats in acoustics_data.items():
            if not feats:
                continue
            acoustics.append({
                "scene": scene_names.get(sid, f"场景{sid}"),
                "duration": feats.get("duration", ""),
                "f0_mean": feats.get("f0_mean", ""),
                "f0_sd": feats.get("f0_sd", ""),
                "speech_rate": feats.get("speech_rate", ""),
                "pause_count": feats.get("pause_count", ""),
            })

    t = Template(REPORT_TEMPLATE)
    html = t.render(
        type=atype,
        type_desc=TYPE_DESC[atype],
        figures=figures,
        match_reason=reason_map[atype],
        criteria=criteria,
        narrative_labels=json.dumps(narrative_labels, ensure_ascii=False),
        narrative_values=json.dumps(narrative_values),
        criteria_labels=json.dumps(criteria_labels, ensure_ascii=False),
        criteria_values=json.dumps(criteria_values),
        acoustics=acoustics,
        tip1=TIPS[atype][0],
        tip2=TIPS[atype][1],
        tip3=TIPS[atype][2]
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path