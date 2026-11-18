"""
graph_visualizer.py - High-Performance Orderly Architectural Grid & Zero-Washout PDG Visualizer
================================================================================================
Renders a structured, beautiful, and responsive Program Dependence Graph (PDG).

Key Innovations:
  1. Dynamic Architectural Gallery Grid: Automatically calculates the optimal 16:10 aspect
     ratio based on function count, organizing functions into clean, vertical card columns.
  2. Zero Washout on Hover: Vis.js background-lightening is completely suppressed by explicitly
     locking values.color to the deep theme palette; text is locked to crisp bold white with a
     solid 3px outline.
  3. Clutter Elimination: Cross-function data edges and 100+ radiating root lines are hidden by
     default on large graphs, transforming the spaghetti hairball into an orderly architectural blueprint.
  4. Real-time Scope Isolation: Select any function to immediately zoom and focus on its isolated
     control & data flow.
  5. Interactive Glassmorphic HUD: Floating glass pane displaying node ID, semantic logic, degree,
     and taint status with zero intrusive browser popups.
"""

import json
import math
from typing import Dict, List, Optional, Any, Set


def generate_pdg_html(
    pdg_graph: Dict[str, Any],
    tainted_flows: Optional[List[Dict[str, Any]]] = None,
    height: str = "720px",
    background: str = "#0b0f19"
) -> str:
    """
    Generates an orderly, high-contrast, structured HTML visualization for the PDG.
    """
    if tainted_flows is None:
        tainted_flows = []

    # Map tainted node IDs and edge pairs
    tainted_node_ids = set()
    tainted_edge_pairs = set()
    for flow in tainted_flows:
        src = flow.get("source_node")
        tgt = flow.get("sink_node")
        if src:
            tainted_node_ids.add(src)
        if tgt:
            tainted_node_ids.add(tgt)
        if src and tgt:
            tainted_edge_pairs.add((src, tgt))

    raw_nodes = pdg_graph.get("nodes", {})
    raw_edges = pdg_graph.get("edges", [])

    # 1. Discover Functions & Map Hierarchy
    functions_map: Dict[str, str] = {}
    for nid, lbl in raw_nodes.items():
        if lbl.startswith("Function "):
            fname = lbl.replace("Function ", "").split("(")[0].strip()
            functions_map[nid] = fname

    assigned_nodes: Set[str] = set()
    fn_groups: List[tuple] = []  # (fn_id, fname, [child_node_ids])

    for fn_id, fname in functions_map.items():
        child_nodes = []
        visited = {fn_id}
        queue = [fn_id]
        while queue:
            curr = queue.pop(0)
            for e in raw_edges:
                if e.get("source") == curr and e.get("kind") == "Control":
                    tgt = e.get("target")
                    if tgt and tgt not in visited and tgt not in functions_map and tgt != "root":
                        visited.add(tgt)
                        child_nodes.append(tgt)
                        queue.append(tgt)
        assigned_nodes.update(visited)
        fn_groups.append((fn_id, fname, child_nodes))

    node_to_func: Dict[str, str] = {}
    for fn_id, fname, children in fn_groups:
        node_to_func[fn_id] = fname
        for c in children:
            node_to_func[c] = fname

    available_functions = sorted([fname for _, fname, _ in fn_groups])
    globals_list = [nid for nid in raw_nodes if nid not in assigned_nodes and nid != "root"]

    # 2. Compute Dynamic Orderly 2D Gallery Grid Coordinates
    total_funcs = len(fn_groups)
    if total_funcs <= 1:
        COLS = 1
    elif total_funcs == 2:
        COLS = 2
    else:
        # Dynamic Golden Aspect Ratio calculation
        COLS = max(3, int(math.ceil(math.sqrt(total_funcs * 1.6))))

    COL_WIDTH = 340
    CARD_SPACING_Y = 86

    # Dynamic row vertical offset calculation
    total_rows = (total_funcs + COLS - 1) // COLS if COLS > 0 else 1
    row_y_offsets = [0] * max(1, total_rows)
    current_y = 120
    for r in range(total_rows):
        row_y_offsets[r] = current_y
        row_slice = fn_groups[r * COLS : (r + 1) * COLS]
        max_c = max([len(c) for _, _, c in row_slice] + [0])
        row_height = (max_c + 1) * CARD_SPACING_Y + 60
        current_y += row_height

    node_positions: Dict[str, Dict[str, int]] = {}

    # Root node positioned at top-center
    grid_center_x = max(0, ((COLS - 1) * COL_WIDTH) // 2)
    node_positions["root"] = {"x": grid_center_x, "y": -140}

    # Top-level global module statements arranged in a neat top band
    for idx, gid in enumerate(globals_list):
        gx = (idx % max(1, COLS)) * COL_WIDTH
        gy = -40 + (idx // max(1, COLS)) * 75
        node_positions[gid] = {"x": gx, "y": gy}

    # Position each function stack
    for idx, (fn_id, fname, children) in enumerate(fn_groups):
        col = idx % COLS
        row = idx // COLS
        base_x = col * COL_WIDTH
        base_y = row_y_offsets[row]

        # Function header card
        node_positions[fn_id] = {"x": base_x, "y": base_y}

        # Children flow straight down in an orderly vertical column
        for c_idx, cid in enumerate(children):
            node_positions[cid] = {"x": base_x, "y": base_y + (c_idx + 1) * CARD_SPACING_Y}

    # Fallback positioning for any remaining nodes
    for nid in raw_nodes:
        if nid not in node_positions:
            node_positions[nid] = {"x": grid_center_x, "y": 0}

    # 3. Build High-Contrast Aesthetic Nodes (Zero Washout Guaranteed)
    vis_nodes = []
    for node_id, label in raw_nodes.items():
        is_tainted = node_id in tainted_node_ids
        clean_label = label.replace("\n", " ").strip()
        scope = node_to_func.get(node_id, "Global Scope" if node_id != "root" else "Program Root")
        pos = node_positions.get(node_id, {"x": 0, "y": 0})

        # Saturated, rich color palettes with distinct typology
        if is_tainted:
            bg = "#3b0808"
            border = "#ef4444"
            glow = "#f87171"
            badge = "⚠️ TAINT"
            type_title = "CRITICAL INSECURE SINK"
        elif node_id == "root":
            bg = "#0c1d37"
            border = "#38bdf8"
            glow = "#7dd3fc"
            badge = "ROOT"
            type_title = "Program Entry Root Node"
        elif clean_label.startswith("Function"):
            bg = "#20124d"
            border = "#a855f7"
            glow = "#c084fc"
            badge = "FUNC"
            type_title = f"Function: {scope}"
        elif clean_label.startswith("If") or clean_label.startswith("For") or clean_label.startswith("While"):
            bg = "#382006"
            border = "#fbbf24"
            glow = "#fde047"
            badge = "BRANCH"
            type_title = "Control Branch Decision"
        elif clean_label.startswith("Return"):
            bg = "#3b0819"
            border = "#f43f5e"
            glow = "#fb7185"
            badge = "RETURN"
            type_title = "Return Statement"
        else:
            # Statement / Assign
            bg = "#042a1d"
            border = "#10b981"
            glow = "#34d399"
            badge = "STMT"
            type_title = "Active Statement"

        color = {
            "background": bg,
            "border": border,
            "hover": {"background": bg, "border": glow},
            "highlight": {"background": bg, "border": glow}
        }

        font = {
            "color": "#ffffff",
            "face": "Consolas, 'Cascadia Code', ui-monospace, SFMono-Regular, monospace",
            "size": 12,
            "bold": True,
            "strokeWidth": 3,
            "strokeColor": "#000000"
        }

        truncated = clean_label[:26] + "..." if len(clean_label) > 26 else clean_label
        display_label = f"[{badge}] {node_id}\n{truncated}"

        vis_nodes.append({
            "id": node_id,
            "label": display_label,
            "full_code": clean_label,
            "node_type": badge,
            "type_title": type_title,
            "scope": scope,
            "is_tainted": is_tainted,
            "x": pos["x"],
            "y": pos["y"],
            "shape": "box",
            "shapeProperties": {"borderRadius": 8},
            "widthConstraint": {"minimum": 240, "maximum": 280},
            "color": color,
            "borderWidth": 2,
            "borderWidthSelected": 3,
            "font": font,
            "margin": {"top": 8, "bottom": 8, "left": 12, "right": 12},
            "shadow": {"enabled": True, "color": "rgba(0,0,0,0.65)", "size": 8, "x": 1, "y": 2}
        })

    # 4. Build Structured Edges & Classify Clutter
    vis_edges = []
    is_large_graph = len(fn_groups) >= 6 or len(raw_nodes) >= 40

    for idx, e in enumerate(raw_edges):
        src = e.get("source")
        tgt = e.get("target")
        kind = e.get("kind")
        lbl = e.get("label", "")
        is_tainted_edge = (src, tgt) in tainted_edge_pairs
        is_root_edge = (src == "root" or tgt == "root")

        src_scope = node_to_func.get(src, "global")
        tgt_scope = node_to_func.get(tgt, "global")
        is_cross_scope = (src_scope != tgt_scope and not is_root_edge)

        if is_tainted_edge:
            color = {"color": "#ef4444", "highlight": "#f87171", "hover": "#fca5a5"}
            width = 3.5
            dashes = False
            edge_lbl = f"⚠ {lbl}"
        elif kind == "Control":
            color = {"color": "#38bdf8", "highlight": "#7dd3fc", "hover": "#bae6fd"}
            width = 2.0
            dashes = [5, 5]
            edge_lbl = ""
        else:
            # Data flow
            color = {"color": "#34d399", "highlight": "#6ee7b7", "hover": "#a7f3d0"}
            width = 2.0
            dashes = False
            edge_lbl = lbl

        vis_edges.append({
            "id": f"e{idx}",
            "from": src,
            "to": tgt,
            "label": edge_lbl,
            "kind": kind,
            "is_tainted": is_tainted_edge,
            "is_root_edge": is_root_edge,
            "is_cross_scope": is_cross_scope,
            "src_scope": src_scope,
            "tgt_scope": tgt_scope,
            "color": color,
            "width": width,
            "dashes": dashes,
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.85}},
            "smooth": {"type": "cubicBezier", "roundness": 0.2},
            "font": {"color": "#94a3b8", "size": 10, "face": "Consolas, monospace", "strokeWidth": 2, "strokeColor": "#0b0f19"}
        })

    nodes_json = json.dumps(vis_nodes).replace("</script>", "<\\/script>")
    edges_json = json.dumps(vis_edges).replace("</script>", "<\\/script>")
    funcs_json = json.dumps(available_functions).replace("</script>", "<\\/script>")

    total_nodes = len(vis_nodes)
    default_root_checked = "false" if is_large_graph else "true"
    default_cross_checked = "false" if is_large_graph else "true"

    html_template = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 0;
      background: radial-gradient(ellipse at 50% 15%, #131c2e 0%, #0c121e 50%, #050811 100%);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #e2e8f0;
      overflow: hidden;
      width: 100%;
      height: 100vh;
    }}
    #pdg-container {{
      width: 100%;
      height: {height};
      position: relative;
    }}
    /* Modern Glassmorphic Top Bar */
    .pdg-toolbar {{
      position: absolute;
      top: 10px;
      left: 12px;
      right: 12px;
      z-index: 100;
      background: rgba(12, 18, 30, 0.94);
      backdrop-filter: blur(14px);
      padding: 7px 14px;
      border-radius: 10px;
      border: 1px solid rgba(56, 189, 248, 0.3);
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      box-shadow: 0 6px 24px rgba(0, 0, 0, 0.6);
    }}
    .toolbar-left, .toolbar-right {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .select-pill {{
      background: #172338;
      color: #38bdf8;
      border: 1px solid #334767;
      padding: 5px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      outline: none;
      cursor: pointer;
      transition: all 0.2s ease;
      max-width: 260px;
    }}
    .select-pill:hover, .select-pill:focus {{
      border-color: #38bdf8;
      background: #0d1624;
      box-shadow: 0 0 8px rgba(56, 189, 248, 0.3);
    }}
    .search-input {{
      background: #172338;
      color: #f8fafc;
      border: 1px solid #334767;
      padding: 5px 10px;
      border-radius: 6px;
      font-size: 11px;
      outline: none;
      width: 150px;
      transition: all 0.2s ease;
    }}
    .search-input:focus {{
      border-color: #38bdf8;
      width: 190px;
    }}
    .btn-action {{
      background: #172338;
      color: #e2e8f0;
      border: 1px solid #334767;
      padding: 5px 11px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 11px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s ease;
    }}
    .btn-action:hover {{
      background: #1e3a5f;
      color: #38bdf8;
      border-color: #38bdf8;
    }}
    .filter-label {{
      display: flex;
      align-items: center;
      gap: 5px;
      cursor: pointer;
      user-select: none;
      color: #cbd5e1;
      font-size: 11px;
    }}
    .filter-label:hover {{ color: #ffffff; }}
    /* Interactive Glassmorphic HUD */
    #node-hud {{
      position: absolute;
      bottom: 12px;
      left: 12px;
      z-index: 100;
      background: rgba(10, 16, 28, 0.96);
      backdrop-filter: blur(16px);
      padding: 12px 16px;
      border-radius: 10px;
      border: 1px solid rgba(56, 189, 248, 0.4);
      max-width: 480px;
      min-width: 300px;
      font-size: 12px;
      box-shadow: 0 10px 35px rgba(0, 0, 0, 0.75);
    }}
    .hud-title {{
      font-weight: 700;
      color: #38bdf8;
      font-size: 13px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }}
    .hud-scope {{
      background: rgba(168, 85, 247, 0.2);
      color: #c084fc;
      border: 1px solid rgba(168, 85, 247, 0.4);
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 600;
    }}
    .hud-code {{
      background: #050811;
      border: 1px solid #1e293b;
      padding: 8px 10px;
      border-radius: 6px;
      font-family: Consolas, 'Cascadia Code', ui-monospace, monospace;
      color: #f8fafc;
      font-size: 11px;
      word-break: break-all;
      max-height: 80px;
      overflow-y: auto;
      margin-bottom: 6px;
    }}
    .hud-meta {{
      display: flex;
      gap: 14px;
      font-size: 11px;
      color: #94a3b8;
    }}
    /* Clean Legend */
    .legend {{
      position: absolute;
      bottom: 12px;
      right: 12px;
      z-index: 90;
      background: rgba(10, 16, 28, 0.92);
      backdrop-filter: blur(12px);
      padding: 9px 13px;
      border-radius: 10px;
      border: 1px solid rgba(51, 65, 85, 0.8);
      font-size: 11px;
      display: flex;
      flex-direction: column;
      gap: 5px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
    }}
    .legend-title {{
      font-weight: 700;
      color: #94a3b8;
      text-transform: uppercase;
      font-size: 10px;
      letter-spacing: 0.5px;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .dot {{
      width: 10px;
      height: 10px;
      border-radius: 3px;
      display: inline-block;
    }}
    .line-dash {{
      width: 16px;
      height: 2px;
      border-top: 2px dashed #38bdf8;
      display: inline-block;
    }}
    .line-solid {{
      width: 16px;
      height: 2px;
      background: #34d399;
      display: inline-block;
    }}
    .line-taint {{
      width: 16px;
      height: 3px;
      background: #ef4444;
      display: inline-block;
    }}
  </style>
</head>
<body>
  <div id="pdg-container">
    <!-- Toolbar -->
    <div class="pdg-toolbar">
      <div class="toolbar-left">
        <!-- Scope Filter -->
        <label style="font-weight:700; color:#38bdf8;">🎯 Scope:</label>
        <select id="scope-selector" class="select-pill">
          <option value="ALL">🌐 All Code ({total_nodes} nodes)</option>
        </select>
        <input type="text" id="node-search" class="search-input" placeholder="🔍 Search logic..." />
        <span style="color:#64748b; font-size:11px;">|</span>
        <span style="color:#94a3b8; font-size:11px; font-weight:600;">📐 Layout: Orderly Architectural Grid</span>
      </div>

      <div class="toolbar-right">
        <label class="filter-label"><input type="checkbox" id="toggle-intra" checked /> Intra-Func</label>
        <label class="filter-label"><input type="checkbox" id="toggle-cross" { 'checked' if default_cross_checked == 'true' else '' } /> Cross-Func</label>
        <label class="filter-label"><input type="checkbox" id="toggle-root" { 'checked' if default_root_checked == 'true' else '' } /> Root Fan-out</label>
        <label class="filter-label"><input type="checkbox" id="toggle-taint-only" /> Only Tainted</label>
        <button class="btn-action" onclick="resetView()">⛶ Fit View</button>
      </div>
    </div>

    <!-- Live HUD -->
    <div id="node-hud">
      <div class="hud-title">
        <span id="hud-name">Hover or click any node</span>
        <span id="hud-scope-badge" class="hud-scope">Global</span>
      </div>
      <div id="hud-code-box" class="hud-code">Point your mouse at nodes to inspect semantic AST logic, control branches, and data flows.</div>
      <div class="hud-meta">
        <span>⬅️ In-Degree: <strong id="hud-in" style="color:#38bdf8;">0</strong></span>
        <span>➡️ Out-Degree: <strong id="hud-out" style="color:#34d399;">0</strong></span>
        <span id="hud-taint-stat" style="display:none; color:#ef4444; font-weight:700;">🚨 TAINTED</span>
      </div>
    </div>

    <!-- Legend -->
    <div class="legend">
      <div class="legend-title">Typology</div>
      <div class="legend-item"><span class="dot" style="background:#20124d; border: 1px solid #a855f7;"></span> Function Def</div>
      <div class="legend-item"><span class="dot" style="background:#382006; border: 1px solid #fbbf24;"></span> Branch (If/For)</div>
      <div class="legend-item"><span class="dot" style="background:#042a1d; border: 1px solid #10b981;"></span> Statement / Assign</div>
      <div class="legend-item"><span class="dot" style="background:#3b0819; border: 1px solid #f43f5e;"></span> Return Stmt</div>
      <div class="legend-item"><span class="dot" style="background:#3b0808; border: 1px solid #ef4444;"></span> Insecure Sink</div>
      <div style="height: 2px;"></div>
      <div class="legend-title">Edges</div>
      <div class="legend-item"><span class="line-dash"></span> Control Edge</div>
      <div class="legend-item"><span class="line-solid"></span> Data Flow</div>
      <div class="legend-item"><span class="line-taint"></span> Tainted Flow</div>
    </div>
  </div>

  <script type="text/javascript">
    const rawNodes = {nodes_json};
    const rawEdges = {edges_json};
    const availableFuncs = {funcs_json};

    // Fast lookup map for nodes
    const rawNodesMap = {{}};
    rawNodes.forEach(n => {{ rawNodesMap[n.id] = n; }});

    const container = document.getElementById("pdg-container");
    const scopeSelector = document.getElementById("scope-selector");
    const nodeSearch = document.getElementById("node-search");

    // Populate scope dropdown
    availableFuncs.forEach(fn => {{
      const opt = document.createElement("option");
      opt.value = fn;
      opt.textContent = `⚡ fn: ${{fn}}`;
      scopeSelector.appendChild(opt);
    }});

    const nodesDataSet = new vis.DataSet(rawNodes);
    const edgesDataSet = new vis.DataSet(rawEdges);

    const data = {{
      nodes: nodesDataSet,
      edges: edgesDataSet
    }};

    // 100% STATIC ORDERLY ARCHITECTURAL GRID (Physics Disabled, Zero Jitter, Zero Washout)
    const baseOptions = {{
      physics: {{
        enabled: false
      }},
      interaction: {{
        hover: true,
        hoverConnectedEdges: false,
        navigationButtons: true,
        keyboard: true,
        dragNodes: true,
        dragView: true,
        zoomView: true
      }},
      nodes: {{
        // Custom chosen handlers: ZERO WASHOUT ON HOVER
        chosen: {{
          node: function(values, id, selected, hovering) {{
            const orig = rawNodesMap[id];
            if (orig && orig.color) {{
              // STRICTLY LOCK BACKGROUND COLOR: Never let vis.js lighten or bleach it!
              values.color = orig.color.background;
            }}
            if (hovering || selected) {{
              values.borderWidth = 3;
              const isTaint = orig && orig.is_tainted;
              values.borderColor = isTaint ? "#f87171" : "#38bdf8";
              values.shadow = true;
              values.shadowColor = isTaint ? "rgba(239, 68, 68, 0.9)" : "rgba(56, 189, 248, 0.85)";
              values.shadowSize = 14;
            }}
          }},
          label: function(values, id, selected, hovering) {{
            // Force label text to stay pure bold white with 3px black stroke!
            values.color = "#ffffff";
            values.strokeWidth = 3;
            values.strokeColor = "#000000";
          }}
        }}
      }},
      edges: {{
        chosen: {{
          edge: function(values, id, selected, hovering) {{
            if (hovering || selected) {{
              values.width = values.width * 1.5;
            }}
          }}
        }}
      }}
    }};

    const network = new vis.Network(container, data, baseOptions);

    // Initial fit once loaded
    network.once("afterDrawing", function() {{
      network.fit();
    }});

    function resetView() {{
      network.fit({{ animation: {{ duration: 500, easingFunction: "easeInOutQuad" }} }});
    }}

    // Filter Logic
    const intraCheck = document.getElementById("toggle-intra");
    const crossCheck = document.getElementById("toggle-cross");
    const rootCheck = document.getElementById("toggle-root");
    const taintCheck = document.getElementById("toggle-taint-only");

    function applyFilters() {{
      const selectedScope = scopeSelector.value;
      const searchQuery = (nodeSearch.value || "").toLowerCase().trim();
      const showIntra = intraCheck.checked;
      const showCross = crossCheck.checked;
      const showRoot = rootCheck.checked;
      const taintOnly = taintCheck.checked;

      // 1. Filter Nodes
      const activeNodeIds = new Set();
      const filteredNodes = rawNodes.filter(n => {{
        if (selectedScope !== "ALL" && n.scope !== selectedScope && n.id !== "root") {{
          return false;
        }}
        if (searchQuery && !n.full_code.toLowerCase().includes(searchQuery) && !n.id.toLowerCase().includes(searchQuery)) {{
          return false;
        }}
        activeNodeIds.add(n.id);
        return true;
      }});

      // 2. Filter Edges
      const filteredEdges = rawEdges.filter(e => {{
        if (!activeNodeIds.has(e.from) || !activeNodeIds.has(e.to)) return false;
        if (taintOnly && !e.is_tainted) return false;
        if (e.is_root_edge && !showRoot && selectedScope === "ALL") return false;
        if (e.is_cross_scope && !showCross && selectedScope === "ALL") return false;
        if (!e.is_root_edge && !e.is_cross_scope && !showIntra) return false;
        return true;
      }});

      nodesDataSet.clear();
      nodesDataSet.add(filteredNodes);

      edgesDataSet.clear();
      edgesDataSet.add(filteredEdges);

      setTimeout(() => resetView(), 40);
    }}

    scopeSelector.addEventListener("change", applyFilters);
    nodeSearch.addEventListener("input", applyFilters);
    intraCheck.addEventListener("change", applyFilters);
    crossCheck.addEventListener("change", applyFilters);
    rootCheck.addEventListener("change", applyFilters);
    taintCheck.addEventListener("change", applyFilters);

    // Live Node HUD Updates on Hover
    const hudName = document.getElementById("hud-name");
    const hudScopeBadge = document.getElementById("hud-scope-badge");
    const hudCodeBox = document.getElementById("hud-code-box");
    const hudIn = document.getElementById("hud-in");
    const hudOut = document.getElementById("hud-out");
    const hudTaintStat = document.getElementById("hud-taint-stat");

    function updateHud(nodeId) {{
      const node = rawNodesMap[nodeId];
      if (!node) return;

      hudName.textContent = `[${{node.node_type}}] ${{nodeId}}`;
      hudScopeBadge.textContent = node.scope;
      hudCodeBox.textContent = node.full_code;

      const connectedEdges = network.getConnectedEdges(nodeId);
      let inCount = 0;
      let outCount = 0;
      connectedEdges.forEach(eId => {{
        const e = edgesDataSet.get(eId);
        if (e) {{
          if (e.to === nodeId) inCount++;
          if (e.from === nodeId) outCount++;
        }}
      }});

      hudIn.textContent = inCount;
      hudOut.textContent = outCount;
      hudTaintStat.style.display = node.is_tainted ? "inline" : "none";
    }}

    network.on("hoverNode", function(params) {{
      updateHud(params.node);
    }});

    network.on("selectNode", function(params) {{
      if (params.nodes.length > 0) {{
        updateHud(params.nodes[0]);
      }}
    }});

    // Apply initial filter (cross-function & root fanout hidden by default for clean architecture)
    applyFilters();
  </script>
</body>
</html>
"""
    return html_template


def save_pdg_html(
    pdg_graph: Dict[str, Any],
    output_path: str,
    tainted_flows: Optional[List[Dict[str, Any]]] = None
) -> str:
    """Saves the interactive PDG visualization to a local HTML file."""
    html = generate_pdg_html(pdg_graph, tainted_flows=tainted_flows, height="100vh")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


if __name__ == "__main__":
    from pdg_extractor import extract_pdg_graph
    sample = """
def authenticate(username, token):
    valid = False
    if len(token) > 10:
        valid = True
    result = eval(token)
    return valid
"""
    graph = extract_pdg_graph(sample)
    taints = [
        {"source_node": "N0", "sink_node": "N3", "variable": "token", "description": "Tainted parameter flow into eval"}
    ]
    out_file = "interactive_pdg_preview.html"
    save_pdg_html(graph, out_file, tainted_flows=taints)
    print(f"Orderly grid PDG preview generated at: {out_file}")
