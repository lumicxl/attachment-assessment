import streamlit as st
import json
import os
from datetime import datetime

from scene_loader import load_scenes, get_formal_scenes, get_practice_scene
from encoder import encode_all
from scoring import compute_scores, classify
from reporter import generate_report
from self_report_scoring import score_self_report

from db import (
    init_db, upsert_subject, save_session,
    save_narrative, save_self_report, save_acoustics
)
from acoustics import extract_features


st.set_page_config(page_title="成人状态性依恋测评", layout="centered")
init_db()

st.title("成人状态性依恋测评")

os.makedirs("data/audio", exist_ok=True)


def transcribe(audio_bytes, filename):
    audio_path = os.path.join("data/audio", filename)
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language="zh")
        return result["text"]
    except Exception:
        return ""


if "stage" not in st.session_state:
    st.session_state.stage = "consent"
    st.session_state.scene_idx = 0
    st.session_state.answers = {}
    st.session_state.narratives = {}
    st.session_state.state_self = {}
    st.session_state.recovery = {}
    st.session_state.ecr = {}
    st.session_state.criterion = {}
    st.session_state.baseline = ""
    st.session_state.audio_paths = {}
    st.session_state.baseline_audio_path = ""
    st.session_state.practice_audio_path = ""
    st.session_state.acoustics = {}
    st.session_state.subject_code = ""
    st.session_state.gender = ""
    st.session_state.age = 20
    st.session_state.identity = ""
    st.session_state.relationship = ""


# ========== 阶段1：知情同意 ==========
if st.session_state.stage == "consent":
    st.header("知情同意")
    st.write("""
    本研究旨在了解人们在亲密关系情境中的即时反应模式。
    您将观看6张图片，并围绕每张图片进行1-2分钟语音叙述，
    随后填写几份自评问卷。全程约25-30分钟。

    您的语音将被录音并转写为文字，用于科研分析。
    所有数据将匿名化处理，仅用于研究目的。
    您可以随时退出，不影响任何权益。
    """)
    agree = st.checkbox("我已阅读并同意")
    if agree and st.button("开始测评"):
        st.session_state.stage = "subject_id"
        st.rerun()


# ========== 阶段2：被试信息 ==========
elif st.session_state.stage == "subject_id":
    st.header("被试信息")
    subject_code = st.text_input("被试编号（如 P001）", value=st.session_state.subject_code)
    gender = st.selectbox("性别", ["男", "女", "其他/不愿透露"])
    age = st.number_input("年龄", 18, 80, 20)
    identity = st.selectbox("身份", ["在校大学生", "在职人员", "其他"])
    relationship = st.selectbox("目前恋爱状态", ["单身", "恋爱中", "已婚", "离异/丧偶"])

    if st.button("下一步"):
        st.session_state.subject_code = subject_code
        st.session_state.gender = gender
        st.session_state.age = age
        st.session_state.identity = identity
        st.session_state.relationship = relationship
        st.session_state.stage = "baseline"
        st.rerun()


# ========== 阶段3：基线录音 ==========
elif st.session_state.stage == "baseline":
    st.header("基线录音")
    st.write("请用30秒左右，说说今天早上从起床到现在你做了什么。自然说话即可。")

    audio = st.audio_input("点击录音", key="baseline_audio")

    if audio:
        st.audio(audio)
        audio_bytes = audio.read()
        fname = f"baseline_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        audio_path = os.path.join("data/audio", fname)
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        st.session_state.baseline_audio_path = audio_path

        if st.button("转写这段录音"):
            text = transcribe(audio_bytes, fname)
            st.session_state.baseline = text
            st.success("转写完成")

    text = st.text_area("转写文本（可手动修改）", value=st.session_state.baseline, height=120)

    if st.button("下一步"):
        st.session_state.baseline = text
        st.session_state.stage = "practice"
        st.rerun()


# ========== 阶段4：练习场景 ==========
elif st.session_state.stage == "practice":
    scenes = load_scenes()
    practice = get_practice_scene(scenes)
    st.header("练习场景（不计分）")

    uploaded = st.file_uploader("上传练习场景图片", type=["jpg", "jpeg", "png"], key="practice_img")
    if uploaded:
        st.image(uploaded)
    else:
        st.info("请上传练习场景图片")

    st.write(practice["instruction"])
    for i, q in enumerate(practice["questions"], 1):
        st.write(f"Q{i}：{q}")
    st.write(f"提示：{practice['hint']}")

    audio = st.audio_input("点击录音", key="practice_audio")
    if audio:
        st.audio(audio)
        audio_bytes = audio.read()
        fname = f"practice_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        audio_path = os.path.join("data/audio", fname)
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        st.session_state.practice_audio_path = audio_path

    text = st.text_area("转写文本（可手动填写）", height=120)

    if st.button("开始正式场景"):
        st.session_state.stage = "survey"
        st.session_state.scene_idx = 0
        st.rerun()


# ========== 阶段5：正式场景 ==========
elif st.session_state.stage == "survey":
    scenes = load_scenes()
    formal = get_formal_scenes(scenes)
    idx = st.session_state.scene_idx
    s = formal[idx]

    st.header(f"场景 {idx+1}/{len(formal)}：{s['title']}")

    uploaded = st.file_uploader(
        f"上传场景图片：{s['title']}",
        type=["jpg", "jpeg", "png"],
        key=f"img_{s['id']}"
    )
    if uploaded:
        st.image(uploaded)
    else:
        st.info("请上传这张场景的图片")

    st.write(s["instruction"])
    for i, q in enumerate(s["questions"], 1):
        st.write(f"Q{i}：{q}")
    st.write(f"提示：{s['hint']}")

    st.subheader("录音")
    audio = st.audio_input("点击录音", key=f"audio_{s['id']}")
    text = ""

    if audio:
        st.audio(audio)
        audio_bytes = audio.read()
        fname = f"scene{s['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        audio_path = os.path.join("data/audio", fname)
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        st.session_state.audio_paths[s["id"]] = audio_path

        if st.button("转写这段录音", key=f"trans_{s['id']}"):
            text = transcribe(audio_bytes, fname)
            st.session_state.narratives[s["id"]] = text
            st.success("转写完成")

    text = st.text_area(
        "转写文本（可手动修改）",
        value=st.session_state.narratives.get(s["id"], ""),
        height=150,
        key=f"narr_{s['id']}"
    )

    st.subheader("自评")
    answers = []
    for item in s["self_report"]:
        val = st.slider(item["text"], 1, 7, 4, key=f"ans_{s['id']}_{item['text']}")
        answers.append(val)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("上一题") and idx > 0:
            st.session_state.narratives[s["id"]] = text
            st.session_state.answers[s["id"]] = answers
            st.session_state.scene_idx -= 1
            st.rerun()
    with col2:
        if st.button("下一题"):
            st.session_state.narratives[s["id"]] = text
            st.session_state.answers[s["id"]] = answers
            if idx + 1 < len(formal):
                st.session_state.scene_idx += 1
                st.rerun()
            else:
                st.session_state.stage = "state_self"
                st.rerun()


# ========== 阶段6：整体状态自评 ==========
elif st.session_state.stage == "state_self":
    st.header("整体状态自评")
    st.write("请根据刚才看图时你最直接的感受作答。")
    qs = [
        "刚才看图时，我感到紧张、不安。",
        "刚才看图时，我想到了被重要的人忽视或抛弃的可能。",
        "刚才看图时，我倾向于不去想那些感受，把注意力转到别处。",
        "刚才看图时，我感到孤单，想有人陪在身边。",
        "刚才看图时，我更愿意自己一个人待着，不想被打扰。",
        "刚才看图时，我能够平静地看待画中的情境。",
        "看图后到现在，我内心的波动已经平复下来了。",
    ]
    vals = []
    for q in qs:
        vals.append(st.slider(q, 1, 7, 4))
    if st.button("下一步"):
        st.session_state.state_self = {
            "状态焦虑": (vals[0] + vals[1] + vals[3]) / 3,
            "状态回避": (vals[2] + vals[4]) / 2,
            "状态恢复": (vals[5] + vals[6]) / 2,
            "状态安全": 8 - (vals[0] + vals[1] + vals[3]) / 3,
        }
        st.session_state.stage = "recovery"
        st.rerun()


# ========== 阶段7：恢复期自评 ==========
elif st.session_state.stage == "recovery":
    st.header("恢复期自评")
    st.write("请再回想一下刚才的图片，现在你的感受如何？")
    q1 = st.slider("现在再回想那些图片，我仍然感到不安。", 1, 7, 4)
    q2 = st.slider("现在我已经能比较平静地回想那些画面。", 1, 7, 4)
    q3 = st.slider("如果现在遇到类似情境，我有信心能处理好。", 1, 7, 4)
    if st.button("下一步"):
        recovery_speed = (q2 + q3) / 2 - q1
        st.session_state.recovery = {
            "恢复速度": recovery_speed,
            "状态弹性": recovery_speed / (st.session_state.state_self["状态焦虑"] + 0.5),
        }
        st.session_state.stage = "ecr"
        st.rerun()


# ========== 阶段8：ECR-S ==========
elif st.session_state.stage == "ecr":
    st.header("ECR-S 简版")
    st.write("以下句子描述的是人们在亲密关系中的感受。请根据你平时在亲密关系中的真实状态作答。")
    items = [
        ("我担心恋人不会像我在乎他/她那样在乎我。", "焦虑"),
        ("当恋人想要和我非常亲近时，我会感到不自在。", "回避"),
        ("我发现自己很难完全信任恋人。", "回避"),
        ("我担心自己在别人眼中不够优秀。", "焦虑"),
        ("当恋人靠得太近时，我会开始感到紧张。", "回避"),
        ("我对自己的亲密关系有很多担忧。", "焦虑"),
        ("当恋人不像我期望的那样在我身边时，我会感到生气和烦躁。", "焦虑"),
        ("与恋人分享我的私密想法和感受，让我感到舒服自在。", "回避反向"),
        ("我担心被恋人抛弃。", "焦虑"),
        ("我不太喜欢与恋人过于亲近。", "回避"),
        ("当我对恋人的需要没有得到回应时，我会感到痛苦。", "焦虑"),
        ("我发现与恋人建立亲密的关系是相对容易的。", "回避反向"),
    ]
    vals = []
    for text, dim in items:
        vals.append(st.slider(text, 1, 7, 4))

    if st.button("下一步"):
        anx = [vals[i] for i, (_, d) in enumerate(items) if d == "焦虑"]
        avo = [vals[i] for i, (_, d) in enumerate(items) if d == "回避"]
        avo_rev = [8 - vals[i] for i, (_, d) in enumerate(items) if d == "回避反向"]
        st.session_state.ecr = {
            "焦虑": sum(anx) / len(anx),
            "回避": (sum(avo) + sum(avo_rev)) / (len(avo) + len(avo_rev)),
        }
        st.session_state.stage = "criterion"
        st.rerun()


# ========== 阶段9：效标量表 ==========
elif st.session_state.stage == "criterion":
    st.header("效标量表")
    st.write("请根据你平时的真实情况作答。")

    st.subheader("第一部分")
    sd_items = [
        "我从不迟到。", "我从不撒谎。", "我从不发脾气。",
        "我从不嫉妒别人。", "我从不背后说人坏话。", "我从不占别人便宜。",
        "我从不感到厌烦。", "我从不后悔自己的决定。", "我从不掩饰自己的错误。",
        "我从不忘记别人的恩惠。", "我从不害怕困难。", "我从不抱怨。",
        "我从不做违心的事。",
    ]
    sd_vals = []
    for item in sd_items:
        sd_vals.append(st.slider(item, 1, 7, 4))

    st.subheader("第二部分")
    erq_items = [
        ("当我想让自己少一些负面情绪时，我会改变对情境的看法。", "认知重评"),
        ("我会通过改变对情境的思考方式来调节情绪。", "认知重评"),
        ("当我想让自己多一些正面情绪时，我会改变对情境的看法。", "认知重评"),
        ("我会通过重新解释情境来调节情绪。", "认知重评"),
        ("我会控制自己的情绪表达。", "表达抑制"),
        ("当我感到负面情绪时，我会尽量不表现出来。", "表达抑制"),
        ("我会隐藏自己的情绪。", "表达抑制"),
        ("我会抑制自己的情绪表达。", "表达抑制"),
        ("当我想让自己少一些负面情绪时，我会尽量不表达出来。", "表达抑制"),
        ("我会通过不表达情绪来调节情绪。", "表达抑制"),
    ]
    erq_vals = []
    for text, dim in erq_items:
        erq_vals.append(st.slider(text, 1, 7, 4))

    st.subheader("第三部分")
    rs_items = [
        "我担心别人会拒绝我。", "我很容易察觉到别人对我的冷淡。",
        "当别人对我冷淡时，我会很在意。", "我害怕向别人提出请求。",
        "我担心自己会被重要的人抛弃。", "别人拒绝我时，我会难过很久。",
    ]
    rs_vals = []
    for item in rs_items:
        rs_vals.append(st.slider(item, 1, 7, 4))

    st.subheader("第四部分")
    bfi_items = [
        "我经常感到紧张。", "我容易担心。",
        "我情绪波动较大。", "我容易感到沮丧。",
    ]
    bfi_vals = []
    for item in bfi_items:
        bfi_vals.append(st.slider(item, 1, 7, 4))

    if st.button("提交并生成报告"):
        st.session_state.criterion = {
            "社会赞许性": sum(sd_vals) / len(sd_vals),
            "认知重评": sum([erq_vals[i] for i, (_, d) in enumerate(erq_items) if d == "认知重评"]) / 4,
            "表达抑制": sum([erq_vals[i] for i, (_, d) in enumerate(erq_items) if d == "表达抑制"]) / 6,
            "拒绝敏感性": sum(rs_vals) / len(rs_vals),
            "神经质": sum(bfi_vals) / len(bfi_vals),
        }
        st.session_state.stage = "report"
        st.rerun()


# ========== 阶段10：生成报告 + 保存数据 ==========
elif st.session_state.stage == "report":
    st.header("正在生成你的依恋画像...")

    narratives = [
        {"图片编号": sid, "文本": txt}
        for sid, txt in st.session_state.narratives.items()
    ]

    with st.spinner("正在编码叙事..."):
        narrative_results = encode_all(narratives)

    with st.spinner("正在计分..."):
        scores = compute_scores(
            narrative_results,
            st.session_state.state_self,
            st.session_state.ecr
        )
        scores["类型"] = classify(scores)

        scenes = load_scenes()
        self_scores = score_self_report(scenes, st.session_state.answers)
        scores.update(self_scores)
        scores.update(st.session_state.criterion)

    with st.spinner("正在提取声学特征..."):
        for scene_id, audio_path in st.session_state.get("audio_paths", {}).items():
            if os.path.exists(audio_path):
                feats = extract_features(audio_path)
                st.session_state.acoustics[scene_id] = feats

    with st.spinner("正在生成报告..."):
        path = generate_report(
            scores,
            acoustics_data=st.session_state.get("acoustics", {})
        )

    with st.spinner("正在保存数据..."):
        subject_id = upsert_subject(
            st.session_state.subject_code,
            st.session_state.gender,
            st.session_state.age,
            st.session_state.identity,
            st.session_state.relationship,
        )

        session_id = save_session(
            subject_id,
            st.session_state.baseline,
            st.session_state.state_self,
            st.session_state.recovery,
            st.session_state.ecr,
            st.session_state.criterion,
            scores,
        )

        for scene_id, text in st.session_state.narratives.items():
            audio_path = st.session_state.get("audio_paths", {}).get(scene_id, "")
            save_narrative(session_id, scene_id, text, audio_path)

            feats = st.session_state.acoustics.get(scene_id)
            if feats:
                save_acoustics(session_id, scene_id, audio_path, feats)

        for scene_id, answers in st.session_state.answers.items():
            scene = next((x for x in scenes if x["id"] == scene_id), None)
            if not scene:
                continue
            for i, (item, score) in enumerate(zip(scene["self_report"], answers)):
                save_self_report(session_id, scene_id, i, item["text"], item["dim"], score)

    st.success("报告已生成，数据已保存！")

    with open(path, encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=800, scrolling=True)

    st.download_button(
        "下载 HTML 报告",
        html,
        file_name="依恋画像报告.html",
        mime="text/html"
    )

    st.markdown("""
    **导出 PDF：** 点击上方“下载 HTML 报告”，用浏览器打开后按 `Ctrl + P`，
    选择“另存为 PDF”即可。
    """)

    if st.button("重新开始"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()