import math
import tkinter as tk
from tkinter import ttk, messagebox

from config import (
    CANVAS_BG, SIDEBAR_BG, BUTTON_BG, BUTTON_FG, BUTTON_ACTIVE_BG,
    NODE_RADIUS, NODE_COLORS, EDGE_COLORS, EDGE_WIDTHS,
    FONT_BUTTON, FONT_NODE, FONT_SMALL, ANIM_STEP_DELAY_MS,
)
from dijkstra import dijkstra_generator
from result_panel import ResultPanel, _fmt


# ─────────────────────────────  Data Models  ─────────────────────────────────

class NodeModel:
    __slots__ = ("node_id", "x", "y",
                 "canvas_oval_id", "canvas_text_id", "canvas_cost_id", "state")

    def __init__(self, node_id: int, x: float, y: float):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.canvas_oval_id = None
        self.canvas_text_id = None
        self.canvas_cost_id = None
        self.state = "default"


class EdgeModel:
    __slots__ = ("edge_id", "node_a_id", "node_b_id", "weight",
                 "canvas_line_id", "canvas_label_id", "state")

    def __init__(self, edge_id: int, node_a_id: int, node_b_id: int, weight: float):
        self.edge_id = edge_id
        self.node_a_id = node_a_id
        self.node_b_id = node_b_id
        self.weight = weight
        self.canvas_line_id = None
        self.canvas_label_id = None
        self.state = "default"


class GraphModel:
    def __init__(self):
        self.nodes: dict[int, NodeModel] = {}
        self.edges: list[EdgeModel] = []
        self.adjacency: dict[int, list[tuple[int, float]]] = {}
        self._next_node_id = 1
        self._next_edge_id = 1

    # ── mutations ─────────────────────────────────────────────────────────────

    def add_node(self, x: float, y: float) -> NodeModel:
        n = NodeModel(self._next_node_id, x, y)
        self.nodes[n.node_id] = n
        self.adjacency[n.node_id] = []
        self._next_node_id += 1
        return n

    def add_edge(self, a_id: int, b_id: int, weight: float) -> EdgeModel:
        e = EdgeModel(self._next_edge_id, a_id, b_id, weight)
        self.edges.append(e)
        self._next_edge_id += 1
        self.adjacency[a_id].append((b_id, weight))
        self.adjacency[b_id].append((a_id, weight))
        return e

    def remove_node(self, node_id: int) -> list[EdgeModel]:
        """Remove node and all its edges. Returns the removed EdgeModel list."""
        removed = [e for e in self.edges
                   if e.node_a_id == node_id or e.node_b_id == node_id]
        self.edges = [e for e in self.edges
                      if e.node_a_id != node_id and e.node_b_id != node_id]
        del self.nodes[node_id]
        del self.adjacency[node_id]
        self._rebuild_adjacency()
        return removed

    def remove_edge(self, edge_id: int) -> EdgeModel | None:
        target = next((e for e in self.edges if e.edge_id == edge_id), None)
        if target:
            self.edges = [e for e in self.edges if e.edge_id != edge_id]
            self._rebuild_adjacency()
        return target

    def reset(self):
        self.nodes.clear()
        self.edges.clear()
        self.adjacency.clear()
        self._next_node_id = 1
        self._next_edge_id = 1

    # ── queries ───────────────────────────────────────────────────────────────

    def get_neighbors(self, node_id: int) -> list[tuple[int, float]]:
        return self.adjacency.get(node_id, [])

    def edge_exists(self, a_id: int, b_id: int) -> bool:
        return any(
            (e.node_a_id == a_id and e.node_b_id == b_id) or
            (e.node_a_id == b_id and e.node_b_id == a_id)
            for e in self.edges
        )

    def find_edge(self, a_id: int, b_id: int) -> EdgeModel | None:
        return next(
            (e for e in self.edges
             if (e.node_a_id == a_id and e.node_b_id == b_id) or
                (e.node_a_id == b_id and e.node_b_id == a_id)),
            None,
        )

    def _rebuild_adjacency(self):
        self.adjacency = {nid: [] for nid in self.nodes}
        for e in self.edges:
            self.adjacency[e.node_a_id].append((e.node_b_id, e.weight))
            self.adjacency[e.node_b_id].append((e.node_a_id, e.weight))


# ─────────────────────────────  Utility  ─────────────────────────────────────

def confirm_exit(root: tk.Tk):
    dlg = tk.Toplevel(root)
    dlg.title("Exit")
    dlg.geometry("310x130")
    dlg.resizable(False, False)
    dlg.configure(bg=SIDEBAR_BG)
    dlg.transient(root)
    dlg.grab_set()
    dlg.focus()

    tk.Label(dlg, text="Exit Shortest Path Finder?", bg=SIDEBAR_BG, fg="#cdd6f4",
             font=("Segoe UI", 12, "bold")).pack(pady=(22, 4))
    tk.Label(dlg, text="Any unsaved graph will be lost.", bg=SIDEBAR_BG, fg="#6c7086",
             font=FONT_SMALL).pack()

    btn_row = tk.Frame(dlg, bg=SIDEBAR_BG)
    btn_row.pack(pady=14)

    _btn = dict(font=FONT_BUTTON, relief="flat", padx=14, pady=5,
                cursor="hand2", bd=0)
    tk.Button(btn_row, text="Yes, Exit", command=root.destroy,
              bg="#f38ba8", fg="#1e1e2e",
              activebackground="#eba0ac", activeforeground="#1e1e2e",
              **_btn).pack(side="left", padx=6)
    tk.Button(btn_row, text="Cancel", command=dlg.destroy,
              bg=BUTTON_BG, fg=BUTTON_FG,
              activebackground=BUTTON_ACTIVE_BG, activeforeground=BUTTON_FG,
              **_btn).pack(side="left")

    dlg.bind("<Escape>", lambda _: dlg.destroy())


# ───────────────────────────  Main Screen  ───────────────────────────────────

class MainGraphScreen(tk.Frame):
    """
    Layout:
        col 0 (weight 3): Canvas
        col 1 (weight 1): Sidebar (buttons + ResultPanel)
        row 1 (full):     Status bar
    """

    def __init__(self, parent, root: tk.Tk, app_state: dict):
        super().__init__(parent, bg=SIDEBAR_BG)
        self._root = root
        self._app_state = app_state
        self.graph = GraphModel()
        app_state["graph"] = self.graph

        # Interaction state
        self.mode = "add_node"   # add_node | select_start | select_end | edge_pending | delete | idle
        self._pending_node: int | None = None   # first node in edge-creation
        self.start_id: int | None = None
        self.end_id: int | None = None
        self._gen = None
        self._stored_path: list[int] = []
        self._result_panel: ResultPanel | None = None

        self._build_layout()

    # ── Layout ───────────────────────────────────────────────────────────────

    def _build_layout(self):
        # Status bar anchored to the bottom first so pack reserves its space
        self._status_var = tk.StringVar(
            value="Click canvas to add nodes. Click two nodes to connect them with an edge."
        )
        tk.Label(
            self, textvariable=self._status_var,
            bg="#11111b", fg="#a6adc8",
            font=FONT_SMALL, anchor="w", padx=10, pady=3,
        ).pack(side="bottom", fill="x")

        # Main content row
        content = tk.Frame(self, bg=SIDEBAR_BG)
        content.pack(fill="both", expand=True)

        # Sidebar — fixed 260 px on the right; pack_propagate=False keeps the width
        sidebar = tk.Frame(content, bg=SIDEBAR_BG, width=260)
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        # Canvas — fills all remaining space on the left
        self.canvas = tk.Canvas(content, bg=CANVAS_BG, cursor="crosshair",
                                highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

    def _build_sidebar(self, sidebar):
        _sep = dict(bg=SIDEBAR_BG, padx=10)
        _btn = dict(bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON, relief="flat",
                    padx=8, pady=6, cursor="hand2", bd=0,
                    activebackground=BUTTON_ACTIVE_BG, activeforeground=BUTTON_FG)

        tk.Label(sidebar, text="Controls", bg=SIDEBAR_BG, fg="#cdd6f4",
                 font=("Segoe UI", 13, "bold"), pady=10).pack(fill="x", padx=10)

        # Node-role buttons
        self._btn_start = tk.Button(sidebar, text="Set Start Node",
                                    command=self._mode_select_start, **_btn)
        self._btn_start.pack(fill="x", padx=10, pady=2)

        self._btn_end = tk.Button(sidebar, text="Set End Node",
                                  command=self._mode_select_end, **_btn)
        self._btn_end.pack(fill="x", padx=10, pady=2)

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10, pady=6)

        # Algorithm buttons
        self._btn_run = tk.Button(sidebar, text="Run Dijkstra",
                                  command=self._run_dijkstra, **_btn)
        self._btn_run.pack(fill="x", padx=10, pady=2)

        self._btn_show = tk.Button(sidebar, text="Show Path",
                                   command=self._show_path, state="disabled", **_btn)
        self._btn_show.pack(fill="x", padx=10, pady=2)

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10, pady=6)

        # Utility buttons
        self._btn_delete = tk.Button(sidebar, text="Delete Mode: OFF",
                                     command=self._toggle_delete_mode, **_btn)
        self._btn_delete.pack(fill="x", padx=10, pady=2)

        self._btn_reset = tk.Button(sidebar, text="Reset Graph",
                                    command=self._reset_graph, **_btn)
        self._btn_reset.pack(fill="x", padx=10, pady=2)

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10, pady=6)

        tk.Button(sidebar, text="Exit",
                  command=lambda: confirm_exit(self._root), **_btn
                  ).pack(fill="x", padx=10, pady=2)

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10, pady=8)

        # Result panel (lower sidebar)
        self._result_panel = ResultPanel(sidebar)
        self._result_panel.set_show_path_callback(self._show_path)
        self._result_panel.pack(fill="both", expand=True, padx=2, pady=2)

    # ── Mode helpers ─────────────────────────────────────────────────────────

    def _mode_select_start(self):
        self._cancel_pending_edge()
        self.mode = "select_start"
        self._set_status("Click a node to mark it as the Start node.")

    def _mode_select_end(self):
        self._cancel_pending_edge()
        self.mode = "select_end"
        self._set_status("Click a node to mark it as the End node.")

    def _toggle_delete_mode(self):
        if self.mode == "delete":
            self.mode = "add_node"
            self._btn_delete.config(text="Delete Mode: OFF", relief="flat")
            self._set_status("Delete mode OFF. Click canvas to add nodes.")
        else:
            self._cancel_pending_edge()
            self.mode = "delete"
            self._btn_delete.config(text="Delete Mode: ON", relief="sunken")
            self._set_status("Delete mode ON. Click a node or edge to remove it.")

    def _cancel_pending_edge(self):
        if self._pending_node is not None:
            self._pending_node = None
        if self.mode == "edge_pending":
            self.mode = "add_node"

    def _set_status(self, msg: str):
        self._status_var.set(msg)

    # ── Canvas interaction ────────────────────────────────────────────────────

    def _on_canvas_click(self, event):
        if self.mode == "idle":
            return

        x, y = float(event.x), float(event.y)
        hit = self._find_node_at(x, y)

        if self.mode == "delete":
            if hit is not None:
                self._delete_node(hit)
            else:
                hit_edge = self._find_edge_at(x, y)
                if hit_edge is not None:
                    self._delete_edge(hit_edge)
            return

        if self.mode == "select_start":
            if hit is not None:
                self._set_start(hit)
            return

        if self.mode == "select_end":
            if hit is not None:
                self._set_end(hit)
            return

        if self.mode == "edge_pending":
            if hit is not None:
                if hit == self._pending_node:
                    self._set_status("Self-loops are not allowed. Click a different node or click empty space to cancel.")
                    return
                if self.graph.edge_exists(self._pending_node, hit):
                    self._set_status("An edge already exists between those two nodes.")
                    self._cancel_pending_edge()
                    return
                self._prompt_weight(self._pending_node, hit)
            else:
                self._cancel_pending_edge()
                self._set_status("Edge creation cancelled. Click canvas to add nodes.")
            return

        # mode == "add_node"
        if hit is not None:
            # First click on a node → begin edge
            self._pending_node = hit
            self.mode = "edge_pending"
            self._set_status(f"Node {hit} selected. Now click another node to add an edge (or empty space to cancel).")
        else:
            self._create_node(x, y)

    # ── Hit tests ─────────────────────────────────────────────────────────────

    def _find_node_at(self, x: float, y: float) -> int | None:
        for node in self.graph.nodes.values():
            if math.hypot(x - node.x, y - node.y) <= NODE_RADIUS + 4:
                return node.node_id
        return None

    def _find_edge_at(self, x: float, y: float) -> int | None:
        for edge in self.graph.edges:
            na = self.graph.nodes[edge.node_a_id]
            nb = self.graph.nodes[edge.node_b_id]
            if _dist_point_segment(x, y, na.x, na.y, nb.x, nb.y) <= 7:
                return edge.edge_id
        return None

    # ── Node / edge creation ──────────────────────────────────────────────────

    def _create_node(self, x: float, y: float):
        for node in self.graph.nodes.values():
            if math.hypot(x - node.x, y - node.y) < NODE_RADIUS * 2.2:
                self._set_status("Too close to an existing node. Click further away.")
                return
        node = self.graph.add_node(x, y)
        self._draw_node(node)
        self._set_status(f"Node {node.node_id} added. Click it then another node to draw an edge.")

    def _draw_node(self, node: NodeModel):
        r = NODE_RADIUS
        fill, outline = NODE_COLORS["default"]
        oid = self.canvas.create_oval(
            node.x - r, node.y - r, node.x + r, node.y + r,
            fill=fill, outline=outline, width=2, tags="node",
        )
        tid = self.canvas.create_text(
            node.x, node.y, text=str(node.node_id),
            font=FONT_NODE, fill="#11111b", tags="node_label",
        )
        cid = self.canvas.create_text(
            node.x, node.y + r + 13, text="∞",   # ∞
            font=FONT_SMALL, fill="#6c7086", tags="cost_label",
        )
        node.canvas_oval_id = oid
        node.canvas_text_id = tid
        node.canvas_cost_id = cid

    def _prompt_weight(self, a_id: int, b_id: int):
        dlg = tk.Toplevel(self._root)
        dlg.title("Edge Weight")
        dlg.geometry("300x140")
        dlg.resizable(False, False)
        dlg.configure(bg=SIDEBAR_BG)
        dlg.transient(self._root)
        dlg.grab_set()

        tk.Label(dlg, text=f"Weight for edge  {a_id}  ↔  {b_id}:",
                 bg=SIDEBAR_BG, fg="#cdd6f4", font=("Segoe UI", 11)).pack(pady=(18, 4))

        entry = tk.Entry(dlg, font=("Segoe UI", 13), width=10, justify="center",
                         bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
                         relief="flat", highlightthickness=1,
                         highlightcolor="#89b4fa", highlightbackground="#45475a")
        entry.pack(pady=4)
        entry.insert(0, "1")
        entry.select_range(0, "end")
        entry.focus()

        def _ok():
            try:
                w = float(entry.get())
                if w <= 0:
                    raise ValueError
            except ValueError:
                entry.config(highlightcolor="#f38ba8", highlightbackground="#f38ba8")
                return
            dlg.destroy()
            edge = self.graph.add_edge(a_id, b_id, w)
            self._draw_edge(edge)
            self._pending_node = None
            self.mode = "add_node"
            self._set_status(f"Edge {a_id} ↔ {b_id} added (weight = {_fmt(w)}).")

        def _cancel():
            dlg.destroy()
            self._cancel_pending_edge()
            self._set_status("Edge creation cancelled.")

        btn_row = tk.Frame(dlg, bg=SIDEBAR_BG)
        btn_row.pack(pady=10)
        _b = dict(font=FONT_BUTTON, relief="flat", padx=12, pady=4, cursor="hand2", bd=0)
        tk.Button(btn_row, text="OK", command=_ok,
                  bg="#89b4fa", fg="#1e1e2e",
                  activebackground="#74c7ec", activeforeground="#1e1e2e",
                  **_b).pack(side="left", padx=5)
        tk.Button(btn_row, text="Cancel", command=_cancel,
                  bg=BUTTON_BG, fg=BUTTON_FG,
                  activebackground=BUTTON_ACTIVE_BG, activeforeground=BUTTON_FG,
                  **_b).pack(side="left")

        entry.bind("<Return>", lambda _: _ok())
        dlg.bind("<Escape>", lambda _: _cancel())

    def _draw_edge(self, edge: EdgeModel):
        na = self.graph.nodes[edge.node_a_id]
        nb = self.graph.nodes[edge.node_b_id]
        lid = self.canvas.create_line(
            na.x, na.y, nb.x, nb.y,
            fill=EDGE_COLORS["default"], width=EDGE_WIDTHS["default"],
            tags="edge",
        )
        self.canvas.tag_lower(lid)   # render under nodes
        mx, my = (na.x + nb.x) / 2, (na.y + nb.y) / 2
        lbl_id = self.canvas.create_text(
            mx, my - 11,
            text=_fmt(edge.weight),
            font=FONT_SMALL, fill="#cdd6f4", tags="edge_label",
        )
        self.canvas.tag_lower(lbl_id)
        edge.canvas_line_id = lid
        edge.canvas_label_id = lbl_id

    # ── Node role assignment ──────────────────────────────────────────────────

    def _set_start(self, node_id: int):
        if self.start_id is not None and self.start_id in self.graph.nodes:
            prev = self.graph.nodes[self.start_id]
            if prev.state == "start":
                prev.state = "default"
                self._apply_node_color(self.start_id, "default")
        self.start_id = node_id
        self.graph.nodes[node_id].state = "start"
        self._apply_node_color(node_id, "start")
        self.mode = "add_node"
        self._set_status(f"Start node: {node_id}. Set an end node or click 'Run Dijkstra'.")

    def _set_end(self, node_id: int):
        if self.end_id is not None and self.end_id in self.graph.nodes:
            prev = self.graph.nodes[self.end_id]
            if prev.state == "end":
                prev.state = "default"
                self._apply_node_color(self.end_id, "default")
        self.end_id = node_id
        self.graph.nodes[node_id].state = "end"
        self._apply_node_color(node_id, "end")
        self.mode = "add_node"
        self._set_status(f"End node: {node_id}. Click 'Run Dijkstra' to find the shortest path.")

    # ── Canvas drawing helpers ────────────────────────────────────────────────

    def _apply_node_color(self, node_id: int, state: str):
        node = self.graph.nodes.get(node_id)
        if not node:
            return
        fill, outline = NODE_COLORS.get(state, NODE_COLORS["default"])
        self.canvas.itemconfig(node.canvas_oval_id, fill=fill, outline=outline)

    def _apply_edge_color(self, edge_id: int, state: str):
        edge = next((e for e in self.graph.edges if e.edge_id == edge_id), None)
        if not edge:
            return
        self.canvas.itemconfig(
            edge.canvas_line_id,
            fill=EDGE_COLORS.get(state, EDGE_COLORS["default"]),
            width=EDGE_WIDTHS.get(state, EDGE_WIDTHS["default"]),
        )

    def _update_cost_label(self, node_id: int, cost: float):
        node = self.graph.nodes.get(node_id)
        if node:
            self.canvas.itemconfig(node.canvas_cost_id, text=_fmt(cost))

    # ── Delete ───────────────────────────────────────────────────────────────

    def _delete_node(self, node_id: int):
        node = self.graph.nodes.get(node_id)
        if not node:
            return
        removed_edges = self.graph.remove_node(node_id)
        for e in removed_edges:
            if e.canvas_line_id:
                self.canvas.delete(e.canvas_line_id)
            if e.canvas_label_id:
                self.canvas.delete(e.canvas_label_id)
        self.canvas.delete(node.canvas_oval_id)
        self.canvas.delete(node.canvas_text_id)
        self.canvas.delete(node.canvas_cost_id)
        if self.start_id == node_id:
            self.start_id = None
        if self.end_id == node_id:
            self.end_id = None
        self._set_status(f"Node {node_id} deleted.")

    def _delete_edge(self, edge_id: int):
        removed = self.graph.remove_edge(edge_id)
        if removed:
            if removed.canvas_line_id:
                self.canvas.delete(removed.canvas_line_id)
            if removed.canvas_label_id:
                self.canvas.delete(removed.canvas_label_id)
            self._set_status("Edge deleted.")

    # ── Dijkstra animation ────────────────────────────────────────────────────

    def _run_dijkstra(self):
        if self.start_id is None or self.end_id is None:
            self._set_status("Set both a Start node and an End node before running.")
            return
        if self.start_id not in self.graph.nodes or self.end_id not in self.graph.nodes:
            self._set_status("Start or end node was deleted. Please reassign and try again.")
            return
        if self.start_id == self.end_id:
            self._set_status("Start and End nodes must be different.")
            return
        if len(self.graph.nodes) < 2:
            self._set_status("Add at least 2 nodes before running.")
            return

        # Reset visual state (keep start/end colours)
        for node in self.graph.nodes.values():
            if node.state not in ("start", "end"):
                node.state = "default"
                self._apply_node_color(node.node_id, "default")
            self._update_cost_label(node.node_id, float("inf"))
        for edge in self.graph.edges:
            edge.state = "default"
            self._apply_edge_color(edge.edge_id, "default")

        self._stored_path = []
        self._btn_show.config(state="disabled")
        if self._result_panel:
            self._result_panel.clear()

        self._lock_buttons()
        self._gen = dijkstra_generator(self.graph, self.start_id, self.end_id)
        self._update_cost_label(self.start_id, 0)
        self._set_status("Running Dijkstra's Algorithm…")
        self.after(ANIM_STEP_DELAY_MS, self._step_animation)

    def _step_animation(self):
        try:
            frame = next(self._gen)
            self._apply_frame(frame)
            if frame["type"] != "done":
                self.after(ANIM_STEP_DELAY_MS, self._step_animation)
            else:
                self._on_complete(frame)
        except StopIteration:
            self._unlock_buttons()

    def _apply_frame(self, frame: dict):
        ftype = frame["type"]

        if ftype == "current":
            u = frame["node"]
            if u != self.start_id and u != self.end_id:
                self._apply_node_color(u, "current")
            self._update_cost_label(u, frame["cost"])
            if self._result_panel:
                self._result_panel.log_step(f"  Processing Node {u}   cost = {_fmt(frame['cost'])}")

        elif ftype == "visit":
            u = frame["node"]
            if u != self.start_id and u != self.end_id:
                self.graph.nodes[u].state = "visited"
                self._apply_node_color(u, "visited")

        elif ftype == "relax":
            v = frame["node"]
            self._update_cost_label(v, frame["cost"])
            if self._result_panel:
                self._result_panel.log_step(
                    f"    Relax Node {v}   new best = {_fmt(frame['cost'])}"
                )

    def _on_complete(self, frame: dict):
        if not frame.get("reachable"):
            self._set_status(
                f"No path exists from Node {self.start_id} to Node {self.end_id}."
            )
            if self._result_panel:
                self._result_panel.display_result([], float("inf"))
                self._result_panel.log_step("DONE — destination is unreachable.")
        else:
            path = frame["path"]
            total = frame["total_cost"]
            self._stored_path = path

            for nid in path:
                if nid != self.start_id and nid != self.end_id:
                    self.graph.nodes[nid].state = "path"
                    self._apply_node_color(nid, "path")

            for i in range(len(path) - 1):
                edge = self.graph.find_edge(path[i], path[i + 1])
                if edge:
                    edge.state = "path"
                    self._apply_edge_color(edge.edge_id, "path")

            path_str = " → ".join(str(n) for n in path)
            self._set_status(
                f"Shortest path: {path_str}   |   Total cost: {_fmt(total)}"
            )
            if self._result_panel:
                self._result_panel.display_result(path, total)
                self._result_panel.log_step(f"DONE — total cost = {_fmt(total)}")

            self._btn_show.config(state="normal")

        self._unlock_buttons()

    def _show_path(self):
        if not self._stored_path:
            return
        path = self._stored_path
        for nid in path:
            if nid != self.start_id and nid != self.end_id:
                self._apply_node_color(nid, "path")
        for i in range(len(path) - 1):
            edge = self.graph.find_edge(path[i], path[i + 1])
            if edge:
                self._apply_edge_color(edge.edge_id, "path")
        self._set_status(
            "Path: " + " → ".join(str(n) for n in path)
        )

    def _reset_graph(self):
        self.canvas.delete("all")
        self.graph.reset()
        self.start_id = None
        self.end_id = None
        self._pending_node = None
        self.mode = "add_node"
        self._stored_path = []
        self._btn_show.config(state="disabled")
        self._btn_delete.config(text="Delete Mode: OFF", relief="flat")
        if self._result_panel:
            self._result_panel.clear()
        self._set_status("Graph reset. Click canvas to add nodes.")

    # ── Button lock/unlock ────────────────────────────────────────────────────

    def _lock_buttons(self):
        self.mode = "idle"
        for btn in (self._btn_start, self._btn_end, self._btn_run,
                    self._btn_show, self._btn_delete, self._btn_reset):
            btn.config(state="disabled")

    def _unlock_buttons(self):
        self.mode = "add_node"
        for btn in (self._btn_start, self._btn_end, self._btn_run,
                    self._btn_delete, self._btn_reset):
            btn.config(state="normal")


# ── Private geometry helper ───────────────────────────────────────────────────

def _dist_point_segment(px, py, ax, ay, bx, by) -> float:
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
