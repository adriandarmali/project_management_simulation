import io
import re
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict, deque

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Project Simulator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }

:root {
    --navy:        #1e2a3a;
    --teal:        #0d9488;
    --teal-h:      #0f766e;
    --teal-light:  #f0fdfa;
    --teal-border: #99f6e4;
    --slate:       #64748b;
    --border:      #e2e8f0;
    --bg:          #f8fafc;
    --card:        #ffffff;
    --red:         #ef4444;
    --amber:       #f59e0b;
    --green:       #10b981;
}

.stApp { background: var(--bg); }
#MainMenu, footer, header { visibility: hidden; }

/* App header */
.app-header {
    padding: 24px 0 16px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0;
}
.app-title {
    font-size: 24px; font-weight: 700; color: var(--navy); margin: 0;
    letter-spacing: -0.02em;
}
.app-desc { font-size: 13px; color: var(--slate); margin-top: 2px; }

/* Step indicator */
.steps-wrap {
    display: flex; align-items: center; gap: 0;
    padding: 18px 0 0 0; margin-bottom: 28px;
}
.step-item {
    display: flex; align-items: center; gap: 8px;
    font-size: 13px; font-weight: 600; color: var(--slate);
    padding: 8px 16px 10px 16px;
    border-bottom: 2px solid transparent;
    cursor: default;
}
.step-item.active { color: var(--teal); border-bottom-color: var(--teal); }
.step-item.done   { color: var(--navy); cursor: pointer; }
.step-num {
    width: 22px; height: 22px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; flex-shrink: 0;
    background: var(--border); color: var(--slate);
}
.step-item.active .step-num { background: var(--teal); color: white; }
.step-item.done .step-num   { background: var(--green); color: white; }
.step-connector { width: 32px; height: 1px; background: var(--border); flex-shrink: 0; }

/* Page headings */
.pg-title { font-size: 18px; font-weight: 700; color: var(--navy); margin-bottom: 2px; }
.pg-sub   { font-size: 13px; color: var(--slate); margin-bottom: 20px; }

/* Section label */
.sec-lbl {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--slate); margin: 18px 0 8px 0;
}

/* Activity row */
.act-row {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 16px; background: var(--card);
    border: 1px solid var(--border); border-radius: 8px; margin-bottom: 5px;
}
.act-lbl {
    font-family: 'DM Mono', monospace; font-size: 12px; font-weight: 500;
    background: var(--navy); color: white;
    width: 28px; height: 28px; border-radius: 6px;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.act-name  { font-size: 13px; font-weight: 600; color: var(--navy); flex: 1; }
.act-range { font-family: 'DM Mono', monospace; font-size: 11px; color: var(--slate); }
.act-preds { font-size: 11px; color: var(--teal); font-weight: 500; }

/* Edit panel */
.edit-panel {
    background: var(--teal-light); border: 1px solid var(--teal-border);
    border-radius: 8px; padding: 20px 22px; margin: 2px 0 10px 0;
}

/* Upload panel */
.upload-panel {
    background: #fafafa; border: 1px dashed var(--border);
    border-radius: 8px; padding: 20px 22px; margin: 10px 0;
}

/* Stat card */
.stat-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 18px; text-align: center;
}
.stat-val {
    font-size: 30px; font-weight: 700; color: var(--navy);
    font-family: 'DM Mono', monospace; line-height: 1;
}
.stat-lbl {
    font-size: 11px; font-weight: 600; color: var(--slate);
    text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px;
}

/* Percentile row */
.pct-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 14px; border-radius: 6px; margin: 3px 0;
    font-size: 13px; font-weight: 600;
}

/* Badge */
.badge {
    display: inline-block; background: var(--teal-light); color: var(--teal);
    font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px;
    margin: 2px; font-family: 'DM Mono', monospace; border: 1px solid var(--teal-border);
}

/* Alerts */
.alert-err  { background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:10px 14px; font-size:13px; color:#991b1b; font-weight:500; margin-bottom:6px; }
.alert-warn { background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:10px 14px; font-size:13px; color:#92400e; font-weight:500; margin-bottom:6px; }
.alert-ok   { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:10px 14px; font-size:13px; color:#166534; font-weight:500; margin-bottom:6px; }

hr { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

/* Buttons */
div.stButton > button {
    border-radius: 6px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 13px !important; transition: all 0.15s !important;
}
div.stButton > button[kind="primary"] {
    background: var(--teal) !important; border-color: var(--teal) !important; color: white !important;
}
div.stButton > button[kind="primary"]:hover {
    background: var(--teal-h) !important; border-color: var(--teal-h) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input {
    border-radius: 6px !important; font-family: 'DM Mono', monospace !important; font-size: 13px !important;
}
label { font-size: 12px !important; font-weight: 600 !important; color: var(--slate) !important; }
.stMultiSelect [data-baseweb="tag"] { background: var(--teal-light) !important; color: var(--teal) !important; }
.stProgress > div > div { background: var(--teal) !important; }

/* Preview table */
.preview-ok  { color: var(--green); font-weight: 700; }
.preview-err { color: var(--red);   font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "activities":   [],
    "page":         0,
    "sim_results":  None,
    "edit_idx":     None,
    "panel_open":   False,
    "del_confirm":  None,
    "upload_open":  False,
    "upload_preview": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Core helpers ──────────────────────────────────────────────────────────────
def nav(p):
    st.session_state.page = p
    st.session_state.panel_open = False
    st.session_state.edit_idx = None
    st.session_state.del_confirm = None
    st.session_state.upload_open = False

def te(a):
    return round((a["min_d"] + 4 * a["avg_d"] + a["max_d"]) / 6, 1)

def is_valid_label(s):
    return bool(re.match(r'^[A-Za-z0-9]+$', s))

def topo_sort(activities):
    lm = {a["label"]: i for i, a in enumerate(activities)}
    indegree = defaultdict(int)
    adj = defaultdict(list)
    for i, a in enumerate(activities):
        for p in a["predecessors"]:
            if p in lm:
                adj[lm[p]].append(i)
                indegree[i] += 1
    queue = deque(i for i in range(len(activities)) if indegree[i] == 0)
    order = []
    while queue:
        n = queue.popleft()
        order.append(n)
        for nb in adj[n]:
            indegree[nb] -= 1
            if indegree[nb] == 0:
                queue.append(nb)
    return (order, adj) if len(order) == len(activities) else None

def forward_pass(activities, durations, topo):
    order, _ = topo
    lm = {a["label"]: j for j, a in enumerate(activities)}
    ef = np.zeros(len(activities))
    for i in order:
        preds = [lm[p] for p in activities[i]["predecessors"] if p in lm]
        ef[i] = max((ef[j] for j in preds), default=0.0) + durations[i]
    return ef


# ── Full validation ───────────────────────────────────────────────────────────
def validate(activities, strict=True):
    """Returns (errors, warnings). errors block progress, warnings are advisory."""
    errors = []
    warnings = []

    if not activities:
        errors.append("No activities added yet.")
        return errors, warnings

    labels = [a["label"] for a in activities]

    # Duplicate labels
    seen = set()
    for lb in labels:
        if lb in seen:
            errors.append(f"Duplicate label '{lb}' detected.")
        seen.add(lb)

    for a in activities:
        lb = a["label"]

        # Invalid label characters
        if not is_valid_label(lb):
            errors.append(f"Label '{lb}' contains invalid characters. Use letters and numbers only.")

        # Self-reference
        if lb in a["predecessors"]:
            errors.append(f"Activity '{lb}' lists itself as a predecessor.")

        # Unknown predecessors
        for p in a["predecessors"]:
            if p not in labels:
                errors.append(f"Activity '{lb}' references unknown predecessor '{p}'.")

        # Duration logic
        if a["min_d"] > a["avg_d"] or a["avg_d"] > a["max_d"]:
            errors.append(f"Activity '{lb}': durations must satisfy min ≤ most likely ≤ max.")

        # Zero durations
        if a["min_d"] == 0 and a["avg_d"] == 0 and a["max_d"] == 0:
            warnings.append(f"Activity '{lb}': all durations are zero. Is this intentional?")

        # Degenerate distribution
        if a["min_d"] == a["avg_d"] == a["max_d"] and a["min_d"] > 0:
            warnings.append(f"Activity '{lb}': min = most likely = max. No uncertainty — simulation will be deterministic for this activity.")

        # Very large duration
        if a["max_d"] > 5200:
            warnings.append(f"Activity '{lb}': maximum duration exceeds 5,200 units. Please verify this is correct.")

        # Whitespace-only name
        if not a["name"].strip():
            errors.append(f"Activity '{lb}': name cannot be blank.")

    # No start node
    if not errors:
        has_start = any(len(a["predecessors"]) == 0 for a in activities)
        if not has_start:
            errors.append("No start activity found. At least one activity must have no predecessors.")

        # No end node (every activity is someone's predecessor)
        all_preds = set(p for a in activities for p in a["predecessors"])
        has_end = any(a["label"] not in all_preds for a in activities)
        if not has_end:
            errors.append("No end activity found. At least one activity must have no successors.")

        # Circular dependency
        if topo_sort(activities) is None:
            errors.append("Circular dependency detected. Check that no activity indirectly depends on itself.")

        # Disconnected graph (only warn, don't block)
        if len(activities) > 1 and topo_sort(activities):
            topo = topo_sort(activities)
            if topo:
                # Check reachability from all start nodes
                lm = {a["label"]: i for i, a in enumerate(activities)}
                adj_fwd = defaultdict(list)
                for i, a in enumerate(activities):
                    for p in a["predecessors"]:
                        if p in lm:
                            adj_fwd[lm[p]].append(i)
                starts = [i for i, a in enumerate(activities) if not a["predecessors"]]
                visited = set()
                queue = deque(starts)
                while queue:
                    n = queue.popleft()
                    if n in visited:
                        continue
                    visited.add(n)
                    for nb in adj_fwd[n]:
                        queue.append(nb)
                if len(visited) < len(activities):
                    unreachable = [activities[i]["label"] for i in range(len(activities)) if i not in visited]
                    warnings.append(f"Activities {unreachable} are not reachable from any start node. The graph may be disconnected.")

        # Duplicate names (warn only)
        names = [a["name"].strip().lower() for a in activities]
        name_seen = set()
        for nm in names:
            if nm in name_seen:
                warnings.append(f"Two activities share the name '{nm}'. Labels are still unique, but this may cause confusion.")
            name_seen.add(nm)

    return errors, warnings


# ── Monte Carlo ───────────────────────────────────────────────────────────────
def monte_carlo(activities, n_sim, dist_type, progress_cb=None):
    topo = topo_sort(activities)
    if not topo:
        return None
    finish_times = []
    path_counts = defaultdict(int)
    for s in range(n_sim):
        if progress_cb and s % 500 == 0:
            progress_cb(s / n_sim)
        durations = []
        for a in activities:
            lo, mi, hi = a["min_d"], a["avg_d"], a["max_d"]
            if dist_type == "PERT Beta":
                mu = (lo + 4 * mi + hi) / 6
                sigma = (hi - lo) / 6
                if sigma < 1e-9:
                    durations.append(mu)
                    continue
                mn = np.clip((mu - lo) / (hi - lo + 1e-9), 0.01, 0.99)
                vn = min((sigma / (hi - lo + 1e-9)) ** 2, mn * (1 - mn) * 0.999)
                al = max(mn * (mn * (1 - mn) / vn - 1), 0.1)
                be = max((1 - mn) * (mn * (1 - mn) / vn - 1), 0.1)
                durations.append(np.random.beta(al, be) * (hi - lo) + lo)
            else:
                durations.append(np.random.triangular(lo, mi, hi))
        ef = forward_pass(activities, durations, topo)
        finish_times.append(max(ef))
        path_counts[activities[int(np.argmax(ef))]["label"]] += 1
    return {"finish_times": np.array(finish_times), "path_counts": dict(path_counts)}


# ── CSV helpers ───────────────────────────────────────────────────────────────
CSV_TEMPLATE = """name,label,predecessors,min_duration,avg_duration,max_duration
Design,A,,16,21,26
Build Prototype,B,A,3,6,9
Evaluate Equipment,C,A,5,7,9
Test Prototype,D,B,2,3,4
Write Equipment Report,E,"C,D",4,6,8
Write Methods Report,F,"C,D",6,8,10
Write Final Report,G,"E,F",1,2,3
"""

def parse_csv(content: str, existing_labels: list):
    """Returns (rows, row_errors) where rows are dicts ready to import."""
    try:
        df = pd.read_csv(io.StringIO(content))
    except Exception as e:
        return [], [f"Could not parse CSV: {e}"]

    required = {"name", "label", "min_duration", "avg_duration", "max_duration"}
    missing_cols = required - set(c.strip().lower() for c in df.columns)
    if missing_cols:
        return [], [f"Missing required columns: {', '.join(missing_cols)}"]

    # Normalise column names
    df.columns = [c.strip().lower() for c in df.columns]

    rows = []
    row_errors = []
    seen_labels = set(existing_labels)
    file_labels = set()

    for idx, row in df.iterrows():
        line = idx + 2  # 1-indexed + header
        errs = []

        name = str(row.get("name", "")).strip()
        label = str(row.get("label", "")).strip().upper()
        preds_raw = str(row.get("predecessors", "")).strip()
        preds = [p.strip().upper() for p in preds_raw.split(",") if p.strip()] if preds_raw and preds_raw.lower() != "nan" else []

        try:
            min_d = float(row["min_duration"])
            avg_d = float(row["avg_duration"])
            max_d = float(row["max_duration"])
        except Exception:
            errs.append("Duration values must be numbers.")
            min_d = avg_d = max_d = 0.0

        if not name:
            errs.append("Name is blank.")
        if not label:
            errs.append("Label is blank.")
        elif not is_valid_label(label):
            errs.append(f"Label '{label}' contains invalid characters.")
        elif label in file_labels:
            errs.append(f"Label '{label}' is duplicated within the file.")
        elif label in seen_labels:
            errs.append(f"Label '{label}' already exists in the project.")

        if label in preds:
            errs.append("Activity lists itself as a predecessor.")
        if min_d > avg_d or avg_d > max_d:
            errs.append("Durations must satisfy: min ≤ most likely ≤ max.")
        if min_d < 0 or avg_d < 0 or max_d < 0:
            errs.append("Durations cannot be negative.")

        file_labels.add(label)
        rows.append({
            "line": line,
            "activity": {"name": name, "label": label, "predecessors": preds,
                         "min_d": min_d, "avg_d": avg_d, "max_d": max_d},
            "errors": errs,
        })

    # Cross-check predecessor references across file
    all_labels_after = set(existing_labels) | {r["activity"]["label"] for r in rows if not r["errors"]}
    for r in rows:
        for p in r["activity"]["predecessors"]:
            if p not in all_labels_after:
                r["errors"].append(f"Predecessor '{p}' not found in file or existing activities.")

    # Circular check on the full merged set (if no row errors)
    if not any(r["errors"] for r in rows):
        merged = [r["activity"] for r in rows]
        if topo_sort(merged) is None:
            row_errors.append("Circular dependency detected within the uploaded file.")

    return rows, row_errors


# ── Network diagram ───────────────────────────────────────────────────────────
def draw_network(activities):
    topo = topo_sort(activities)
    if not topo:
        return None
    order, adj = topo
    lm = {a["label"]: i for i, a in enumerate(activities)}
    levels = [0] * len(activities)
    for idx in order:
        preds = [lm[p] for p in activities[idx]["predecessors"] if p in lm]
        if preds:
            levels[idx] = max(levels[p] for p in preds) + 1
    max_lv = max(levels) if levels else 0
    lv_count = defaultdict(int)
    lv_pos = defaultdict(int)
    for i in order:
        lv_count[levels[i]] += 1
    xp = [0.0] * len(activities)
    yp = [0.0] * len(activities)
    for i in order:
        lv = levels[i]
        xp[i] = lv / max(max_lv, 1)
        yp[i] = (lv_pos[lv] + 0.5) / lv_count[lv]
        lv_pos[lv] += 1

    fig = go.Figure()
    for i, a in enumerate(activities):
        for p in a["predecessors"]:
            if p in lm:
                j = lm[p]
                dx, dy = xp[i] - xp[j], yp[i] - yp[j]
                fig.add_trace(go.Scatter(
                    x=[xp[j], xp[i]], y=[yp[j], yp[i]], mode="lines",
                    line=dict(color="#e2e8f0", width=2), showlegend=False, hoverinfo="skip",
                ))
                fig.add_annotation(
                    ax=xp[j] + 0.72 * dx, ay=yp[j] + 0.72 * dy,
                    x=xp[j] + 0.82 * dx,  y=yp[j] + 0.82 * dy,
                    xref="x", yref="y", axref="x", ayref="y",
                    showarrow=True, arrowhead=2, arrowsize=1.4, arrowwidth=2, arrowcolor="#94a3b8",
                )
    for i, a in enumerate(activities):
        _te = te(a)
        var = round(((a["max_d"] - a["min_d"]) / 6) ** 2, 2)
        fig.add_trace(go.Scatter(
            x=[xp[i]], y=[yp[i]], mode="markers+text",
            marker=dict(size=54, color="#1e2a3a", line=dict(color="white", width=3)),
            text=[f"<b>{a['label']}</b>"],
            textposition="middle center",
            textfont=dict(size=14, color="white", family="DM Mono"),
            hovertemplate=(
                f"<b>{a['name']}</b><br>"
                f"Range: {a['min_d']} / {a['avg_d']} / {a['max_d']}<br>"
                f"Expected (te): <b>{_te}</b><br>"
                f"Variance: {var}<br>"
                f"Predecessors: {', '.join(a['predecessors']) or 'None'}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))
        fig.add_annotation(
            x=xp[i], y=yp[i] - 0.1,
            text=f"<b>{a['name']}</b><br><span style='color:#64748b;font-size:10px;font-family:DM Mono'>te = {_te}</span>",
            showarrow=False,
            font=dict(size=11, family="DM Sans", color="#1e2a3a"),
            bgcolor="rgba(255,255,255,0.92)", borderpad=4,
        )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=10, b=30), height=420,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 1.2]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.28, 1.28]),
    )
    return fig


# ── Add / Edit form ───────────────────────────────────────────────────────────
def render_edit_panel(prefill=None, exclude_label=None):
    is_edit = prefill is not None
    st.markdown(f"**{'Edit Activity' if is_edit else 'New Activity'}**")

    c1, c2 = st.columns([3, 1])
    with c1:
        name = st.text_input(
            "Activity Name",
            value=prefill["name"] if prefill else "",
            placeholder="e.g. Design prototype",
            key="ep_name",
        )
    with c2:
        label = st.text_input(
            "Label",
            value=prefill["label"] if prefill else "",
            placeholder="A",
            max_chars=6,
            key="ep_label",
            help="Short unique identifier, letters and numbers only (e.g. A, B, T1).",
        ).upper().strip()

    existing = [a["label"] for a in st.session_state.activities if a["label"] != exclude_label]
    preds = st.multiselect(
        "Predecessors",
        options=existing,
        default=[p for p in (prefill["predecessors"] if prefill else []) if p in existing],
        key="ep_preds",
        help="Select all activities that must be completed before this one starts. Leave empty if this is a start activity.",
    )

    st.markdown("**Duration range**")
    d1, d2, d3 = st.columns(3)
    with d1:
        min_d = st.number_input(
            "Minimum", min_value=0.0,
            value=float(prefill["min_d"]) if prefill else 1.0,
            step=0.5, key="ep_min",
            help="Best-case duration — the shortest this activity could realistically take.",
        )
    with d2:
        avg_d = st.number_input(
            "Most Likely", min_value=0.0,
            value=float(prefill["avg_d"]) if prefill else 3.0,
            step=0.5, key="ep_avg",
            help="The duration you would expect in a typical scenario.",
        )
    with d3:
        max_d = st.number_input(
            "Maximum", min_value=0.0,
            value=float(prefill["max_d"]) if prefill else 5.0,
            step=0.5, key="ep_max",
            help="Worst-case duration — if everything goes wrong.",
        )

    # Inline validation
    errors = []
    warnings = []
    if not name.strip():
        errors.append("Name is required.")
    if not label:
        errors.append("Label is required.")
    elif not is_valid_label(label):
        errors.append("Label must contain only letters and numbers (e.g. A, B2, T1).")
    elif label == exclude_label:
        pass  # unchanged in edit
    elif label in [a["label"] for a in st.session_state.activities if a["label"] != exclude_label]:
        errors.append(f"Label '{label}' is already in use.")
    if label and label in preds:
        errors.append("An activity cannot be its own predecessor.")
    if min_d > avg_d or avg_d > max_d:
        errors.append("Durations must satisfy: min ≤ most likely ≤ max.")
    if min_d == 0 and avg_d == 0 and max_d == 0:
        warnings.append("All durations are zero — is this intentional?")
    if min_d == avg_d == max_d and min_d > 0:
        warnings.append("Min = most likely = max. This activity has no uncertainty.")
    if max_d > 5200:
        warnings.append(f"Maximum duration of {max_d} seems very large. Please verify.")

    for w in warnings:
        st.markdown(f'<div class="alert-warn">⚠ {w}</div>', unsafe_allow_html=True)

    b1, b2, _ = st.columns([1, 1, 4])
    with b1:
        save_clicked = st.button("Save", type="primary", key="ep_save", use_container_width=True)
    with b2:
        if st.button("Cancel", key="ep_cancel", use_container_width=True):
            st.session_state.panel_open = False
            st.session_state.edit_idx = None
            st.rerun()

    if save_clicked:
        if errors:
            for e in errors:
                st.error(e)
        else:
            return True, {
                "name": name.strip(), "label": label, "predecessors": preds,
                "min_d": min_d, "avg_d": avg_d, "max_d": max_d,
            }
    return False, None


# ── App header ────────────────────────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="app-header">
        <div class="app-title">📊 Project Simulator</div>
        <div class="app-desc">Model project timelines using PERT estimation and Monte Carlo simulation.</div>
    </div>
    """, unsafe_allow_html=True)


# ── Step indicator ────────────────────────────────────────────────────────────
def render_steps():
    acts = st.session_state.activities
    errs, _ = validate(acts) if acts else (["empty"], [])
    step_done = [
        len(acts) > 0 and not errs,
        len(acts) > 0 and not errs,
    ]
    steps = ["Project Setup", "Network Diagram", "Simulation"]
    cur = st.session_state.page

    cols = st.columns(len(steps))
    for i, (col, name) in enumerate(zip(cols, steps)):
        with col:
            is_active = i == cur
            is_done = i < cur and (step_done[i - 1] if i > 0 else True)
            btn_type = "primary" if is_active else "secondary"
            label = f"{'✓ ' if is_done else ''}{i+1}. {name}"
            if st.button(label, key=f"step_{i}", use_container_width=True, type=btn_type):
                nav(i)
                st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)


# ── CSV Upload section ────────────────────────────────────────────────────────
def render_upload_section():
    st.markdown('<div class="sec-lbl">Bulk Import via CSV</div>', unsafe_allow_html=True)
    with st.expander("Upload CSV / Download Template", expanded=st.session_state.upload_open):

        dl_col, _ = st.columns([2, 4])
        with dl_col:
            st.download_button(
                "⬇ Download CSV Template",
                data=CSV_TEMPLATE,
                file_name="project_template.csv",
                mime="text/csv",
                use_container_width=True,
                help="Download a pre-filled example. Edit in Excel or Google Sheets, then upload.",
            )

        st.markdown("""
        <div style="font-size:12px;color:#64748b;margin:8px 0 12px 0">
        Columns: <code>name</code>, <code>label</code>, <code>predecessors</code> (comma-separated, leave blank if none),
        <code>min_duration</code>, <code>avg_duration</code>, <code>max_duration</code>
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Upload your CSV file",
            type=["csv"],
            key="csv_uploader",
            help="CSV must include the required columns. Extra columns are ignored.",
        )

        if uploaded:
            content = uploaded.read().decode("utf-8")
            existing_labels = [a["label"] for a in st.session_state.activities]
            rows, file_errors = parse_csv(content, existing_labels)

            if file_errors:
                for e in file_errors:
                    st.markdown(f'<div class="alert-err">✕ {e}</div>', unsafe_allow_html=True)
                return

            # Preview table
            preview_data = []
            has_errors = False
            for r in rows:
                status = "✕ " + "; ".join(r["errors"]) if r["errors"] else "✓ OK"
                if r["errors"]:
                    has_errors = True
                a = r["activity"]
                preview_data.append({
                    "Line": r["line"],
                    "Label": a["label"],
                    "Name": a["name"],
                    "Predecessors": ", ".join(a["predecessors"]) or "—",
                    "Min": a["min_d"],
                    "Likely": a["avg_d"],
                    "Max": a["max_d"],
                    "Status": status,
                })

            st.markdown('<div class="sec-lbl">Preview</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)

            if has_errors:
                st.markdown('<div class="alert-err">✕ Fix the errors above before importing. No activities were added.</div>', unsafe_allow_html=True)
                return

            # Merge options
            merge_mode = st.radio(
                "Import mode",
                ["Append to existing activities", "Replace all existing activities"],
                horizontal=True,
                help="Append adds new rows alongside existing ones. Replace clears everything first.",
            )

            clean_rows = [r["activity"] for r in rows]

            if st.button(f"Import {len(clean_rows)} Activities", type="primary", use_container_width=True):
                if merge_mode.startswith("Replace"):
                    st.session_state.activities = clean_rows
                else:
                    st.session_state.activities.extend(clean_rows)
                st.session_state.sim_results = None
                st.session_state.upload_open = False
                st.success(f"Imported {len(clean_rows)} activities.")
                st.rerun()


# ── Page 0: Project Setup ─────────────────────────────────────────────────────
def page_builder():
    st.markdown('<div class="pg-title">Step 1 — Project Setup</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Define your project activities, durations, and dependencies.</div>', unsafe_allow_html=True)

    acts = st.session_state.activities

    # Activity list
    if acts:
        st.markdown('<div class="sec-lbl">Activities — use ↑ ↓ to reorder</div>', unsafe_allow_html=True)
        for i, a in enumerate(acts):
            preds_str = " → ".join(a["predecessors"]) + f" → {a['label']}" if a["predecessors"] else f"{a['label']}  (start)"
            ci, cu, cd2, ce, cd = st.columns([6, 0.55, 0.55, 1, 1])

            with ci:
                st.markdown(f"""
                <div class="act-row">
                    <div class="act-lbl">{a['label']}</div>
                    <div style="flex:1">
                        <div class="act-name">{a['name']}</div>
                        <div class="act-preds">{preds_str}</div>
                    </div>
                    <div class="act-range">{a['min_d']} / {a['avg_d']} / {a['max_d']} &nbsp;·&nbsp; te = {te(a)}</div>
                </div>
                """, unsafe_allow_html=True)

            with cu:
                if i > 0:
                    if st.button("↑", key=f"up_{i}", use_container_width=True, help="Move up"):
                        st.session_state.activities[i - 1], st.session_state.activities[i] = \
                            st.session_state.activities[i], st.session_state.activities[i - 1]
                        st.session_state.sim_results = None
                        st.rerun()

            with cd2:
                if i < len(acts) - 1:
                    if st.button("↓", key=f"dn_{i}", use_container_width=True, help="Move down"):
                        st.session_state.activities[i + 1], st.session_state.activities[i] = \
                            st.session_state.activities[i], st.session_state.activities[i + 1]
                        st.session_state.sim_results = None
                        st.rerun()

            with ce:
                if st.button("Edit", key=f"edit_{i}", use_container_width=True):
                    st.session_state.edit_idx = i
                    st.session_state.panel_open = True
                    st.session_state.del_confirm = None
                    st.session_state.upload_open = False
                    st.rerun()

            with cd:
                if st.session_state.del_confirm == i:
                    if st.button("Confirm", key=f"delok_{i}", use_container_width=True, type="primary"):
                        removed = acts[i]["label"]
                        st.session_state.activities.pop(i)
                        for a2 in st.session_state.activities:
                            a2["predecessors"] = [p for p in a2["predecessors"] if p != removed]
                        st.session_state.del_confirm = None
                        st.session_state.sim_results = None
                        if st.session_state.edit_idx == i:
                            st.session_state.edit_idx = None
                            st.session_state.panel_open = False
                        st.rerun()
                else:
                    if st.button("Delete", key=f"del_{i}", use_container_width=True):
                        st.session_state.del_confirm = i
                        st.rerun()

            # Inline edit panel
            if st.session_state.edit_idx == i and st.session_state.panel_open:
                with st.container():
                    st.markdown('<div class="edit-panel">', unsafe_allow_html=True)
                    saved, new_act = render_edit_panel(prefill=a, exclude_label=a["label"])
                    st.markdown('</div>', unsafe_allow_html=True)
                    if saved and new_act:
                        st.session_state.activities[i] = new_act
                        st.session_state.panel_open = False
                        st.session_state.edit_idx = None
                        st.session_state.sim_results = None
                        st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center;padding:40px 0;">
            <div style="font-size:36px;margin-bottom:10px">📋</div>
            <div style="font-size:14px;font-weight:600;color:#94a3b8">No activities yet</div>
            <div style="font-size:12px;margin-top:4px;color:#cbd5e1">Add manually below or import a CSV file</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Toolbar
    add_open = st.session_state.panel_open and st.session_state.edit_idx is None
    t1, t2, t3 = st.columns([2, 2, 1])
    with t1:
        if st.button(
            "Close Form" if add_open else "+ Add Activity",
            type="secondary" if add_open else "primary",
            use_container_width=True, key="btn_add",
        ):
            st.session_state.panel_open = not add_open
            st.session_state.edit_idx = None
            st.session_state.del_confirm = None
            st.rerun()
    with t2:
        if st.button("Load Example Project", use_container_width=True,
                     help="Loads the Computer Design example from the PERT textbook."):
            st.session_state.activities = [
                {"name": "Design",                "label": "A", "predecessors": [],         "min_d": 16, "avg_d": 21, "max_d": 26},
                {"name": "Build Prototype",        "label": "B", "predecessors": ["A"],      "min_d": 3,  "avg_d": 6,  "max_d": 9 },
                {"name": "Evaluate Equipment",     "label": "C", "predecessors": ["A"],      "min_d": 5,  "avg_d": 7,  "max_d": 9 },
                {"name": "Test Prototype",          "label": "D", "predecessors": ["B"],      "min_d": 2,  "avg_d": 3,  "max_d": 4 },
                {"name": "Write Equipment Report", "label": "E", "predecessors": ["C", "D"], "min_d": 4,  "avg_d": 6,  "max_d": 8 },
                {"name": "Write Methods Report",   "label": "F", "predecessors": ["C", "D"], "min_d": 6,  "avg_d": 8,  "max_d": 10},
                {"name": "Write Final Report",     "label": "G", "predecessors": ["E", "F"], "min_d": 1,  "avg_d": 2,  "max_d": 3 },
            ]
            st.session_state.sim_results = None
            st.session_state.panel_open = False
            st.session_state.edit_idx = None
            st.rerun()
    with t3:
        if st.button("Clear All", use_container_width=True):
            st.session_state.activities = []
            st.session_state.sim_results = None
            st.session_state.panel_open = False
            st.session_state.edit_idx = None
            st.rerun()

    # Add form
    if add_open:
        st.markdown('<div class="edit-panel" style="margin-top:12px">', unsafe_allow_html=True)
        saved, new_act = render_edit_panel()
        st.markdown('</div>', unsafe_allow_html=True)
        if saved and new_act:
            st.session_state.activities.append(new_act)
            st.session_state.panel_open = False
            st.session_state.sim_results = None
            st.rerun()

    # CSV upload
    st.markdown("<br>", unsafe_allow_html=True)
    render_upload_section()

    # Validation summary + continue
    st.markdown("<hr>", unsafe_allow_html=True)
    if acts:
        errs, warns = validate(acts)
        for w in warns:
            st.markdown(f'<div class="alert-warn">⚠ {w}</div>', unsafe_allow_html=True)
        if errs:
            for e in errs:
                st.markdown(f'<div class="alert-err">✕ {e}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-ok">✓ All activities look valid. Ready to continue.</div>', unsafe_allow_html=True)
            if st.button("Continue to Network Diagram →", type="primary", use_container_width=True):
                nav(1)
                st.rerun()


# ── Page 1: Network Diagram ───────────────────────────────────────────────────
def page_network():
    st.markdown('<div class="pg-title">Step 2 — Network Diagram</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Verify dependency structure before running the simulation. Hover over nodes for details.</div>', unsafe_allow_html=True)

    errs, warns = validate(st.session_state.activities)
    if errs:
        for e in errs:
            st.markdown(f'<div class="alert-err">✕ {e}</div>', unsafe_allow_html=True)
        if st.button("← Back to Setup", use_container_width=True):
            nav(0); st.rerun()
        return

    for w in warns:
        st.markdown(f'<div class="alert-warn">⚠ {w}</div>', unsafe_allow_html=True)

    fig = draw_network(st.session_state.activities)
    if fig:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="sec-lbl">Activity Summary</div>', unsafe_allow_html=True)
    rows = [{
        "Label": a["label"],
        "Name": a["name"],
        "Predecessors": ", ".join(a["predecessors"]) or "—",
        "Min": a["min_d"],
        "Most Likely": a["avg_d"],
        "Max": a["max_d"],
        "Expected (te)": round((a["min_d"] + 4 * a["avg_d"] + a["max_d"]) / 6, 2),
        "Variance": round(((a["max_d"] - a["min_d"]) / 6) ** 2, 2),
    } for a in st.session_state.activities]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("What do these columns mean?"):
        st.markdown("""
        **Expected (te)** — The PERT expected duration: `(min + 4×most_likely + max) / 6`.
        It weights the most likely estimate four times more than the extremes.

        **Variance** — Measures uncertainty: `((max − min) / 6)²`.
        A higher variance means the activity duration is harder to predict.
        """)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back to Setup", use_container_width=True):
            nav(0); st.rerun()
    with c2:
        if st.button("Continue to Simulation →", type="primary", use_container_width=True):
            nav(2); st.rerun()


# ── Page 2: Simulation ────────────────────────────────────────────────────────
def page_simulation():
    st.markdown('<div class="pg-title">Step 3 — Monte Carlo Simulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Run thousands of simulated project scenarios to estimate completion probability.</div>', unsafe_allow_html=True)

    errs, warns = validate(st.session_state.activities)
    if errs:
        for e in errs:
            st.markdown(f'<div class="alert-err">✕ {e}</div>', unsafe_allow_html=True)
        if st.button("← Back to Setup", use_container_width=True):
            nav(0); st.rerun()
        return

    for w in warns:
        st.markdown(f'<div class="alert-warn">⚠ {w}</div>', unsafe_allow_html=True)

    # Check for no uncertainty
    all_deterministic = all(a["min_d"] == a["avg_d"] == a["max_d"] for a in st.session_state.activities)
    if all_deterministic:
        st.markdown('<div class="alert-warn">⚠ All activities have identical min/most likely/max durations. The simulation will produce a single deterministic result with no spread.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-lbl">Settings</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        n_sim = st.select_slider(
            "Iterations",
            options=[500, 1000, 5000, 10000, 25000, 50000],
            value=10000,
            help="Number of times the simulation reruns with randomly sampled durations. More iterations = more accurate results, but slower. 10,000 is a reliable default.",
        )
    with c2:
        dist = st.radio(
            "Duration Distribution",
            ["PERT Beta", "Triangular"],
            horizontal=True,
            help=(
                "**PERT Beta**: Uses a weighted formula (min + 4×likely + max) / 6 to define the distribution. "
                "More accurate for project estimation because it emphasises the most likely value.\n\n"
                "**Triangular**: Treats all three points equally. Simpler and faster, but less statistically rigorous."
            ),
        )

    if st.button("Run Simulation", type="primary", use_container_width=True):
        bar = st.progress(0, text="Running simulation...")
        results = monte_carlo(
            st.session_state.activities, n_sim, dist,
            progress_cb=lambda p: bar.progress(p, text=f"Running simulation... {int(p * 100)}%"),
        )
        bar.progress(1.0, text="Complete.")
        st.session_state.sim_results = results
        st.rerun()

    if not st.session_state.sim_results:
        st.markdown("""
        <div style="text-align:center;padding:40px 0;color:#94a3b8;">
            <div style="font-size:13px;font-weight:600">Configure settings above and click Run Simulation.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    res = st.session_state.sim_results
    ft = res["finish_times"]
    if len(ft) == 0:
        st.error("Simulation returned no results. Check your project for errors.")
        return

    mean_ft = float(np.mean(ft))
    std_ft  = float(np.std(ft))
    p50  = float(np.percentile(ft, 50))
    p75  = float(np.percentile(ft, 75))
    p80  = float(np.percentile(ft, 80))
    p90  = float(np.percentile(ft, 90))
    p95  = float(np.percentile(ft, 95))

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="sec-lbl">Results</div>', unsafe_allow_html=True)

    for col, val, lbl in zip(
        st.columns(4),
        [f"{mean_ft:.1f}", f"± {std_ft:.1f}", f"{min(ft):.1f}", f"{max(ft):.1f}"],
        ["Expected Finish", "Std. Deviation", "Minimum Observed", "Maximum Observed"],
    ):
        with col:
            st.markdown(
                f'<div class="stat-card"><div class="stat-val">{val}</div><div class="stat-lbl">{lbl}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col_hist, col_pct = st.columns([3, 2])

    with col_hist:
        st.markdown('<div class="sec-lbl">Completion Time Distribution</div>', unsafe_allow_html=True)
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=ft, nbinsx=60,
            marker=dict(color="#0d9488", opacity=0.75, line=dict(color="white", width=0.4)),
            hovertemplate="Finish: %{x:.1f}<br>Count: %{y}<extra></extra>",
        ))
        for v, lb, col in [(mean_ft, "Mean", "#1e2a3a"), (p50, "P50", "#10b981"), (p90, "P90", "#ef4444")]:
            fig_hist.add_vline(
                x=v, line=dict(color=col, width=1.5, dash="dash"),
                annotation_text=f" {lb}={v:.1f}",
                annotation_font=dict(color=col, size=11, family="DM Mono"),
            )
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=30), height=280,
            xaxis=dict(title="Completion Time", showgrid=False, tickfont=dict(family="DM Mono", size=11)),
            yaxis=dict(title="Frequency", showgrid=True, gridcolor="#f1f5f9", tickfont=dict(family="DM Mono", size=11)),
            showlegend=False, bargap=0.04, font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

    with col_pct:
        st.markdown(
            '<div class="sec-lbl">Confidence Intervals</div>',
            unsafe_allow_html=True,
        )
        with st.expander("What does this mean?"):
            st.markdown(
                "**P90 = 42** means: in 90% of simulated scenarios, the project finished by week 42. "
                "Use this to set deadlines with a known level of risk tolerance."
            )
        for lbl, val, bg, fg in [
            ("P50 — 50% confidence", p50, "#f0fdf4", "#166534"),
            ("P75 — 75% confidence", p75, "#fefce8", "#854d0e"),
            ("P80 — 80% confidence", p80, "#fff7ed", "#9a3412"),
            ("P90 — 90% confidence", p90, "#fef2f2", "#991b1b"),
            ("P95 — 95% confidence", p95, "#fdf4ff", "#6b21a8"),
        ]:
            st.markdown(f"""
            <div class="pct-row" style="background:{bg};color:{fg}">
                <span>{lbl}</span>
                <span style="font-family:'DM Mono',monospace;font-size:16px">{val:.1f}</span>
            </div>""", unsafe_allow_html=True)

    if res["path_counts"]:
        st.markdown("<hr>", unsafe_allow_html=True)
        col_bn, col_bn_help = st.columns([4, 2])
        with col_bn:
            st.markdown('<div class="sec-lbl">Most Frequent Bottleneck</div>', unsafe_allow_html=True)
        with col_bn_help:
            with st.expander("What is a bottleneck?"):
                st.markdown(
                    "The bottleneck is the activity that most often determined when the project finished. "
                    "It is not always the same as the PERT critical path — because durations are randomly sampled, "
                    "different paths can become critical in different runs."
                )
        total = sum(res["path_counts"].values())
        badges = ""
        for lbl, count in sorted(res["path_counts"].items(), key=lambda x: -x[1])[:5]:
            name = next((a["name"] for a in st.session_state.activities if a["label"] == lbl), lbl)
            badges += f'<span class="badge">{lbl} · {name} · {round(count / total * 100, 1)}%</span> '
        st.markdown(badges, unsafe_allow_html=True)
        st.caption("Percentage of simulation runs where this activity was the last to complete.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Network Diagram", use_container_width=True):
        nav(1); st.rerun()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    render_header()
    render_steps()
    {0: page_builder, 1: page_network, 2: page_simulation}[st.session_state.page]()

if __name__ == "__main__":
    main()
