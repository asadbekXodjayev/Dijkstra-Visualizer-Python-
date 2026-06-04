"""
Shortest Path Finder using Dijkstra's Algorithm
Entry point — creates the root Tk window and orchestrates screen transitions:
    SplashScreen  →  LoginScreen  →  MainGraphScreen
"""

import tkinter as tk
from config import APP_TITLE, WINDOW_SIZE, WINDOW_MIN_W, WINDOW_MIN_H, CANVAS_BG


def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry(WINDOW_SIZE)
    root.minsize(WINDOW_MIN_W, WINDOW_MIN_H)
    root.configure(bg=CANVAS_BG)

    app_state = {"logged_in_user": None, "graph": None}
    _current_frame: list = []   # mutable container so inner functions can update it

    def _clear():
        for child in root.winfo_children():
            child.destroy()

    def show_splash():
        _clear()
        from splash import SplashScreen
        frame = SplashScreen(root, on_complete=show_login)
        _current_frame[:] = [frame]

    def show_login():
        _clear()
        from login import LoginScreen
        frame = LoginScreen(root, root, on_success=lambda username: show_main(username))
        _current_frame[:] = [frame]

    def show_main(username: str):
        _clear()
        from graph_interface import MainGraphScreen, confirm_exit
        app_state["logged_in_user"] = username
        frame = MainGraphScreen(root, root, app_state)
        frame.pack(fill="both", expand=True)
        _current_frame[:] = [frame]
        root.protocol("WM_DELETE_WINDOW", lambda: confirm_exit(root))

    # Wire the window-close button on splash/login to just exit normally
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    show_splash()
    root.mainloop()


if __name__ == "__main__":
    main()
