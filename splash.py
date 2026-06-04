import tkinter as tk
from tkinter import ttk
from config import (APP_TITLE, APP_SUBTITLE, CANVAS_BG, SIDEBAR_BG,
                    FONT_TITLE, FONT_SUBTITLE, FONT_SMALL, SPLASH_DURATION_MS)

_STATUS_MILESTONES = {
    34: "Initializing graph engine…",
    68: "Loading visualization engine…",
    90: "Almost ready…",
}


class SplashScreen(tk.Frame):
    def __init__(self, parent, on_complete):
        super().__init__(parent, bg=CANVAS_BG)
        self._on_complete = on_complete
        self._title_idx = 0
        self._progress = 0
        self._step_ms = SPLASH_DURATION_MS // 50  # 50 increments of 2%
        self._build()
        self.after(200, self._animate_title)
        self.after(400, self._animate_progress)

    def _build(self):
        self.pack(fill="both", expand=True)

        # ── centre card ──────────────────────────────────────────────────────
        card = tk.Frame(self, bg=SIDEBAR_BG, padx=50, pady=36)
        card.place(relx=0.5, rely=0.42, anchor="center")

        self.title_var = tk.StringVar(value="")
        tk.Label(card, textvariable=self.title_var, bg=SIDEBAR_BG, fg="#cdd6f4",
                 font=FONT_TITLE).pack()

        tk.Label(card, text=APP_SUBTITLE, bg=SIDEBAR_BG, fg="#6c7086",
                 font=FONT_SUBTITLE).pack(pady=(4, 18))

        sep = tk.Frame(card, bg="#313244", height=1)
        sep.pack(fill="x", pady=4)

        info_rows = [
            ("Course:",     "Data Structures & Algorithms"),
            ("Project:",    "Shortest Path Finder"),
            ("Algorithm:",  "Dijkstra's Algorithm"),
        ]
        for label, value in info_rows:
            row = tk.Frame(card, bg=SIDEBAR_BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, bg=SIDEBAR_BG, fg="#6c7086",
                     font=("Segoe UI", 10), width=12, anchor="e").pack(side="left")
            tk.Label(row, text=value, bg=SIDEBAR_BG, fg="#89b4fa",
                     font=("Segoe UI", 10, "bold"), anchor="w").pack(side="left", padx=(6, 0))

        # ── progress area ─────────────────────────────────────────────────────
        prog_area = tk.Frame(self, bg=CANVAS_BG)
        prog_area.place(relx=0.5, rely=0.80, anchor="center", width=420)

        self.status_var = tk.StringVar(value="Loading…")
        tk.Label(prog_area, textvariable=self.status_var, bg=CANVAS_BG, fg="#6c7086",
                 font=FONT_SMALL).pack(pady=(0, 5))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Splash.Horizontal.TProgressbar",
                         troughcolor="#313244", background="#89b4fa", thickness=8)

        self.progress_bar = ttk.Progressbar(prog_area, orient="horizontal", length=400,
                                             mode="determinate", maximum=100,
                                             style="Splash.Horizontal.TProgressbar")
        self.progress_bar.pack()

    # ── animations ────────────────────────────────────────────────────────────

    def _animate_title(self):
        if self._title_idx <= len(APP_TITLE):
            self.title_var.set(APP_TITLE[: self._title_idx])
            self._title_idx += 1
            self.after(75, self._animate_title)

    def _animate_progress(self):
        if self._progress < 100:
            self._progress += 2
            self.progress_bar["value"] = self._progress
            if self._progress in _STATUS_MILESTONES:
                self.status_var.set(_STATUS_MILESTONES[self._progress])
            self.after(self._step_ms, self._animate_progress)
        else:
            self.status_var.set("Ready!")
            self.after(350, self._on_complete)
