import tkinter as tk
from tkinter import ttk
from config import SIDEBAR_BG, FONT_SMALL, FONT_LOG, BUTTON_BG, BUTTON_FG, BUTTON_ACTIVE_BG, FONT_BUTTON


class ResultPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=SIDEBAR_BG)
        self._on_show_path = None  # callback set by MainGraphScreen
        self._build()

    def set_show_path_callback(self, cb):
        self._on_show_path = cb

    def _build(self):
        tk.Label(self, text="Results", bg=SIDEBAR_BG, fg="#cdd6f4",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=(6, 2))

        self.path_var = tk.StringVar(value="Path:  —")
        tk.Label(self, textvariable=self.path_var, bg=SIDEBAR_BG, fg="#a6e3a1",
                 font=FONT_SMALL, wraplength=230, justify="left").pack(anchor="w", padx=8)

        self.cost_var = tk.StringVar(value="Total Cost:  —")
        tk.Label(self, textvariable=self.cost_var, bg=SIDEBAR_BG, fg="#89dceb",
                 font=FONT_SMALL).pack(anchor="w", padx=8, pady=(2, 4))

        self.btn_show = tk.Button(
            self, text="Show Path", state="disabled",
            command=self._on_show_path_click,
            bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON,
            relief="flat", padx=6, pady=4, cursor="hand2",
            activebackground=BUTTON_ACTIVE_BG, activeforeground=BUTTON_FG, bd=0,
        )
        self.btn_show.pack(fill="x", padx=8, pady=(0, 6))

        tk.Label(self, text="Step Log:", bg=SIDEBAR_BG, fg="#6c7086",
                 font=FONT_SMALL).pack(anchor="w", padx=8)

        log_frame = tk.Frame(self, bg=SIDEBAR_BG)
        log_frame.pack(fill="both", expand=True, padx=8, pady=(2, 6))

        self.log_text = tk.Text(
            log_frame, font=FONT_LOG, bg="#11111b", fg="#a6adc8",
            relief="flat", state="disabled", wrap="none", cursor="arrow",
            selectbackground="#313244",
        )
        scroll_y = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

    def _on_show_path_click(self):
        if self._on_show_path:
            self._on_show_path()

    def display_result(self, path: list, cost: float):
        if not path:
            self.path_var.set("Path:  No path found")
            self.cost_var.set("Total Cost:  —")
            self.btn_show.config(state="disabled")
        else:
            self.path_var.set("Path:  " + " → ".join(str(n) for n in path))
            cost_str = _fmt(cost)
            self.cost_var.set(f"Total Cost:  {cost_str}")
            self.btn_show.config(state="normal")

    def log_step(self, text: str):
        self.log_text.config(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def clear(self):
        self.path_var.set("Path:  —")
        self.cost_var.set("Total Cost:  —")
        self.btn_show.config(state="disabled")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")


def _fmt(value: float) -> str:
    if value == float("inf"):
        return "∞"
    return str(int(value)) if value == int(value) else f"{value:.2f}"
