---
name: ask-user-choice
description: 凡是需要让用户在离散选项中抉择时调用本 skill，通过原生 GUI 弹窗让用户点选回答。支持一次弹窗问多个问题、每个问题支持"其他"自定义回答、多 agent 通过标识区分来源。适用于选方案、确认操作、选技术栈等。
---

# Ask User Choice

## 何时使用

适用于有明确离散选项的提问（选方案、确认操作、选技术栈等）。不适用于开放式问题，这类问题直接在对话中提问。多个问题尽量合并到一次弹窗，减少打扰。

## 用法

通过 `terminal` 工具执行本 skill 目录下的 `ask_choice.py`：

```bash
py ~/.agents/skills/ask-user-choice/ask_choice.py --questions '[{"question":"问题1","options":["A","B"]},{"question":"问题2","options":["是","否"]}]' --agent-label "简短任务描述"
```

> `~` 在 sh（Git Bash）中会自动展开为用户主目录，直接使用即可。

### 参数

| 参数             | 必填 | 说明                                        |
| ---------------- | ---- | ------------------------------------------- |
| `--questions`    | 是   | JSON 数组，每个元素是一个问题对象（格式见下） |
| `--agent-label`  | 建议 | agent 标识，多 agent 同时工作时用于区分来源   |

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

| 字段        | 类型    | 必填 | 说明                  |
| ----------- | ------- | ---- | --------------------- |
| `question`  | string  | 是   | 要问用户的问题        |
| `options`   | array   | 是   | 选项列表              |
| `multiple`  | boolean | 否   | 是否多选，默认 false  |

> 每个问题会自动追加"其他"选项。用户选"其他"后可输入自定义回答，无需在 options 中手动添加。

### 输出格式

stdout 输出 JSON：

```json
{"status": "ok", "answers": [{"question": "问题1", "answer": "选项A"}, {"question": "问题2", "answer": "其他: 自定义内容"}], "remarks": "用户输入的备注，可为空字符串"}
```

用户取消时：

```json
{"status": "cancelled"}
```

> 弹窗底部始终有一个「备注」输入框，用户可留空。`remarks` 字段即其内容（留空时为空字符串 `""`），agent 可结合各问题的答案与备注一起思考。

## 注意事项

1. **传 `--agent-label` 并合并问题**：用简短中文描述当前任务（如"修复登录bug"）；有多个问题时合并到一次 `--questions` 调用，不要分多次弹窗。
2. **`timeout_ms` 设为 600000**（10 分钟），给用户足够时间点选。
3. **JSON 引号**：`--questions` 的 JSON 字符串用单引号包裹，内部用双引号，避免转义。
4. **尊重取消**：输出 `{"status":"cancelled"}` 时不要继续追问，告知用户已取消并等待指示。
5. **"其他"回答格式**：用户选"其他"时，answer 为 `"其他: 用户输入的文本"`，agent 应解析这个前缀。脚本依赖 Python + tkinter（Windows 默认随 Python 安装），用 `py` 命令调用。

## 示例

多问题合并（推荐）：

```
terminal(
  cd="nkc",
  command='py ~/.agents/skills/ask-user-choice/ask_choice.py --questions ''[{"question":"使用哪种方案？","options":["JWT","Session"]},{"question":"需要测试吗？","options":["需要","不需要"]},{"question":"部署到哪个环境？","options":["开发","测试","生产"]}]'' --agent-label "实现登录功能"',
  timeout_ms=600000
)
```
