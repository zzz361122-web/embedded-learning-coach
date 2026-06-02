# Embedded Learning Coach  直接下载embedded-learning-coach.zip

**A WorkBuddy AI Skill for Embedded Systems Deep Learning**

<p align="center">
  <img src="https://img.shields.io/badge/Platform-WorkBuddy-blue" alt="Platform">
  <img src="https://img.shields.io/badge/Language-中文/English-green" alt="Language">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

## What is this?

Embedded Learning Coach is an AI-powered skill designed for [WorkBuddy](https://www.codebuddy.cn) that transforms embedded systems projects into structured learning courses. It uses **recursive deep learning + Socratic questioning** methods, combined with a **learner profile system** that continuously observes user behavior and **dynamically adjusts teaching strategies**.

## Features

- **Project Analysis** (`/analyze`) - Scan embedded projects to identify tech stack, peripherals, protocols, and generate learning roadmaps
- **Adaptive Learning** (`/learn`) - Deep-dive into topics with personalized pacing, code-first or theory-first approach, adjustable recursion depth
- **Socratic Quiz** (`/quiz`) - AI-generated questions with adaptive difficulty, automatic weak-point detection
- **Spaced Repetition Review** (`/review`) - Personalized review schedule based on memory patterns and quiz performance
- **Progress Tracking** (`/progress`) - Comprehensive progress reports with learner profile insights

## Key Innovation: Learner Profile System

The skill builds and evolves a **learner profile** that tracks:
- Learning style preferences (code-first vs theory-first)
- Explanation length preference
- Question frequency tolerance
- Recursion depth comfort
- Memory retention patterns
- Quiz difficulty calibration

This profile **self-evolves** with every interaction, enabling truly personalized teaching.

## Directory Structure

```
embedded-learning-coach/
├── SKILL.md                          # Main skill definition file
├── assets/                           # Templates
│   ├── kp-note-template.md           # Knowledge point note template
│   ├── learner-profile-template.json # Learner profile template
│   └── topic-outline-template.md     # Topic outline template
├── references/                       # Reference materials
│   ├── embedded-tech-map.md          # Embedded systems technology map
│   └── teaching-strategy-map.md      # Teaching strategy specifications
├── scripts/                          # Python helper scripts
│   ├── embedded_learn_init.py         # Learning directory initializer
│   ├── generate_progress_report.py   # Progress report generator
│   └── learner_profile.py            # Learner profile manager
├── docs/                             # Documentation
│   └── Embedded_Learning_Coach_Introduction.docx
├── README.md
└── LICENSE
```

## How to Use

1. Install this skill in your WorkBuddy workspace under `.workbuddy/skills/`
2. Open your embedded project in WorkBuddy
3. Use commands to start learning:
   ```
   /analyze [project-path]     # Analyze your embedded project
   /learn [topic-name]         # Start learning a topic
   /quiz [topic-name]          # Test your knowledge
   /review                     # Review previously learned content
   /progress                   # View learning progress report
   ```

## Supported Domains

- MCU development (STM32, ESP32, Arduino, etc.)
- RTOS (FreeRTOS, RT-Thread, etc.)
- Communication protocols (UART, SPI, I2C, CAN, etc.)
- Peripheral drivers (GPIO, ADC, PWM, Timer, etc.)
- Linux driver development
- Middleware and application layer analysis

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
