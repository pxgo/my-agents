---
name: ask-user-choice
description: 当需要向用户提出有离散选项的问题时，通过原生 GUI 弹窗让用户鼠标点选回答，而不是让用户在聊天框手动输入。支持一次弹窗同时回答多个问题，每个问题还支持选"其他"并输入自定义回答。适用于选择方案、确认操作、选择技术栈等有明确选项的场景。多个 agent 同时工作时也能通过标识区分来源。
---

# Ask User Choice

当需要向用户提问且问题有离散选项时，通过原生 GUI 弹窗让用户点选，而非在聊天框手动输入。

**支持一次弹窗问多个问题**，避免反复打扰用户。每个问题自动带"其他"选项，用户选中后可输入自定义回答。

## 何时使用

适用于有明确选项的提问：

- 选择实现方案（方案 A / 方案 B / 方案 C）
- 确认操作（继续 / 取消 / 修改）
- 选择技术栈或依赖
- 任何 2 个以上离散选项的选择

**不适用于**开放式问题（没有固定选项的），这类问题直接在对话中提问。

**最佳实践**：当你有多个问题需要问用户时，合并到一次弹窗中，减少打扰。

## 用法

通过 `terminal` 工具执行本 skill 目录下的 `ask_choice.py`：

```bash
py ~/.agents/skills/ask-user-choice/ask_choice.py --questions '[{"question":"问题1","options":["A","B"]},{"question":"问题2","options":["是","否"]}]' --agent-label "简短任务描述"
```

> `~` 在 sh（Git Bash）中会自动展开为用户主目录，直接使用即可。
```

### 参数

| 参数             | 必填 | 说明                                                                 |
| ---------------- | ---- | -------------------------------------------------------------------- |
| `--questions`    | 是   | JSON 数组，每个元素是一个问题对象（格式见下）                        |
| `--agent-label`  | 建议 | agent 标识，多 agent 同时工作时用于区分来源                          |

### questions JSON 格式

```json
[
  {
    "question": "问题文本",
    "options": ["选项A", "选项B", "选项C"],
    "multiple": false
  },
  {
    "question": "多选问题？",
    "options": ["选项1", "选项2", "选项3"],
    "multiple": true
  }
]
```

| 字段        | 类型    | 必填 | 说明                              |
| ----------- | ------- | ---- | --------------------------------- |
| `question`  | string  | 是   | 要问用户的问题                    |
| `options`   | array   | 是   | 选项列表                          |
| `multiple`  | boolean | 否   | 是否多选，默认 false              |

> 每个问题会自动追加"其他"选项。用户选"其他"后可输入自定义回答，无需你在 options 中手动添加。

### 输出格式

stdout 输出 JSON：

```json
{"status": "ok", "answers": [{"question": "问题1", "answer": "选项A"}, {"question": "问题2", "answer": "其他: 自定义内容"}]}
```

用户取消时：

```json
{"status": "cancelled"}
```

## 注意事项

1. **务必传 `--agent-label`**：用简短中文描述当前任务，如"修复登录bug"。多个 agent 同时弹窗时用户靠标题栏和蓝色头部区分。
2. **合并多个问题**：有多个问题时，合并到一次 `--questions` 调用，不要分多次弹窗。
3. **timeout_ms 设为 600000**：给用户足够时间点选（10 分钟）。
4. **JSON 引号**：`--questions` 的 JSON 字符串用单引号包裹，内部用双引号，避免转义。
5. **尊重取消**：如果输出 `{"status":"cancelled"}`，不要继续追问，告知用户已取消并等待指示。
6. **"其他"回答**：用户选"其他"时，answer 格式为 `"其他: 用户输入的文本"`。agent 应解析这个前缀。
7. 脚本依赖 Python + tkinter（Windows 默认随 Python 安装），用 `py` 命令调用。

## 示例

单问题：

```
terminal(
  cd="nkc",
  command='py ~/.agents/skills/ask-user-choice/ask_choice.py --questions ''[{"question":"使用哪种方案实现登录？","options":["JWT","Session","OAuth2"]}]'' --agent-label "实现登录功能"',
  timeout_ms=600000
)
```

多问题合并（推荐）：

```
terminal(
  cd="nkc",
  command='py ~/.agents/skills/ask-user-choice/ask_choice.py --questions ''[{"question":"使用哪种方案？","options":["JWT","Session"]},{"question":"需要测试吗？","options":["需要","不需要"]},{"question":"部署到哪个环境？","options":["开发","测试","生产"]}]'' --agent-label "实现登录功能"',
  timeout_ms=600000
)
```
