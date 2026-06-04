import os
import tkinter as tk
from tkinter import messagebox
from config import (APP_TITLE, CANVAS_BG, SIDEBAR_BG,
                    BUTTON_BG, BUTTON_FG, BUTTON_ACTIVE_BG,
                    FONT_MAIN, FONT_BUTTON, FONT_SMALL)

_FALLBACK_CREDS = [("admin", "admin123"), ("student", "pass1234"), ("guest", "qwerty")]
_CREDS_FILE = os.path.join(os.path.dirname(__file__), "credentials.txt")


class LoginScreen(tk.Frame):
    def __init__(self, parent, root, on_success):
        super().__init__(parent, bg=CANVAS_BG)
        self._root = root
        self._on_success = on_success
        self._is_login_mode = True
        self._build()

    def _build(self):
        self.pack(fill="both", expand=True)

        # ── outer card ────────────────────────────────────────────────────────
        card = tk.Frame(self, bg=SIDEBAR_BG, padx=44, pady=36)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420)

        # Header
        self._title_label = tk.Label(card, text="Welcome Back", 
                 bg=SIDEBAR_BG, fg="#cdd6f4", font=("Segoe UI", 18, "bold"))
        self._title_label.pack()
        
        self._subtitle_label = tk.Label(card, text="Sign in to continue", 
                 bg=SIDEBAR_BG, fg="#6c7086", font=FONT_SMALL)
        self._subtitle_label.pack(pady=(2, 20))

        # Username field
        tk.Label(card, text="Username", bg=SIDEBAR_BG, fg="#a6adc8",
                 font=FONT_SMALL, anchor="w").pack(fill="x")
        self._user_entry = self._make_entry(card, show=None)
        self._user_entry.pack(fill="x", pady=(3, 12), ipady=5)

        # Password field
        tk.Label(card, text="Password", bg=SIDEBAR_BG, fg="#a6adc8",
                 font=FONT_SMALL, anchor="w").pack(fill="x")
        self._pass_entry = self._make_entry(card, show="*")
        self._pass_entry.pack(fill="x", pady=(3, 8), ipady=5)

        # Confirm password field (for registration only) - hidden initially
        self._confirm_frame = tk.Frame(card, bg=SIDEBAR_BG)
        tk.Label(self._confirm_frame, text="Confirm Password", bg=SIDEBAR_BG, fg="#a6adc8",
                 font=FONT_SMALL, anchor="w").pack(fill="x")
        self._confirm_entry = self._make_entry(self._confirm_frame, show="*")
        self._confirm_entry.pack(fill="x", pady=(3, 8), ipady=5)

        # Status
        self._status_var = tk.StringVar()
        self._status_label = tk.Label(card, textvariable=self._status_var, bg=SIDEBAR_BG,
                 fg="#f38ba8", font=FONT_SMALL, height=1)
        self._status_label.pack(pady=(0, 10))

        # Buttons
        btn_row = tk.Frame(card, bg=SIDEBAR_BG)
        btn_row.pack(fill="x")

        self._btn_login = tk.Button(btn_row, text="Login", command=self._on_login,
                  bg="#89b4fa", fg="#1e1e2e", font=FONT_BUTTON,
                  relief="flat", padx=10, pady=6, cursor="hand2", bd=0,
                  activebackground=BUTTON_ACTIVE_BG, activeforeground=BUTTON_FG)
        self._btn_login.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self._btn_register = tk.Button(btn_row, text="Register", command=self._on_register,
                  bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON,
                  relief="flat", padx=10, pady=6, cursor="hand2", bd=0,
                  activebackground=BUTTON_ACTIVE_BG, activeforeground=BUTTON_FG)
        self._btn_register.pack(side="left", fill="x", expand=True)

        # Toggle text
        self._toggle_var = tk.StringVar(value="Don't have an account?")
        tk.Label(card, textvariable=self._toggle_var, bg=SIDEBAR_BG, fg="#6c7086",
                 font=FONT_SMALL).pack(pady=(10, 0))

        # Key bindings
        self._user_entry.focus()
        self._user_entry.bind("<Return>", lambda e: self._pass_entry.focus())
        self._pass_entry.bind("<Return>", lambda e: self._on_login())
        self._confirm_entry.bind("<Return>", lambda e: self._on_register())

    @staticmethod
    def _make_entry(parent, show):
        return tk.Entry(
            parent, font=FONT_MAIN, show=show or "",
            bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
            relief="flat", highlightthickness=1,
            highlightcolor="#89b4fa", highlightbackground="#45475a",
        )

    # ── actions ─────────────────────────────────────────────────────────────

    def _on_login(self):
        if self._is_login_mode:
            username = self._user_entry.get().strip()
            password = self._pass_entry.get()
            if _validate(username, password):
                self._on_success(username)
            else:
                self._status_var.set("Invalid username or password.")
                self._pass_entry.delete(0, "end")
                self._user_entry.delete(0, "end")
                self._user_entry.focus()
        else:
            # Switch back to login mode
            self._is_login_mode = True
            self._update_ui()

    def _on_register(self):
        if not self._is_login_mode:
            username = self._user_entry.get().strip()
            password = self._pass_entry.get()
            confirm = self._confirm_entry.get()

            # Validation
            if not username:
                self._status_var.set("Please enter username.")
                self._user_entry.config(highlightbackground="#f38ba8", highlightcolor="#f38ba8")
                return

            if len(username) < 2:
                self._status_var.set("Username must be at least 2 characters.")
                self._user_entry.config(highlightbackground="#f38ba8", highlightcolor="#f38ba8")
                return

            if len(username) > 30:
                self._status_var.set("Username must be less than 30 characters.")
                self._user_entry.config(highlightbackground="#f38ba8", highlightcolor="#f38ba8")
                return

            # Check for valid characters
            for c in username:
                if not (c.isalnum() or c == '_'):
                    self._status_var.set("Username can only contain letters, numbers, and underscores.")
                    self._user_entry.config(highlightbackground="#f38ba8", highlightcolor="#f38ba8")
                    return

            if not password:
                self._status_var.set("Please enter password.")
                self._pass_entry.config(highlightbackground="#f38ba8", highlightcolor="#f38ba8")
                return

            if len(password) < 4:
                self._status_var.set("Password must be at least 4 characters.")
                self._pass_entry.config(highlightbackground="#f38ba8", highlightcolor="#f38ba8")
                return

            if password != confirm:
                self._status_var.set("Passwords do not match.")
                self._confirm_entry.config(highlightbackground="#f38ba8", highlightcolor="#f38ba8")
                return

            # Attempt registration
            if _register(username, password):
                self._status_label.config(fg="#a6e3a1")
                self._status_var.set("Registration successful! Logging in...")
                self._on_success(username)
            else:
                self._status_var.set("Username already exists.")
                self._user_entry.config(highlightbackground="#f38ba8", highlightcolor="#f38ba8")
                self._pass_entry.config(highlightbackground="#f38ba8", highlightcolor="#f38ba8")
                self._confirm_entry.config(highlightbackground="#f38ba8", highlightcolor="#f38ba8")
        else:
            # Switch to register mode
            self._is_login_mode = False
            self._update_ui()

    def _update_ui(self):
        """Update UI when switching between login and register modes"""
        # Clear error highlights
        self._user_entry.config(highlightbackground="#45475a", highlightcolor="#89b4fa")
        self._pass_entry.config(highlightbackground="#45475a", highlightcolor="#89b4fa")
        self._confirm_entry.config(highlightbackground="#45475a", highlightcolor="#89b4fa")
        self._status_label.config(fg="#f38ba8")  # reset to error colour after any green success message
        self._status_var.set("")
        
        if self._is_login_mode:
            # Login mode
            self._title_label.config(text="Welcome Back")
            self._subtitle_label.config(text="Sign in to continue")
            self._toggle_var.set("Don't have an account?")
            self._btn_login.config(text="Login", bg="#89b4fa", fg="#1e1e2e")
            self._btn_register.config(text="Register", bg=BUTTON_BG, fg=BUTTON_FG)
            self._confirm_frame.pack_forget()  # Hide confirm password
        else:
            # Register mode
            self._title_label.config(text="Create Account")
            self._subtitle_label.config(text="Register a new account")
            self._toggle_var.set("Already have an account?")
            self._btn_login.config(text="Login", bg=BUTTON_BG, fg=BUTTON_FG)
            self._btn_register.config(text="Register", bg="#89b4fa", fg="#1e1e2e")
            self._confirm_frame.pack(fill="x", pady=(3, 8))  # Show confirm password


# ── standalone helpers ────────────────────────────────────────────────────────

def _validate(username: str, password: str) -> bool:
    try:
        with open(_CREDS_FILE, "r") as fh:
            for line in fh:
                line = line.strip()
                if ":" in line:
                    u, p = line.split(":", 1)
                    if u == username and p == password:
                        return True
    except FileNotFoundError:
        for u, p in _FALLBACK_CREDS:
            if u == username and p == password:
                return True
    return False


def _register(username: str, password: str) -> bool:
    """Register a new user. Returns True on success, False if username exists."""
    # Check if username already exists
    try:
        with open(_CREDS_FILE, "r") as fh:
            for line in fh:
                line = line.strip()
                if ":" in line:
                    u, _ = line.split(":", 1)
                    if u == username:
                        return False
    except FileNotFoundError:
        pass  # File doesn't exist yet, which is fine for first registration

    # Append new user. Guard against a missing trailing newline in the existing
    # file, otherwise the new record would be concatenated onto the last line.
    try:
        needs_leading_newline = False
        try:
            with open(_CREDS_FILE, "rb") as fh:
                data = fh.read()
            if data and not data.endswith((b"\n", b"\r")):
                needs_leading_newline = True
        except FileNotFoundError:
            pass
        with open(_CREDS_FILE, "a") as fh:
            if needs_leading_newline:
                fh.write("\n")
            fh.write(f"{username}:{password}\n")
        return True
    except OSError as e:
        print(f"Registration error: {e}")
        return False