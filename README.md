# Shortest Path Finder — Dijkstra's Algorithm Visualizer

An interactive desktop application that lets you build a weighted graph on a canvas
and watch Dijkstra's algorithm find the shortest path between two nodes, step by step,
with live animation, per-node cost labels, and a detailed step log.

Built with Python and Tkinter as a Data Structures & Algorithms project.

## Features

- **Interactive graph editor** — click the canvas to add nodes, click two nodes to draw a weighted edge.
- **Animated Dijkstra** — nodes light up as they are selected (blue), settled (yellow), and the
  final shortest path is highlighted in green; tentative costs update live under each node.
- **Step log & result panel** — a scrolling log of every "processing" / "relax" step plus the
  final path and total cost.
- **Start / End selection**, **delete mode** (remove nodes or edges), and **reset graph**.
- **Login / registration screen** backed by a simple `credentials.txt` user store.
- **Animated splash screen** with progress bar.
- Catppuccin Mocha dark theme, self-loop and duplicate-edge prevention, unreachable-destination handling.

## Tech Stack

- **Language:** Python 3 (tested on 3.14)
- **GUI:** Tkinter (`tkinter`, `tkinter.ttk`) — standard library
- **Algorithm:** Dijkstra's shortest path via a binary heap (`heapq`) with lazy deletion
- No third-party dependencies.

## Requirements

- Python 3.10+ (uses `dict[int, NodeModel]` / `int | None` style type hints).
- Tkinter, which ships with the standard CPython installer.
- A `.venv` is included in the project; the interpreter lives at `.venv\Scripts\python.exe` on Windows.

## How to Run

The entry point is **`script.py`**. It creates the root window and orchestrates the
screen flow: **Splash → Login → Main graph editor**.

```bash
# From the project folder (PyCharmMiscProject):

# Windows (using the bundled venv)
.venv\Scripts\python.exe script.py

# or, with a system Python that has Tkinter
python script.py
```

Do **not** run `splash.py` or `login.py` directly — they are screen modules imported by `script.py`.

### Default login credentials

Credentials are read from `credentials.txt` (one `username:password` per line). Built-in accounts:

| Username | Password   |
|----------|------------|
| admin    | admin123   |
| student  | pass1234   |
| guest    | qwerty     |

You can also register a new account from the login screen ("Register"); it is appended to
`credentials.txt`. If `credentials.txt` is missing, the app falls back to the first three
accounts above.

### Using the app

1. Log in.
2. Click empty canvas space to **add nodes**.
3. Click one node, then another, to **add an edge** (you'll be prompted for a positive weight).
4. Use **Set Start Node** / **Set End Node**, then click a node for each.
5. Click **Run Dijkstra** to animate the search; the shortest path is highlighted in green.
6. **Delete Mode** removes nodes/edges; **Reset Graph** clears everything.

## File Overview

| File                  | Responsibility |
|-----------------------|----------------|
| `script.py`           | **Entry point.** Builds the root Tk window and switches between splash, login, and main screens. |
| `splash.py`           | Animated splash screen (typed title + progress bar), then transitions to login. |
| `login.py`            | Login / registration UI and the `_validate` / `_register` credential helpers. |
| `graph_interface.py`  | Main screen: `GraphModel`/`NodeModel`/`EdgeModel`, canvas interaction, and the Dijkstra animation driver. |
| `dijkstra.py`         | Pure algorithm: `dijkstra_generator` (yields animation frames) and `reconstruct_path`. |
| `result_panel.py`     | Sidebar results panel (path, total cost, step log) and the `_fmt` number formatter. |
| `config.py`           | Constants: window size, colour palette, fonts, node/edge styling, timings. |
| `credentials.txt`     | `username:password` store for the login screen. |

## Bug Fixes Applied

The Dijkstra core, path reconstruction, priority-queue (lazy-deletion) usage, and the
cwd-safe `credentials.txt` path (`os.path.dirname(__file__)`) were all reviewed and verified
correct via automated tests. The following genuine issues were fixed:

- **`login.py` — registration could corrupt the last credential line.** `_register` appended
  `"user:pass\n"` without checking that the existing file ended in a newline. If `credentials.txt`
  lacked a trailing newline, the new record was concatenated onto the previous user
  (e.g. `bob:secret` → `bob:secretcarol:pw`), destroying that account. Now the file is checked
  and a separating newline is written first when needed.
- **`login.py` — overly broad exception swallowing in `_register`.** The bare `except Exception`
  (which would hide programming errors like `NameError`) was narrowed to `except OSError`, the only
  failure a file append should tolerate.
- **`login.py` — success status colour was not reset.** The green "Registration successful" colour
  was set on the status label but never reset; `_update_ui` now restores the error colour so later
  messages always render correctly. The success colour hex was also corrected from the off-theme
  `#a6e38d` to the Catppuccin green `#a6e3a1`.

### Issues noted but not fixed (out of scope / not bugs)

- Passwords are stored in plain text in `credentials.txt` — fine for a coursework demo, but not
  production-safe.
- Edge weights must be positive; Dijkstra is not valid for negative weights (correctly enforced by
  the weight-entry dialog).
- Clicking between ~1.2× and 2.2× the node radius of an existing node neither adds a node nor selects
  one (it shows a "too close" hint) — intended behaviour, just noting the small dead zone.
"# Dijkstra-Visualizer-Python-" 
