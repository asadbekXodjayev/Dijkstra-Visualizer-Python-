APP_TITLE = "Shortest Path Finder"
APP_SUBTITLE = "Dijkstra's Algorithm Visualizer"
WINDOW_SIZE = "1100x720"
WINDOW_MIN_W = 900
WINDOW_MIN_H = 600

SPLASH_DURATION_MS = 4000
ANIM_STEP_DELAY_MS = 250
NODE_RADIUS = 22

# Palette (Catppuccin Mocha)
CANVAS_BG = "#1e1e2e"
SIDEBAR_BG = "#181825"
BUTTON_BG = "#313244"
BUTTON_FG = "#cdd6f4"
BUTTON_ACTIVE_BG = "#45475a"

FONT_TITLE = ("Segoe UI", 26, "bold")
FONT_SUBTITLE = ("Segoe UI", 12)
FONT_MAIN = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_NODE = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_LOG = ("Consolas", 8)

# Node state → (fill, outline)
NODE_COLORS = {
    "default": ("#cdd6f4", "#585b70"),
    "current": ("#4dabf7", "#1971c2"),   # blue  — being processed
    "visited": ("#ffd43b", "#e67700"),   # yellow — settled
    "start":   ("#ff922b", "#d9480f"),   # orange
    "end":     ("#fa5252", "#c92a2a"),   # crimson
    "path":    ("#51cf66", "#2f9e44"),   # green  — shortest path
}

EDGE_COLORS = {
    "default": "#585b70",
    "path":    "#51cf66",
}
EDGE_WIDTHS = {
    "default": 2,
    "path":    4,
}
