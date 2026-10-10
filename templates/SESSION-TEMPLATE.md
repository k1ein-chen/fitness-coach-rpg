---
date: {{DATE}}
type: {{TYPE}} # 例如: Push (推类 · 胸肩三头) / Pull (拉类 · 背二头后束) / Legs (腿类 · 臀腿核心)
duration: {{DURATION_MIN}} min (抗阻 {{LIFT_MIN}}m + 有氧 {{CARDIO_MIN}}m)
body_weight: {{WEIGHT_KG}} kg
calories_in: {{CALORIES_IN}} kcal
protein_in: {{PROTEIN_G}} g
energy_level: {{ENERGY_LEVEL}} # 例如: 7/10
status: {{STATUS}} # 例如: 减脂重启期 / 力量积累期
tags:
  - 训练手记
  - 减脂期
  - 重启阶段
---

# 📋 战训手记：{{DATE}} · {{TITLE}}

---

## 🏋️‍♂️ 上半部分：现实科学训练日志 (Coach's Briefing)

> **教练寄语**：
> {{COACH_COMMENTS}}

### 1. 训练动作矩阵 (Workout Log)

| 动作名称 | 组别 | 负重 (kg) | 次数 (Reps) | RIR (力竭余力) | 动作体感与要点 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **{{EXERCISE_1}}** | 热身 | {{WEIGHT}} | {{REPS}} | - | {{NOTE}} |
| | 正式 1 | {{WEIGHT}} | {{REPS}} | {{RIR}} | {{NOTE}} |
| | 正式 2 | {{WEIGHT}} | {{REPS}} | {{RIR}} | {{NOTE}} |
| **{{EXERCISE_2}}** | 正式 1 | {{WEIGHT}} | {{REPS}} | {{RIR}} | {{NOTE}} |

### 2. 有氧减脂与后燃 (Cardio)
- **项目**：{{CARDIO_NAME}} (例如: 跑步机坡度快走)
- **参数**：坡度 {{INCLINE}}%，速度 {{SPEED}} km/h，时长 {{CARDIO_MIN}} 分钟
- **反馈**：{{CARDIO_FEEDBACK}} (心率感受、出汗量、膝关节受力体感)

### 3. 营养与恢复监控 (Nutrition & Bio-metrics)
- **当日饮食与补剂**：
  - 中午：{{LUNCH}}
  - 晚上：{{DINNER}}
  - 补剂：{{SUPPLEMENTS}} (例如: 蛋白粉、肌酸)
  - 全天估算蛋白：~{{PROTEIN_G}}g / 目标 {{TARGET_PROTEIN_G}}g
- **伤病警戒区跟踪**：
  - **左肩（重点监控）**：{{LEFT_SHOULDER_STATUS}}
  - **右膝（重点监控）**：{{RIGHT_KNEE_STATUS}}
- **教练下次递进指标**：
  - {{NEXT_TARGETS}}

---

## 🔮 下半部分：巨龙港异界回响 (Tales from Longwan Port)

> **魔导纪事**：{{CHAPTER_SUBTITLE}}

{{GROUNDED_STORY_PARAGRAPHS}}
*(写作要求：不堆砌华丽词藻，用词自然克制；有网络小说感与故事张力；动作意象化，不出现现代词汇与动作名,对话自然有生活感)*
*(写作指引：创作前必读 profiles/STORY-LOG.md 对齐当前大纲与任务，并参考 references/narrative-templates.md 启发式感觉映射灵感库。将训练内容与状态自然融入剧情推进与任务执行中，绝非给健身房换皮；严禁江湖黑话与刻意短句；严禁出现“下班/打卡/地铁”等现代词汇)*

---

### ⚔️ 本役战绩结算 (State Delta)
- **本场斩获**：`+{{EXP_GAINED}} EXP`（当前等级进度：`Lv.{{LEVEL}} [ {{CURRENT_EXP}} / {{NEXT_LEVEL_EXP}} ]`）
- **巨龙港账本**：{{LEDGER_DELTA}} (例如: 消耗 26.4 铜钱，今日余粮充足)
- **身体与心境状态**：{{STATUS_BUFFS}} (例如: 【轻度肌肉酸胀】、【经脉唤醒度提升】)
