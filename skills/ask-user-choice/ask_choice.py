#!/usr/bin/env python3
"""
ask_choice.py - 通过原生 GUI 对话框让用户点选答案（支持多问题、其他选项）

用法:
  py ask_choice.py --questions '[{"question":"问题","options":["A","B"]}]' [--agent-label "标识"]

输出 (JSON):
  确定: {"status":"ok","answers":[{"question":"问题","answer":"A"},...]}
  取消: {"status":"cancelled"}
"""

import argparse
import ctypes
import json
import sys
import tkinter as tk

OTHER_LABEL = "其他"
OTHER_VALUE = "__other__"


def enable_dpi_awareness():
    """启用 DPI 感知，高分屏下渲染清晰"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def build_question_ui(parent, index, question_text, options, multiple):
    """为单个问题构建 UI，返回 get_answer 回调"""
    entry_var = tk.StringVar()
    entry: tk.Entry | None = None

    # 分隔线（第一个问题不加）
    if index > 0:
        tk.Frame(parent, height=1, bg="#D0D0D0").pack(fill="x", padx=24, pady=(12, 0))

    # 问题文本
    tk.Label(
        parent,
        text=f"{index + 1}. {question_text}",
        wraplength=500,
        justify="left",
        anchor="w",
        padx=24,
        font=("Microsoft YaHei UI", 11, "bold"),
    ).pack(fill="x", pady=(12 if index > 0 else 8, 4))

    opts_frame = tk.Frame(parent)
    opts_frame.pack(fill="x", padx=24, pady=(0, 8))

    if multiple:
        # 多选模式
        check_vars: list[tuple[str, tk.BooleanVar]] = []
        for opt in options:
            var = tk.BooleanVar()
            check_vars.append((opt, var))
            tk.Checkbutton(
                opts_frame,
                text=opt,
                variable=var,
                anchor="w",
                font=("Microsoft YaHei UI", 10),
            ).pack(fill="x")

        other_var = tk.BooleanVar()
        other_row = tk.Frame(opts_frame)
        other_row.pack(fill="x")
        other_cb = tk.Checkbutton(
            other_row,
            text=OTHER_LABEL,
            variable=other_var,
            anchor="w",
            font=("Microsoft YaHei UI", 10),
        )
        other_cb.pack(side="left")
        entry = tk.Entry(
            other_row,
            textvariable=entry_var,
            width=28,
            font=("Microsoft YaHei UI", 10),
        )
        entry.pack(side="left", padx=(8, 0))
        entry.configure(state="disabled")

        def on_other_toggle() -> None:
            if other_var.get():
                entry.configure(state="normal")
                entry.focus_set()
            else:
                entry_var.set("")
                entry.configure(state="disabled")

        other_cb.configure(command=on_other_toggle)

        def get_answer() -> str:
            selected = [opt for opt, v in check_vars if v.get()]
            if other_var.get():
                custom = entry_var.get().strip()
                selected.append(f"{OTHER_LABEL}: {custom}" if custom else OTHER_LABEL)
            return ", ".join(selected) if selected else ""

    else:
        # 单选模式
        var = tk.StringVar(value=options[0] if options else "")
        for opt in options:
            tk.Radiobutton(
                opts_frame,
                text=opt,
                value=opt,
                variable=var,
                anchor="w",
                font=("Microsoft YaHei UI", 10),
            ).pack(fill="x")

        other_row = tk.Frame(opts_frame)
        other_row.pack(fill="x")
        tk.Radiobutton(
            other_row,
            text=OTHER_LABEL,
            value=OTHER_VALUE,
            variable=var,
            anchor="w",
            font=("Microsoft YaHei UI", 10),
        ).pack(side="left")
        entry = tk.Entry(
            other_row,
            textvariable=entry_var,
            width=28,
            font=("Microsoft YaHei UI", 10),
        )
        entry.pack(side="left", padx=(8, 0))
        entry.configure(state="disabled")

        def on_var_change(*args) -> None:
            if var.get() == OTHER_VALUE:
                entry.configure(state="normal")
                entry.focus_set()
            else:
                entry_var.set("")
                entry.configure(state="disabled")

        var.trace_add("write", on_var_change)

        def get_answer() -> str:
            v = var.get()
            if v == OTHER_VALUE:
                custom = entry_var.get().strip()
                return f"{OTHER_LABEL}: {custom}" if custom else OTHER_LABEL
            return v

    return get_answer


def show_dialog(questions: list[dict], agent_label: str = "") -> dict:
    """显示多问题选择对话框"""
    root = tk.Tk()
    root.title(f"🤖 {agent_label}" if agent_label else "Agent 提问")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    result: list = [None]
    get_answer_fns: list = []

    # Agent 标识头部（蓝底白字）
    if agent_label:
        header = tk.Frame(root, bg="#0A84FF")
        header.pack(fill="x", side="top")
        tk.Label(
            header,
            text=f"🤖 {agent_label}",
            fg="white",
            bg="#0A84FF",
            padx=24,
            pady=10,
            anchor="w",
            font=("Microsoft YaHei UI", 10, "bold"),
        ).pack(fill="x")

    # 按钮区域（先 pack 到 bottom）
    btn_frame = tk.Frame(root)
    btn_frame.pack(side="bottom", fill="x", padx=24, pady=(4, 16))

    def on_ok() -> None:
        answers = [
            {"question": q_text, "answer": ga()} for q_text, ga in get_answer_fns
        ]
        result[0] = {"status": "ok", "answers": answers}
        root.destroy()

    def on_cancel() -> None:
        result[0] = {"status": "cancelled"}
        root.destroy()

    tk.Button(btn_frame, text="确定", width=10, command=on_ok).pack(side="right")
    tk.Button(btn_frame, text="取消", width=10, command=on_cancel).pack(
        side="right", padx=(0, 8)
    )

    # 内容容器（canvas + scrollbar 放在一起，避免布局错乱）
    content_container = tk.Frame(root)
    content_container.pack(fill="both", expand=True)

    canvas = tk.Canvas(content_container, highlightthickness=0)
    scrollbar = tk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
    content = tk.Frame(canvas)
    content.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas.create_window((0, 0), window=content, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 先 pack scrollbar，再 pack canvas，确保 scrollbar 不被挤掉
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # 鼠标滚轮支持
    def on_mousewheel(event) -> None:
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # 构建每个问题的 UI
    for i, q in enumerate(questions):
        ga = build_question_ui(
            content, i, q["question"], q["options"], q.get("multiple", False)
        )
        get_answer_fns.append((q["question"], ga))

    # 调整 canvas 宽度匹配内容
    content.update_idletasks()
    canvas.configure(width=content.winfo_reqwidth())

    root.protocol("WM_DELETE_WINDOW", on_cancel)

    # 计算窗口尺寸并定位到主屏幕右下角
    root.update_idletasks()
    max_height = 700
    win_w = root.winfo_reqwidth()
    win_h = min(root.winfo_reqheight(), max_height)

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    margin = 16
    taskbar_h = 48  # 预留任务栏高度
    x = screen_w - win_w - margin
    y = screen_h - win_h - taskbar_h
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")

    root.mainloop()
    try:
        canvas.unbind_all("<MouseWheel>")
    except Exception:
        pass

    return result[0] if result[0] else {"status": "cancelled"}


def main() -> None:
    enable_dpi_awareness()

    parser = argparse.ArgumentParser(
        description="通过原生 GUI 对话框让用户点选答案（支持多问题、其他选项）"
    )
    parser.add_argument(
        "--questions",
        required=True,
        help='JSON: [{"question":"问题","options":["A","B"],"multiple":false}]',
    )
    parser.add_argument(
        "--agent-label",
        default="",
        help="agent 标识，用于区分多个同时工作的 agent",
    )
    args = parser.parse_args()

    try:
        questions = json.loads(args.questions)
    except json.JSONDecodeError as e:
        print(
            json.dumps(
                {"status": "error", "message": f"JSON 解析失败: {e}"},
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    if not isinstance(questions, list) or not questions:
        print(
            json.dumps(
                {"status": "error", "message": "questions 必须是非空数组"},
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    for i, q in enumerate(questions):
        if not isinstance(q, dict) or "question" not in q or "options" not in q:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "message": f"问题 {i + 1} 格式错误，需要 question 和 options 字段",
                    },
                    ensure_ascii=False,
                )
            )
            sys.exit(1)
        if not q["options"]:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "message": f"问题 {i + 1} 的 options 为空",
                    },
                    ensure_ascii=False,
                )
            )
            sys.exit(1)

    try:
        result = show_dialog(questions, args.agent_label)
    except Exception as e:
        print(
            json.dumps(
                {"status": "error", "message": str(e)},
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
