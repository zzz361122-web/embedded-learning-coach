#!/usr/bin/env python3
"""
learner_profile.py
用户学习画像系统 — 自动分析、更新、输出学习者画像

功能：
  - 从 quiz-log、review-log、会话记录中提取行为特征
  - 更新用户画像 JSON
  - 输出当前教学策略建议

用法：
  python scripts/learner_profile.py [workspace_path] [--update] [--report]
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from collections import Counter


# ─── 默认画像模板 ────────────────────────────────────────────────────
DEFAULT_PROFILE = {
    "version": "2.0",
    "created_at": None,
    "updated_at": None,

    # ── 提问习惯 ──
    "question_style": {
        "tends_to_ask_why": 0,          # 追问原理型（问"为什么"的频率）
        "tends_to_ask_how": 0,          # 操作实践型（问"怎么做"的频率）
        "tends_to_ask_what": 0,         # 概念确认型（问"是什么"的频率）
        "tends_to_give_short_answers": 0,   # 倾向简短回答
        "tends_to_give_detailed_answers": 0, # 倾向详细展开回答
        "asks_for_examples": 0,         # 主动要求举例
        "asks_for_code": 0,             # 主动要求看代码
        "asks_for_analogy": 0,          # 主动要求类比解释
        "skips_questions": 0,           # 跳过问题的次数
        "total_interactions": 0
    },

    # ── 学习习惯 ──
    "learning_style": {
        "preferred_depth": "balanced",  # shallow / balanced / deep
        "code_first": False,            # 是否偏好先看代码再看原理
        "theory_first": False,          # 是否偏好先看原理再看代码
        "analogy_helps": True,          # 类比解释是否有效
        "diagram_preference": False,    # 是否偏好图示/流程图
        "pace": "normal",               # fast / normal / slow
        "session_avg_kp": 1.5,          # 每次会话平均学习KP数
        "prefers_chunked_learning": False,  # 偏好碎片化（短段落）
        "prefers_immersive_learning": False # 偏好沉浸式（连续长篇）
    },

    # ── 记忆习惯 ──
    "memory_pattern": {
        "avg_retention_days": 7,        # 平均记忆保留天数（根据复习间隔推算）
        "review_frequency": "low",      # high / normal / low（主动复习频率）
        "best_review_interval": 7,      # 最佳复习间隔（天）
        "forgets_details_first": True,  # 先忘细节（寄存器位）
        "forgets_concepts_first": False,# 先忘概念
        "strong_topics": [],            # 掌握较好的主题列表
        "weak_topics": [],              # 需要加强的主题列表
        "quiz_avg_score": 0.0,          # 测验平均通过率
        "total_quizzes": 0
    },

    # ── 认知特征（自动推断）──
    "cognitive_traits": {
        "learning_type": "unknown",     # visual / logical / practical / conceptual
        "attention_span": "normal",     # short / normal / long
        "error_tolerance": "normal",    # sensitive（容易沮丧）/ normal / resilient
        "curiosity_index": 0.5,         # 0~1，主动探索深度的倾向
        "confidence_level": "unknown"   # low / building / confident
    },

    # ── 教学策略（由画像自动计算）──
    "teaching_strategy": {
        "explanation_length": "medium",      # short / medium / long
        "code_position": "after_theory",     # before_theory / after_theory / interleaved
        "analogy_usage": "moderate",         # minimal / moderate / heavy
        "question_frequency": "normal",      # sparse / normal / dense
        "recursion_depth": 2,                # 递归展开层数（1~3）
        "review_interval_days": 7,           # 推荐复习间隔
        "quiz_difficulty_start": "easy",     # easy / medium / hard（起始难度）
        "encouragement_style": "balanced",   # minimal / balanced / heavy
        "pacing": "normal"                   # fast / normal / slow
    },

    # ── 行为历史（用于趋势分析）──
    "behavior_history": []  # 每次会话后追加一条记录
}


# ─── 画像读写 ────────────────────────────────────────────────────────

def get_profile_path(workspace: str) -> str:
    return os.path.join(workspace, ".workbuddy", "embedded-learning", "learner-profile.json")


def load_profile(workspace: str) -> dict:
    path = get_profile_path(workspace)
    if not os.path.exists(path):
        profile = DEFAULT_PROFILE.copy()
        profile["created_at"] = datetime.now().isoformat()
        save_profile(workspace, profile)
        return profile
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(workspace: str, profile: dict):
    path = get_profile_path(workspace)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    profile["updated_at"] = datetime.now().isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


# ─── 行为特征提取 ────────────────────────────────────────────────────

def analyze_quiz_logs(workspace: str) -> dict:
    """从所有 quiz-log.md 提取测验行为特征"""
    topics_dir = os.path.join(workspace, ".workbuddy", "embedded-learning", "topics")
    stats = {
        "total_correct": 0, "total_partial": 0, "total_wrong": 0,
        "total_quizzes": 0, "weak_topics": [], "strong_topics": [],
        "avg_answer_length": 0, "answer_lengths": []
    }

    if not os.path.exists(topics_dir):
        return stats

    for topic in os.listdir(topics_dir):
        quiz_log = os.path.join(topics_dir, topic, "quiz-log.md")
        if not os.path.exists(quiz_log):
            continue
        with open(quiz_log, "r", encoding="utf-8") as f:
            content = f.read()

        correct = content.count("✅")
        partial = content.count("🔶")
        wrong = content.count("❌")
        total = correct + partial + wrong

        if total > 0:
            stats["total_correct"] += correct
            stats["total_partial"] += partial
            stats["total_wrong"] += wrong
            stats["total_quizzes"] += total

            pass_rate = correct / total
            if pass_rate >= 0.8:
                stats["strong_topics"].append(topic)
            elif pass_rate < 0.5:
                stats["weak_topics"].append(topic)

        # 粗略估算回答长度（字符数）
        answers = re.findall(r"用户回答[：:]\s*(.+?)(?=\n|$)", content)
        for ans in answers:
            stats["answer_lengths"].append(len(ans.strip()))

    if stats["answer_lengths"]:
        stats["avg_answer_length"] = sum(stats["answer_lengths"]) / len(stats["answer_lengths"])

    return stats


def analyze_review_log(workspace: str) -> dict:
    """从 review-log.md 分析记忆习惯"""
    review_log = os.path.join(workspace, ".workbuddy", "embedded-learning", "review-log.md")
    stats = {"review_count": 0, "avg_interval_days": 7}

    if not os.path.exists(review_log):
        return stats

    with open(review_log, "r", encoding="utf-8") as f:
        content = f.read()

    dates = re.findall(r"(\d{4}-\d{2}-\d{2})", content)
    stats["review_count"] = len(dates)

    if len(dates) >= 2:
        intervals = []
        for i in range(1, len(dates)):
            d1 = datetime.strptime(dates[i-1], "%Y-%m-%d")
            d2 = datetime.strptime(dates[i], "%Y-%m-%d")
            diff = abs((d2 - d1).days)
            if 0 < diff < 60:
                intervals.append(diff)
        if intervals:
            stats["avg_interval_days"] = round(sum(intervals) / len(intervals))

    return stats


# ─── 画像推断 ────────────────────────────────────────────────────────

def infer_teaching_strategy(profile: dict) -> dict:
    """根据用户画像推断最优教学策略"""
    qs = profile["question_style"]
    ls = profile["learning_style"]
    mp = profile["memory_pattern"]
    ct = profile["cognitive_traits"]

    strategy = profile["teaching_strategy"].copy()

    # ── 讲解长度 ──
    if qs.get("tends_to_give_short_answers", 0) > qs.get("tends_to_give_detailed_answers", 0):
        strategy["explanation_length"] = "short"
        strategy["pacing"] = "fast"
    elif qs.get("tends_to_give_detailed_answers", 0) > 5:
        strategy["explanation_length"] = "long"
        strategy["pacing"] = "slow"
    else:
        strategy["explanation_length"] = "medium"

    # ── 代码位置 ──
    if qs.get("asks_for_code", 0) > qs.get("tends_to_ask_why", 0):
        strategy["code_position"] = "before_theory"   # 实践型：先看代码
    elif qs.get("tends_to_ask_why", 0) > qs.get("asks_for_code", 0):
        strategy["code_position"] = "after_theory"    # 原理型：先讲理论
    else:
        strategy["code_position"] = "interleaved"     # 均衡穿插

    # ── 类比使用 ──
    if qs.get("asks_for_analogy", 0) >= 3 or ls.get("analogy_helps", True):
        strategy["analogy_usage"] = "heavy"
    elif qs.get("asks_for_analogy", 0) == 0 and ls.get("preferred_depth") == "deep":
        strategy["analogy_usage"] = "minimal"
    else:
        strategy["analogy_usage"] = "moderate"

    # ── 提问频率 ──
    if qs.get("skips_questions", 0) > 3:
        strategy["question_frequency"] = "sparse"   # 经常跳过，减少提问
    elif qs.get("tends_to_ask_why", 0) + qs.get("tends_to_ask_how", 0) > 10:
        strategy["question_frequency"] = "dense"    # 主动探索型，增加互动
    else:
        strategy["question_frequency"] = "normal"

    # ── 递归深度 ──
    if ls.get("preferred_depth") == "shallow" or ct.get("attention_span") == "short":
        strategy["recursion_depth"] = 1
    elif ls.get("preferred_depth") == "deep" or ct.get("curiosity_index", 0.5) > 0.7:
        strategy["recursion_depth"] = 3
    else:
        strategy["recursion_depth"] = 2

    # ── 复习间隔 ──
    avg_interval = mp.get("best_review_interval", 7)
    strategy["review_interval_days"] = max(3, min(14, avg_interval))

    # ── 测验起始难度 ──
    avg_score = mp.get("quiz_avg_score", 0.0)
    if avg_score > 0.8:
        strategy["quiz_difficulty_start"] = "medium"
    elif avg_score < 0.4:
        strategy["quiz_difficulty_start"] = "easy"
    else:
        strategy["quiz_difficulty_start"] = "easy"

    # ── 鼓励风格 ──
    if ct.get("error_tolerance") == "sensitive":
        strategy["encouragement_style"] = "heavy"
    elif ct.get("confidence_level") == "confident":
        strategy["encouragement_style"] = "minimal"
    else:
        strategy["encouragement_style"] = "balanced"

    return strategy


def update_profile_from_session(workspace: str, session_data: dict) -> dict:
    """
    根据一次会话数据更新画像

    session_data 格式：
    {
        "why_questions": int,     # 追问原理次数
        "how_questions": int,     # 询问操作次数
        "code_requests": int,     # 要求看代码次数
        "analogy_requests": int,  # 要求类比次数
        "skipped_questions": int, # 跳过问题次数
        "answer_lengths": list,   # 每次回答的字符数列表
        "kp_learned": int,        # 本次学了几个KP
        "session_duration_min": float  # 会话时长（分钟）
    }
    """
    profile = load_profile(workspace)
    qs = profile["question_style"]
    ls = profile["learning_style"]

    # 更新提问习惯
    qs["tends_to_ask_why"] += session_data.get("why_questions", 0)
    qs["tends_to_ask_how"] += session_data.get("how_questions", 0)
    qs["asks_for_code"] += session_data.get("code_requests", 0)
    qs["asks_for_analogy"] += session_data.get("analogy_requests", 0)
    qs["skips_questions"] += session_data.get("skipped_questions", 0)
    qs["total_interactions"] += 1

    # 更新回答长度分析
    ans_lens = session_data.get("answer_lengths", [])
    if ans_lens:
        avg = sum(ans_lens) / len(ans_lens)
        if avg < 20:
            qs["tends_to_give_short_answers"] += 1
        elif avg > 100:
            qs["tends_to_give_detailed_answers"] += 1

    # 更新学习节奏
    kp = session_data.get("kp_learned", 0)
    dur = session_data.get("session_duration_min", 30)
    old_avg = ls.get("session_avg_kp", 1.5)
    interactions = qs["total_interactions"]
    ls["session_avg_kp"] = round((old_avg * (interactions - 1) + kp) / interactions, 2)

    # 推断学习深度偏好
    if ls["session_avg_kp"] > 3:
        ls["preferred_depth"] = "shallow"  # 学得快，可能浅尝
    elif ls["session_avg_kp"] < 1:
        ls["preferred_depth"] = "deep"     # 学得慢，深度挖掘

    # 更新测验统计
    quiz_stats = analyze_quiz_logs(workspace)
    if quiz_stats["total_quizzes"] > 0:
        total = quiz_stats["total_correct"] + quiz_stats["total_partial"] + quiz_stats["total_wrong"]
        profile["memory_pattern"]["quiz_avg_score"] = round(
            quiz_stats["total_correct"] / total, 2
        ) if total > 0 else 0.0
        profile["memory_pattern"]["total_quizzes"] = quiz_stats["total_quizzes"]
        profile["memory_pattern"]["weak_topics"] = quiz_stats["weak_topics"]
        profile["memory_pattern"]["strong_topics"] = quiz_stats["strong_topics"]

    # 更新复习习惯
    review_stats = analyze_review_log(workspace)
    profile["memory_pattern"]["best_review_interval"] = review_stats["avg_interval_days"]
    if review_stats["review_count"] > 5:
        profile["memory_pattern"]["review_frequency"] = "high"
    elif review_stats["review_count"] > 2:
        profile["memory_pattern"]["review_frequency"] = "normal"
    else:
        profile["memory_pattern"]["review_frequency"] = "low"

    # 重新推断教学策略
    profile["teaching_strategy"] = infer_teaching_strategy(profile)

    # 追加行为历史
    profile["behavior_history"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "kp_learned": kp,
        "session_min": dur,
        "interactions": session_data.get("why_questions", 0) + session_data.get("how_questions", 0)
    })
    # 只保留最近50条历史
    if len(profile["behavior_history"]) > 50:
        profile["behavior_history"] = profile["behavior_history"][-50:]

    save_profile(workspace, profile)
    return profile


# ─── 教学策略报告 ────────────────────────────────────────────────────

def get_strategy_report(workspace: str) -> str:
    """生成当前教学策略的可读摘要，供 AI 在每次会话开始时读取"""
    profile = load_profile(workspace)
    strategy = profile["teaching_strategy"]
    qs = profile["question_style"]
    mp = profile["memory_pattern"]
    ct = profile["cognitive_traits"]

    lines = [
        "# 🧠 当前学习者画像与教学策略",
        f"_更新于: {profile.get('updated_at', '未更新')}_",
        "",
        "## 提问习惯",
        f"- 追问原理(Why)：{qs['tends_to_ask_why']} 次",
        f"- 询问操作(How)：{qs['tends_to_ask_how']} 次",
        f"- 要求代码：{qs['asks_for_code']} 次",
        f"- 要求类比：{qs['asks_for_analogy']} 次",
        f"- 跳过问题：{qs['skips_questions']} 次",
        "",
        "## 学习风格",
        f"- 偏好深度：{profile['learning_style']['preferred_depth']}",
        f"- 每次学习KP均值：{profile['learning_style']['session_avg_kp']}",
        f"- 节奏：{strategy['pacing']}",
        "",
        "## 记忆特征",
        f"- 测验平均通过率：{mp['quiz_avg_score'] * 100:.0f}%",
        f"- 薄弱主题：{', '.join(mp['weak_topics']) if mp['weak_topics'] else '暂无'}",
        f"- 擅长主题：{', '.join(mp['strong_topics']) if mp['strong_topics'] else '暂无'}",
        f"- 主动复习频率：{mp['review_frequency']}",
        "",
        "## ✅ 当前教学策略（本次会话请遵守）",
        f"- 讲解长度：**{strategy['explanation_length']}**（short/medium/long）",
        f"- 代码位置：**{strategy['code_position']}**",
        f"  - before_theory = 先展示代码，再讲原理",
        f"  - after_theory = 先讲理论，再给代码",
        f"  - interleaved = 理论与代码穿插",
        f"- 类比使用：**{strategy['analogy_usage']}**",
        f"- 提问频率：**{strategy['question_frequency']}**（sparse/normal/dense）",
        f"- 递归展开深度：**{strategy['recursion_depth']} 层**",
        f"- 推荐复习间隔：**{strategy['review_interval_days']} 天**",
        f"- 测验起始难度：**{strategy['quiz_difficulty_start']}**",
        f"- 鼓励风格：**{strategy['encouragement_style']}**",
        "",
        "## 📌 AI 执行须知",
        "- 每次会话结束前，调用 `update_profile_from_session()` 更新画像",
        "- 若用户表现与当前策略偏差明显，立即更新对应字段",
        "- 若用户明确说「讲短一点」「少出题」等，直接修改策略并保存",
        "- 画像版本每10次交互自动重新推断一次，确保策略不落后于用户成长"
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    if "--report" in sys.argv:
        print(get_strategy_report(workspace))
    elif "--update" in sys.argv:
        # 示例：模拟一次会话更新
        sample = {
            "why_questions": 2,
            "how_questions": 1,
            "code_requests": 1,
            "analogy_requests": 0,
            "skipped_questions": 0,
            "answer_lengths": [45, 30, 60],
            "kp_learned": 2,
            "session_duration_min": 25
        }
        profile = update_profile_from_session(workspace, sample)
        print("✅ 画像已更新")
        print(json.dumps(profile["teaching_strategy"], ensure_ascii=False, indent=2))
    else:
        # 默认：初始化画像并输出报告
        profile = load_profile(workspace)
        print(f"✅ 画像已加载: {get_profile_path(workspace)}")
        print(get_strategy_report(workspace))
