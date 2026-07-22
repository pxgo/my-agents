---
name: ask-user-choice
description: 凡是需要让用户在离散选项中抉择时调用本 skill，通过原生 GUI 弹窗让用户点选回答。支持一次弹窗问多个问题、每个问题支持"其他"自定义回答、多 agent 通过标识区分来源。适用于选方案、确认操作、选技术栈等。
---

# Ask User Choice

## 何时使用

有明确离散选项的提问（选方案、确认操作、选技术栈等）；开放式问题直接在对话中提问。多个问题尽量合并到一次弹窗。

## 用法

通过 `terminal` 工具执行 `ask_choice.py`：

```bash
py ~/.agents/skills/ask-user-choice/ask_choice.py --questions '[{"question":"问题1","options":["A","B"]},{"question":"问题2","options":["是","否"]}]' --agent-label "简短任务描述"
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--questions` | 是 | JSON 数组，每个元素含 `question`（string，必填）、`options`（array，必填）、`multiple`（boolean，可选，默认 false） |
| `--agent-label` | 建议 | agent 标识，多 agent 同时工作时区分来源 |

> 每个问题自动追加"其他"选项，用户选后可输入自定义回答（answer 格式为 `"其他: 用户输入"`）。

### 输出格式

stdout 输出 JSON：

```json
{"status": "ok", "answers": [{"question": "问题1", "answer": "选项A"}], "remarks": "用户备注，可为空"}
```

用户取消时输出 `{"status": "cancelled"}`。弹窗底部有备注输入框，`remarks` 为其内容（留空为 `""`）。

## 注意事项

1. 传 `--agent-label`（简短中文描述当前任务），多个问题合并到一次 `--questions` 调用。
2. `timeout_ms` 设为 600000（10 分钟）。
3. JSON 引号：`--questions` 的 JSON 用单引号包裹，内部用双引号，避免转义。
4. 尊重取消：输出 `cancelled` 时不追问，告知用户已取消并等待指示。
5. 依赖 Python + tkinter（Windows 默认随 Python 安装），用 `py` 调用。
