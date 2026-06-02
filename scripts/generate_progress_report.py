#!/usr/bin/env python3
"""
generate_progress_report.py
生成嵌入式学习进度报告

用法：
  python scripts/generate_progress_report.py [workspace_path]

输出：workspace/.workbuddy/embedded-learning/progress-report.md
"""

import os
import sys
import json
import re
from datetime import datetime


def read_outline(outline_path: str) -> dict:
    """解析 outline.md，统计已学/未学知识点"""
    if not os.path.exists(outline_path):
        return {"total": 0, "learned": 0, "kps": []}
    
    with open(outline_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    total = 0
    learned = 0
    kps = []
    
    for line in content.split("\n"):
        # 匹配 "- ✅ KP名称" 或 "- ⬜ KP名称" 或 "- KP名称"
        if re.match(r"^\s*[-*]\s*(✅|⬜|🔲|\[x\]|\[ \])", line, re.IGNORECASE):
            total += 1
            if "✅" in line or "[x]" in line.lower():
                learned += 1
                kps.append({"name": line.strip(), "status": "learned"})
            else:
                kps.append({"name": line.strip(), "status": "pending"})
    
    return {"total": total, "learned": learned, "kps": kps}


def read_quiz_log(quiz_log_path: str) -> dict:
    """解析 quiz-log.md，统计评分情况"""
    if not os.path.exists(quiz_log_path):
        return {"total_quizzes": 0, "correct": 0, "partial": 0, "wrong": 0, "last_quiz": None}
    
    with open(quiz_log_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    correct = content.count("✅")
    partial = content.count("🔶")
    wrong = content.count("❌")
    total = correct + partial + wrong
    
    # 提取最后一次测验日期
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", content)
    last_quiz = dates[-1] if dates else None
    
    return {
        "total_quizzes": total,
        "correct": correct,
        "partial": partial,
        "wrong": wrong,
        "pass_rate": round(correct / total * 100) if total > 0 else 0,
        "last_quiz": last_quiz
    }


def read_notes_metadata(notes_dir: str) -> list:
    """读取知识点笔记的元数据（创建时间等）"""
    notes = []
    if not os.path.exists(notes_dir):
        return notes
    
    for fname in sorted(os.listdir(notes_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(notes_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            first_lines = "".join([f.readline() for _ in range(5)])
        
        created = re.search(r"创建时间[：:]\s*(.+)", first_lines)
        updated = re.search(r"更新时间[：:]\s*(.+)", first_lines)
        title = re.search(r"^#\s+(.+)", first_lines)
        
        notes.append({
            "file": fname,
            "title": title.group(1) if title else fname,
            "created": created.group(1).strip() if created else "未记录",
            "updated": updated.group(1).strip() if updated else "未记录"
        })
    
    return notes


def generate_report(workspace: str) -> str:
    """生成完整学习进度报告，返回报告内容"""
    base = os.path.join(workspace, ".workbuddy", "embedded-learning")
    topics_dir = os.path.join(base, "topics")
    project_analysis = os.path.join(base, "project-analysis.md")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = [
        "# 🎓 嵌入式学习进度报告",
        f"",
        f"> 生成时间：{now}",
        f"",
        "---",
        "",
    ]
    
    # 项目分析状态
    if os.path.exists(project_analysis):
        lines += ["## ✅ 项目已分析", "", "已完成项目结构分析，详见 `project-analysis.md`", ""]
    else:
        lines += ["## ⚠️ 项目尚未分析", "", "请先执行 `/analyze [项目路径]` 分析嵌入式项目", ""]
    
    # 总体进度统计
    total_topics = 0
    total_kp = 0
    total_learned = 0
    all_wrong_kps = []
    topic_rows = []
    
    if os.path.exists(topics_dir):
        for topic_name in sorted(os.listdir(topics_dir)):
            topic_path = os.path.join(topics_dir, topic_name)
            if not os.path.isdir(topic_path):
                continue
            
            outline_info = read_outline(os.path.join(topic_path, "outline.md"))
            quiz_info = read_quiz_log(os.path.join(topic_path, "quiz-log.md"))
            notes = read_notes_metadata(os.path.join(topic_path, "notes"))
            
            total_topics += 1
            total_kp += outline_info["total"] or len(notes)
            total_learned += outline_info["learned"] or len(notes)
            
            pass_rate_str = f"{quiz_info['pass_rate']}%" if quiz_info["total_quizzes"] > 0 else "未测验"
            last_learn = notes[-1]["created"] if notes else "未开始"
            
            topic_rows.append(
                f"| {topic_name} | {outline_info['total'] or len(notes)} | "
                f"{outline_info['learned'] or len(notes)} | {pass_rate_str} | {last_learn} |"
            )
            
            # 收集错题
            if quiz_info["wrong"] > 0:
                all_wrong_kps.append(f"- **{topic_name}**：{quiz_info['wrong']} 个知识点需要复习")
    
    # 写入总体进度
    overall_pct = round(total_learned / total_kp * 100) if total_kp > 0 else 0
    progress_bar = "█" * (overall_pct // 10) + "░" * (10 - overall_pct // 10)
    
    lines += [
        "## 📊 总体学习进度",
        "",
        f"**{progress_bar}** {overall_pct}%",
        "",
        f"- 学习主题数：**{total_topics}**",
        f"- 总知识点数：**{total_kp}**",
        f"- 已学知识点：**{total_learned}**",
        f"- 完成进度：**{overall_pct}%**",
        "",
    ]
    
    # 各主题进度表格
    if topic_rows:
        lines += [
            "## 📚 各主题学习详情",
            "",
            "| 主题 | 知识点总数 | 已学 | 测验通过率 | 最近学习 |",
            "|------|-----------|------|-----------|---------|",
        ]
        lines += topic_rows
        lines += [""]
    else:
        lines += ["## 📚 各主题学习详情", "", "> 暂无学习记录，请执行 `/learn [主题名]` 开始学习", ""]
    
    # 待复习列表
    lines += ["## 🔁 待复习知识点", ""]
    if all_wrong_kps:
        lines += all_wrong_kps + [""]
    else:
        lines += ["✅ 暂无待复习知识点（或尚未进行测验）", ""]
    
    # 下一步建议
    lines += ["## 🚀 下一步建议", ""]
    if total_topics == 0:
        lines += [
            "1. 执行 `/analyze [项目路径]` 分析嵌入式项目，了解技术栈",
            "2. 根据分析结果执行 `/learn [主题名]` 开始第一个主题的学习",
            ""
        ]
    elif total_learned < total_kp:
        lines += [
            f"1. 继续学习未完成的主题，当前进度 {total_learned}/{total_kp}",
            "2. 完成某个主题后，执行 `/quiz [主题名]` 进行测验巩固",
            ""
        ]
    else:
        lines += [
            "1. 执行 `/review` 回顾所有已学知识点，强化记忆",
            "2. 尝试应用所学知识，修改项目中的实际代码",
            ""
        ]
    
    lines += [
        "---",
        "",
        f"*报告由 embedded-learning-coach 自动生成 · {now}*",
        ""
    ]
    
    report_content = "\n".join(lines)
    
    # 写入文件
    report_path = os.path.join(base, "progress-report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"✅ 进度报告已生成: {report_path}")
    return report_content


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    content = generate_report(workspace)
    print("\n" + "="*60)
    print(content)
