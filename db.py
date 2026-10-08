import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "data/asaara.db"


def get_conn():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT UNIQUE,
        gender TEXT,
        age INTEGER,
        identity TEXT,
        relationship TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER,
        baseline_text TEXT,
        state_anxiety REAL,
        state_avoidance REAL,
        state_recovery REAL,
        state_safety REAL,
        recovery_speed REAL,
        state_elasticity REAL,
        ecr_anxiety REAL,
        ecr_avoidance REAL,
        social_desirability REAL,
        cognitive_reappraisal REAL,
        expressive_suppression REAL,
        rejection_sensitivity REAL,
        neuroticism REAL,
        sep_distress REAL,
        proximity_seeking REAL,
        others_availability REAL,
        mentalizing REAL,
        resolution REAL,
        defensive_processing REAL,
        anxiety_score REAL,
        avoidance_score REAL,
        safety_score REAL,
        fear_score REAL,
        attachment_type TEXT,
        created_at TEXT,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS narratives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        scene_id INTEGER,
        text TEXT,
        audio_path TEXT,
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS self_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        scene_id INTEGER,
        item_index INTEGER,
        item_text TEXT,
        dimension TEXT,
        score INTEGER,
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS acoustics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        scene_id INTEGER,
        file_path TEXT,
        duration REAL,
        f0_mean REAL,
        f0_sd REAL,
        speech_rate REAL,
        pause_count INTEGER,
        pause_mean REAL,
        pause_max REAL,
        intensity_mean REAL,
        intensity_sd REAL,
        jitter REAL,
        shimmer REAL,
        created_at TEXT,
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    )
    """)

    conn.commit()
    conn.close()


def upsert_subject(subject_code, gender, age, identity, relationship):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM subjects WHERE subject_code=?", (subject_code,))
    row = c.fetchone()
    if row:
        subject_id = row["id"]
    else:
        c.execute("""
            INSERT INTO subjects (subject_code, gender, age, identity, relationship, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (subject_code, gender, age, identity, relationship, datetime.now().isoformat()))
        conn.commit()
        subject_id = c.lastrowid
    conn.close()
    return subject_id


def save_session(subject_id, baseline_text, state_self, recovery, ecr, criterion, scores):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO sessions (
            subject_id, baseline_text,
            state_anxiety, state_avoidance, state_recovery, state_safety,
            recovery_speed, state_elasticity,
            ecr_anxiety, ecr_avoidance,
            social_desirability, cognitive_reappraisal, expressive_suppression,
            rejection_sensitivity, neuroticism,
            sep_distress, proximity_seeking, others_availability,
            mentalizing, resolution, defensive_processing,
            anxiety_score, avoidance_score, safety_score, fear_score,
            attachment_type, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        subject_id, baseline_text,
        state_self.get("状态焦虑"), state_self.get("状态回避"),
        state_self.get("状态恢复"), state_self.get("状态安全"),
        recovery.get("恢复速度"), recovery.get("状态弹性"),
        ecr.get("焦虑"), ecr.get("回避"),
        criterion.get("社会赞许性"), criterion.get("认知重评"),
        criterion.get("表达抑制"), criterion.get("拒绝敏感性"),
        criterion.get("神经质"),
        scores.get("分离痛苦"), scores.get("亲近寻求"),
        scores.get("他人可获得性"), scores.get("心智化"),
        scores.get("结局整合"), scores.get("防御加工"),
        scores.get("焦虑分"), scores.get("回避分"),
        scores.get("安全分"), scores.get("恐惧分"),
        scores.get("类型"),
        datetime.now().isoformat()
    ))
    conn.commit()
    session_id = c.lastrowid
    conn.close()
    return session_id


def save_narrative(session_id, scene_id, text, audio_path=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO narratives (session_id, scene_id, text, audio_path)
        VALUES (?, ?, ?, ?)
    """, (session_id, scene_id, text, audio_path))
    conn.commit()
    conn.close()


def save_self_report(session_id, scene_id, item_index, item_text, dimension, score):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO self_reports (session_id, scene_id, item_index, item_text, dimension, score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, scene_id, item_index, item_text, dimension, score))
    conn.commit()
    conn.close()


def save_acoustics(session_id, scene_id, file_path, features):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO acoustics (
            session_id, scene_id, file_path,
            duration, f0_mean, f0_sd, speech_rate,
            pause_count, pause_mean, pause_max,
            intensity_mean, intensity_sd,
            jitter, shimmer, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        session_id, scene_id, file_path,
        features.get("duration"), features.get("f0_mean"), features.get("f0_sd"),
        features.get("speech_rate"), features.get("pause_count"),
        features.get("pause_mean"), features.get("pause_max"),
        features.get("intensity_mean"), features.get("intensity_sd"),
        features.get("jitter"), features.get("shimmer"),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def list_subjects():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM subjects ORDER BY id")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def list_sessions():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT s.*, sub.subject_code
        FROM sessions s
        LEFT JOIN subjects sub ON s.subject_id = sub.id
        ORDER BY s.id DESC
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def export_csv(path="data/export.csv"):
    import pandas as pd
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT sub.subject_code, sub.gender, sub.age, sub.identity, sub.relationship,
               s.*
        FROM sessions s
        LEFT JOIN subjects sub ON s.subject_id = sub.id
    """, conn)
    conn.close()
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path