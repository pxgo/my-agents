#!/usr/bin/env python3
"""
ask_choice.py - 通过原生 GUI 对话框让用户点选答案（支持多问题、其他选项、备注）

用法:
  py ask_choice.py --questions '[{"question":"问题","options":["A","B"]}]' [--agent-label "标识"]

输出 (JSON):
  确定: {"status":"ok","answers":[{"question":"问题","answer":"A"},...],"remarks":"备注内容"}
  取消: {"status":"cancelled"}
"""

import argparse
import ctypes
import json
import sys
import tkinter as tk

OTHER_LABEL = "其他"
OTHER_VALUE = "__other__"

# 窗口尺寸常量
WIN_W = 520  # 固定窗口宽度（像素）
MIN_H = 300  # 最小窗口高度（像素）
MAX_H = 700  # 最大窗口高度（像素），超出后内容区域滚动
WRAP_W = 440  # Label / 按钮 文本换行宽度（像素）
TASKBAR_H = 48  # 预留任务栏高度
MARGIN = 16  # 窗口距屏幕右下角的边距

FONT = ("Microsoft YaHei UI", 10)
FONT_BOLD = ("Microsoft YaHei UI", 11, "bold")


def enable_dpi_awareness():
    """启用 DPI 感知，高分屏下渲染清晰"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def _display_line_count(text_widget: tk.Text) -> int:
    """返回 Text 当前内容占据的显示行数（含自动换行）。"""
    r = text_widget.count("1.0", "end-1c", "displaylines")
    if isinstance(r, tuple):
        breaks = r[0] if r else 0
    else:
        breaks = r if r else 0
    return breaks + 1


def make_auto_text(parent, min_lines: int, refit):
    """创建一个随内容自动变高、自动换行的 Text 控件。

    - 不使用 wraplength（Text 不支持），改用 pack(fill='x') 让其按实际像素宽度换行。
    - 高度随显示行数增长，最小为 min_lines。
    - refit: 高度变化后回调，用于重新适配窗口尺寸。
    返回 (text 控件, 触发重算高度的函数)。
    """
    text = tk.Text(
        parent,
        height=min_lines,
        width=20,
        wrap="word",
        font=FONT,
        relief="solid",
        borderwidth=1,
        highlightthickness=0,
        padx=4,
        pady=3,
    )

    def resize(_event=None):
        # after_idle 确保在按键/粘贴实际写入文本之后再计算高度
        text.after_idle(lambda: _do_resize(text, min_lines, refit))

    text.bind("<KeyRelease>", resize)
    text.bind("<<Paste>>", resize)
    return text, resize


def _do_resize(text: tk.Text, min_lines: int, refit):
    text.update_idletasks()
    lines = _display_line_count(text)
    text.configure(height=max(min_lines, lines))
    refit()


def build_question_ui(parent, index, question_text, options, multiple, refit):
    """为单个问题构建 UI，返回 get_answer 回调"""
    custom_text: tk.Text | None = None

    # 分隔线（第一个问题不加）
    if index > 0:
        tk.Frame(parent, height=1, bg="#D0D0D0").pack(fill="x", padx=24, pady=(12, 0))

    # 问题文本
    tk.Label(
        parent,
        text=f"{index + 1}. {question_text}",
        wraplength=WRAP_W,
        justify="left",
        anchor="w",
        padx=24,
        font=FONT_BOLD,
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
                wraplength=WRAP_W,
                justify="left",
                font=FONT,
            ).pack(fill="x")

        other_var = tk.BooleanVar()
        other_cb = tk.Checkbutton(
            opts_frame,
            text=OTHER_LABEL,
            variable=other_var,
            anchor="w",
            wraplength=WRAP_W,
            justify="left",
            font=FONT,
        )
        other_cb.pack(fill="x")

        custom_text, custom_resize = make_auto_text(
            opts_frame, min_lines=1, refit=refit
        )
        custom_text.pack(fill="x", padx=(20, 0), pady=(2, 0))
        custom_text.configure(state="disabled")

        def on_other_toggle() -> None:
            if other_var.get():
                custom_text.configure(state="normal")
                custom_text.focus_set()
            else:
                custom_text.configure(state="normal")
                custom_text.delete("1.0", "end")
                custom_text.configure(state="disabled")
                custom_resize()

        other_cb.configure(command=on_other_toggle)

        def get_answer() -> str:
            selected = [opt for opt, v in check_vars if v.get()]
            if other_var.get():
                custom = custom_text.get("1.0", "end-1c").strip()
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
                wraplength=WRAP_W,
                justify="left",
                font=FONT,
            ).pack(fill="x")

        other_cb = tk.Radiobutton(
            opts_frame,
            text=OTHER_LABEL,
            value=OTHER_VALUE,
            variable=var,
            anchor="w",
            wraplength=WRAP_W,
            justify="left",
            font=FONT,
        )
        other_cb.pack(fill="x")

        custom_text, custom_resize = make_auto_text(
            opts_frame, min_lines=1, refit=refit
        )
        custom_text.pack(fill="x", padx=(20, 0), pady=(2, 0))
        custom_text.configure(state="disabled")

        def on_var_change(*args) -> None:
            if var.get() == OTHER_VALUE:
                custom_text.configure(state="normal")
                custom_text.focus_set()
            else:
                custom_text.configure(state="normal")
                custom_text.delete("1.0", "end")
                custom_text.configure(state="disabled")
                custom_resize()

        var.trace_add("write", on_var_change)

        def get_answer() -> str:
            v = var.get()
            if v == OTHER_VALUE:
                custom = custom_text.get("1.0", "end-1c").strip()
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

    # 固定内容宽度（= 窗口宽度 - 滚动条），用于让 Text 按实际像素宽度换行
    content_w = WIN_W - 16

    # Agent 标识头部（蓝底白字）
    header = None
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
            wraplength=WRAP_W,
            justify="left",
            font=("Microsoft YaHei UI", 10, "bold"),
        ).pack(fill="x")

    # 按钮区域（先 pack 到 bottom）
    btn_frame = tk.Frame(root)
    btn_frame.pack(side="bottom", fill="x", padx=24, pady=(4, 16))

    def on_ok() -> None:
        answers = [
            {"question": q_text, "answer": ga()} for q_text, ga in get_answer_fns
        ]
        remarks = remarks_text.get("1.0", "end-1c").strip()
        result[0] = {"status": "ok", "answers": answers, "remarks": remarks}
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

    canvas = tk.Canvas(content_container, highlightthickness=0, width=content_w)
    scrollbar = tk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
    content = tk.Frame(canvas, width=content_w)
    content.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    win_item = canvas.create_window((0, 0), window=content, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 用 canvas 窗口项的 width 来固定内容区宽度（而非设置 content 宽度——
    # 因为 pack 传播会覆盖 content 的请求宽度）。高度仍由 content 的子控件决定。
    def _on_canvas_configure(event):
        canvas.itemconfigure(win_item, width=event.width)

    canvas.bind("<Configure>", _on_canvas_configure)

    # 先 pack scrollbar，再 pack canvas，确保 scrollbar 不被挤掉
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # 鼠标滚轮支持
    def on_mousewheel(event) -> None:
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # 根据内容高度重新适配窗口尺寸（高度在 MIN_H~MAX_H 范围内自适应）
    # initial_placed 标记初始定位是否完成：完成后 refit 只调高度，
    # 保留用户拖动后的窗口位置，避免切换选项时窗口跳回默认位置。
    initial_placed = {"done": False}

    def refit():
        content.update_idletasks()
        header_h = header.winfo_reqheight() if header is not None else 0
        btn_h = btn_frame.winfo_reqheight()
        avail_min = MIN_H - header_h - btn_h
        avail_max = MAX_H - header_h - btn_h
        content_h = content.winfo_reqheight()
        canvas_h = max(avail_min, min(avail_max, content_h))
        canvas.configure(height=canvas_h)
        win_h = header_h + btn_h + canvas_h

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()

        if not initial_placed["done"]:
            # 首次定位到屏幕右下角
            x = max(0, screen_w - WIN_W - MARGIN)
            y = max(0, screen_h - win_h - TASKBAR_H)
            root.geometry(f"{WIN_W}x{win_h}+{x}+{y}")
            initial_placed["done"] = True
        else:
            # 已初始化：保持当前窗口位置，只调整高度
            cur_x = root.winfo_x()
            cur_y = root.winfo_y()
            # 若高度增长导致底部超出屏幕（留出任务栏），则窗口上移
            if cur_y + win_h > screen_h - TASKBAR_H:
                cur_y = max(0, screen_h - win_h - TASKBAR_H)
            root.geometry(f"{WIN_W}x{win_h}+{cur_x}+{cur_y}")
        canvas.configure(scrollregion=canvas.bbox("all"))

    # 构建每个问题的 UI
    for i, q in enumerate(questions):
        ga = build_question_ui(
            content, i, q["question"], q["options"], q.get("multiple", False), refit
        )
        get_answer_fns.append((q["question"], ga))

    # 底部备注输入框（始终显示，可留空）
    tk.Frame(content, height=1, bg="#D0D0D0").pack(fill="x", padx=24, pady=(12, 0))
    tk.Label(
        content,
        text="备注（可选，可留空）",
        wraplength=WRAP_W,
        justify="left",
        anchor="w",
        padx=24,
        font=FONT_BOLD,
    ).pack(fill="x", pady=(8, 4))
    remarks_text, _ = make_auto_text(content, min_lines=2, refit=refit)
    remarks_text.pack(fill="x", padx=24, pady=(0, 8))

    root.protocol("WM_DELETE_WINDOW", on_cancel)

    # 初始定位并适配高度
    root.update_idletasks()
    refit()

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
