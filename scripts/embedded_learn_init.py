#!/usr/bin/env python3
"""
embedded_learn_init.py
嵌入式学习数据目录初始化脚本

用法：
  python scripts/embedded_learn_init.py [workspace_path]

若未提供 workspace_path，默认在当前目录下创建 .workbuddy/embedded-learning/
"""

import os
import sys
import json
from datetime import datetime

def init_learning_dir(workspace: str) -> str:
    """初始化嵌入式学习数据目录结构"""
    base = os.path.join(workspace, ".workbuddy", "embedded-learning")
    topics_dir = os.path.join(base, "topics")
    
    os.makedirs(base, exist_ok=True)
    os.makedirs(topics_dir, exist_ok=True)
    
    # 创建 index.json（元数据索引）
    index_path = os.path.join(base, "index.json")
    if not os.path.exists(index_path):
        index = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "project_analyzed": False,
            "topics": [],
            "total_kp": 0,
            "learned_kp": 0,
            "last_activity": None
        }
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        print(f"✅ 创建索引文件: {index_path}")
    
    # 创建 review-log.md
    review_log = os.path.join(base, "review-log.md")
    if not os.path.exists(review_log):
        with open(review_log, "w", encoding="utf-8") as f:
            f.write("# 知识回顾记录\n\n")
            f.write("> 本文件自动记录每次 `/review` 命令的执行情况\n\n")
            f.write("---\n\n")
        print(f"✅ 创建回顾日志: {review_log}")
    
    print(f"\n📁 学习数据目录已就绪: {base}")
    return base


def create_topic_dir(base: str, topic_name: str) -> str:
    """为新主题创建目录结构"""
    # 将主题名转为安全目录名
    safe_name = topic_name.replace(" ", "-").replace("/", "-").replace("\\", "-")
    topic_dir = os.path.join(base, "topics", safe_name)
    notes_dir = os.path.join(topic_dir, "notes")
    
    os.makedirs(notes_dir, exist_ok=True)
    
    # 创建 quiz-log.md
    quiz_log = os.path.join(topic_dir, "quiz-log.md")
    if not os.path.exists(quiz_log):
        with open(quiz_log, "w", encoding="utf-8") as f:
            f.write(f"# {topic_name} — 问答记录\n\n")
            f.write("> 记录所有 `/quiz` 问答历史，用于分析薄弱点\n\n")
            f.write("---\n\n")
    
    print(f"✅ 主题目录已创建: {topic_dir}")
    return topic_dir


def update_index(base: str, **kwargs):
    """更新 index.json 中的字段"""
    index_path = os.path.join(base, "index.json")
    if not os.path.exists(index_path):
        init_learning_dir(os.path.dirname(os.path.dirname(base)))
    
    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    
    index.update(kwargs)
    index["last_activity"] = datetime.now().isoformat()
    
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def get_progress_summary(base: str) -> dict:
    """读取并返回学习进度摘要"""
    index_path = os.path.join(base, "index.json")
    if not os.path.exists(index_path):
        return {"error": "学习数据目录未初始化"}
    
    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    
    topics_dir = os.path.join(base, "topics")
    summary = {
        "total_topics": 0,
        "total_kp": 0,
        "learned_kp": 0,
        "topics_detail": []
    }
    
    if os.path.exists(topics_dir):
        for topic_name in os.listdir(topics_dir):
            topic_path = os.path.join(topics_dir, topic_name)
            if not os.path.isdir(topic_path):
                continue
            
            notes_path = os.path.join(topic_path, "notes")
            kp_count = len([f for f in os.listdir(notes_path) if f.endswith(".md")]) if os.path.exists(notes_path) else 0
            
            outline_path = os.path.join(topic_path, "outline.md")
            has_outline = os.path.exists(outline_path)
            
            summary["total_topics"] += 1
            summary["learned_kp"] += kp_count
            summary["topics_detail"].append({
                "name": topic_name,
                "learned_kp": kp_count,
                "has_outline": has_outline
            })
    
    return summary


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    init_learning_dir(workspace)
    
    summary = get_progress_summary(os.path.join(workspace, ".workbuddy", "embedded-learning"))
    print(f"\n📊 当前学习概况：")
    print(f"   主题数：{summary.get('total_topics', 0)}")
    print(f"   已学知识点：{summary.get('learned_kp', 0)}")
