# Fitness Coach RPG 🎮💪

> 把枯燥的现实训练，变成一场可以升级记录的异世界冒险

<!-- TODO: 添加 demo GIF 或视频
![Demo](./assets/demo.gif)
-->

[![License](https://img.shields.io/github/license/k1ein-chen/fitness-coach-rpg)](./LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/k1ein-chen/fitness-coach-rpg?style=social)](https://github.com/k1ein-chen/fitness-coach-rpg)

一个**对话驱动**的 AI 健身教练框架：训练记录、RPG 属性成长、剧情推进三者联动。你的每一次训练都会转化为角色成长和故事推进——不只是数据，还是冒险。

```
真实训练 → 经验值 & 属性成长 → 剧情推进 → 下一次训练的动力
```

---

## ✨ 核心特性

- 🎯 **对话式训练**：和 AI 聊天就能记录训练、获取建议、推进剧情
- 📊 **自动加点**：完成训练自动获得 EXP，升级后属性点自动分配（力量/耐力/体质/敏捷/智力）
- 📝 **智能记录**：自动追踪重量、次数、RPE、体感反馈，AI 会参考历史数据给建议
- 🎭 **剧情模式**：可选的故事系统，把每次训练映射为异世界冒险
- 🌍 **多世界观**：内置剑与魔法、武侠、乙游等主题，也可以自己创建
- 🔄 **恢复感知**：智能判断中断后的恢复强度，不硬来
- 🤖 **越用越懂你**：AI 会记住你的偏好、弱项和进步节奏

---

## 🚀 快速开始

### 1. 获取项目

```bash
git clone https://github.com/k1ein-chen/fitness-coach-rpg.git
cd fitness-coach-rpg
```

### 2. 初始化档案

**方式一：脚本初始化（推荐）**

```bash
python scripts/init_profile.py --name 你的名字 --theme 武侠
```

**方式二：手动复制**

```bash
cp -r assets/starter-profile user-data
# 然后编辑 user-data/PROFILE.md 填入你的信息
```

> 💡 脚本只用 Python 标准库，无需安装依赖。没有 Python？直接复制模板也能用。

### 3. 开始训练

在支持的 AI 环境中打开项目，对 AI 说：

- "开始训练" — 直接开练
- "初始化档案" — 完整设定流程
- "帮我做个计划" — 制定训练计划

AI 会自动读取你的档案和历史记录，给出个性化建议。

---

## 🎮 玩法说明

### 训练与成长

每次训练后，系统会自动：

1. 记录训练数据（动作、重量、次数、RPE）
2. 计算并发放经验值
3. 检查是否升级，自动分配属性点
4. 更新训练统计和个人最佳记录

### 剧情模式（可选）

开启后，你的训练会映射为故事情节：

| 训练类型 | 剧情映射 |
|:---|:---|
| 推日 (Push) | 突破、强攻、正面输出 |
| 拉日 (Pull) | 控制、夺取、精确发力 |
| 腿日 (Legs) | 负重、坚守、耐力考验 |
| 恢复/有氧 | 营地修整、旅行、侦察 |

### 世界观选择

| 主题 | 等级称号示例 |
|:---|:---|
| **剑与魔法** | 冒险者新人 → 见习佣兵 → 精英冒险家 → … → 位面守护者 |
| **武侠** | 练气期 → 筑基期 → 金丹期 → … → 大乘期 |
| **社会** | 健身房游客 → 月卡钉子户 → 自由重量区 → … → 传说中人 |

不想要剧情？选择「经典模式」，纯教练功能。

---

## 👥 选择你的教练

预设的凯圣王×谭指导适合力量增长。其他目标可以选择：

| 目标 | 推荐教练 | 风格 |
|:---|:---|:---|
| 减脂塑形 | 周六野、帕梅拉 | 温柔鼓励 / 高效直接 |
| 瑜伽柔韧 | 林芊妤 | 舒缓专注 |
| 体态矫正 | 欧阳春晓 | 细致拆解 |
| 零基础 | 韩小四 | 超友好 |

初始化时告诉 AI："我想跟周六野练"或"力量日跟凯圣王，有氧跟帕梅拉"——混搭也可以。

详见 [教练风格指南](references/coach-guide.md)。

---

## 📁 项目结构

```
fitness-coach-rpg/
├── SKILL.md                    # AI 行为说明书（核心）
├── assets/starter-profile/     # 空白存档模板
├── worlds/default/             # 预置世界设定（剑与魔法）
├── references/                 # 训练方法论、RPG 规则、叙事模板
├── scripts/                    # 辅助脚本（初始化、更新状态等）
├── templates/                  # 训练日志模板
└── examples/                   # 示例存档（用了一个月后的样子）
```

初始化后会生成 `user-data/` 目录，存放你的个人档案和训练记录。

---

## 🔧 运行环境

这不是需要安装的 app 或插件——它是一套**本地文件 + AI 行为规则**。

**需要的环境：**

- 可读写本地文件的 AI 环境
- 可持续访问同一工作区的多个 Markdown/JSON 文件
- 最好支持时间获取和长期上下文

**推荐平台：**

- Cursor（原生支持）
- 其他支持文件读写的 AI IDE/Agent

**没有 Python 也能用：**

AI 可以直接手写 JSON 记录，脚本只是让更新更可靠。

---

## 🌟 为什么用这个？

| 痛点 | 解决方案 |
|:---|:---|
| 训练记录枯燥，没动力看 | RPG 成长感 + 剧情推进，训练有反馈 |
| 中断后不知道从何开始 | 恢复判断 + 强度自动调整 |
| 通用计划不适合自己 | AI 根据你的历史数据个性化建议 |
| 换个 app 数据就没了 | 本地 Markdown/JSON，永远属于你 |

---

## 📖 更多资源

- [完整示例存档](examples/completed-save/) — 用了一个月后的样子
- [训练方法论](references/coach-wang-tan-method.md) — 凯圣王×谭指导的力量训练体系
- [RPG 规则详解](references/rpg-rules.md) — 等级、属性、经验值计算
- [叙事引擎](references/story-engine.md) — 训练如何映射为剧情
- [更新日志](CHANGELOG.md) — 版本变化

---

## 📬 关于

- **小红书**：[@龙酱](https://www.xiaohongshu.com/user/profile/5c63da27000000001202556a)
- **GitHub**：[k1ein-chen/fitness-coach-rpg](https://github.com/k1ein-chen/fitness-coach-rpg)

---

## ⭐ 觉得有用？

如果这个项目对你有帮助，请给个 **Star** ⭐ 支持一下！

这是对作者最大的鼓励，也能让更多人发现这个项目。

[![Star History](https://img.shields.io/github/stars/k1ein-chen/fitness-coach-rpg?style=social)](https://github.com/k1ein-chen/fitness-coach-rpg)

---

## 📄 许可

[MIT License](./LICENSE)

---

## Quick Start (English)

Fitness Coach RPG is a conversation-driven AI fitness coach framework that links workout logging, RPG stat progression, and optional story mode.

**Features:**
- Chat-based workout tracking (weight, reps, RPE, notes)
- Auto stat allocation: training → EXP → level up → attribute growth
- Optional story mode: map real workouts to fantasy adventures
- Multiple worldviews: Sword & Sorcery, Wuxia, or custom
- Recovery-aware planning with smart intensity adjustment
- Local Markdown/JSON storage — your data stays yours

**Quick Start:**

```bash
git clone https://github.com/k1ein-chen/fitness-coach-rpg.git
cd fitness-coach-rpg
python scripts/init_profile.py --name YourName --theme "Sword & Sorcery"
```

Then open the project in a file-aware AI environment and say "Start training" or "Initialize profile".

See [RELEASE-v0.1.md](./RELEASE-v0.1.md) for more details in English.
