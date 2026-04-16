import io
import re
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict, deque

st.set_page_config(
    page_title="Project Simulator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }

:root {
    --navy:   #1e2a3a;
    --teal:   #0d9488;
    --tealh:  #0f766e;
    --tlight: #f0fdfa;
    --tbord:  #99f6e4;
    --slate:  #64748b;
    --border: #e2e8f0;
    --bg:     #f8fafc;
    --card:   #ffffff;
    --red:    #ef4444;
    --amber:  #f59e0b;
    --green:  #10b981;
}

.stApp { background: var(--bg); }
#MainMenu, footer, header { visibility: hidden; }

/* ── Title ── */
.app-title {
    text-align: center; font-size: 28px; font-weight: 700;
    color: var(--navy); letter-spacing: -0.02em; margin: 8px 0 2px 0;
}
.app-sub {
    text-align: center; font-size: 13px; color: var(--slate); margin-bottom: 20px;
}

/* ── Sidebar activity row ── */
.sb-row {
    display: flex; align-items: center; gap: 8px;
    padding: 9px 12px; background: var(--card);
    border: 1px solid var(--border); border-radius: 7px; margin-bottom: 4px;
}
.sb-lbl {
    font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 500;
    background: var(--navy); color: white;
    width: 26px; height: 26px; border-radius: 5px;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.sb-name  { font-size: 12px; font-weight: 600; color: var(--navy); flex: 1; line-height: 1.3; }
.sb-meta  { font-size: 10px; color: var(--slate); font-family: 'DM Mono', monospace; }
.sb-preds { font-size: 10px; color: var(--teal); font-weight: 500; }

/* ── Edit panel (sidebar) ── */
.edit-panel {
    background: var(--tlight); border: 1px solid var(--tbord);
    border-radius: 8px; padding: 14px 16px; margin: 6px 0 10px 0;
}

/* ── Stat cards ── */
.hero-card {
    background: var(--navy); border-radius: 12px;
    padding: 22px 20px; text-align: center;
}
.hero-val {
    font-size: 42px; font-weight: 700; color: white;
    font-family: 'DM Mono', monospace; line-height: 1;
}
.hero-lbl {
    font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.6);
    text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px;
}
.stat-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px; text-align: center;
}
.stat-val {
    font-size: 26px; font-weight: 700; color: var(--navy);
    font-family: 'DM Mono', monospace; line-height: 1;
}
.stat-lbl {
    font-size: 11px; font-weight: 600; color: var(--slate);
    text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px;
}

/* ── Percentile rows ── */
.pct-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 13px; border-radius: 6px; margin: 3px 0;
    font-size: 13px; font-weight: 600;
}

/* ── Badges ── */
.badge {
    display: inline-block; background: var(--tlight); color: var(--teal);
    font-size: 11px; font-weight: 600; padding: 2px 9px;
    border-radius: 20px; margin: 2px; font-family: 'DM Mono', monospace;
    border: 1px solid var(--tbord);
}
.badge-red {
    display: inline-block; background: #fef2f2; color: #991b1b;
    font-size: 11px; font-weight: 600; padding: 2px 9px;
    border-radius: 20px; margin: 2px; font-family: 'DM Mono', monospace;
    border: 1px solid #fecaca;
}

/* ── Section label ── */
.sec-lbl {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--slate); margin: 14px 0 6px 0;
}

/* ── Alerts ── */
.alert-err  { background:#fef2f2; border:1px solid #fecaca; border-radius:7px; padding:9px 13px; font-size:12px; color:#991b1b; font-weight:500; margin-bottom:5px; }
.alert-warn { background:#fffbeb; border:1px solid #fde68a; border-radius:7px; padding:9px 13px; font-size:12px; color:#92400e; font-weight:500; margin-bottom:5px; }
.alert-ok   { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:7px; padding:9px 13px; font-size:12px; color:#166534; font-weight:500; margin-bottom:5px; }

/* ── Sim control bar ── */
.sim-bar {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px 20px; margin-bottom: 20px;
}

/* ── Risk level chips ── */
.risk-high   { color: #991b1b; font-weight: 700; }
.risk-medium { color: #92400e; font-weight: 700; }
.risk-low    { color: #166534; font-weight: 700; }

hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

/* Buttons */
div.stButton > button {
    border-radius: 6px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 13px !important; transition: all 0.15s !important;
}
div.stButton > button[kind="primary"] {
    background: var(--teal) !important; border-color: var(--teal) !important; color: white !important;
}
div.stButton > button[kind="primary"]:hover {
    background: var(--tealh) !important; border-color: var(--tealh) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input {
    border-radius: 6px !important; font-family: 'DM Mono', monospace !important; font-size: 12px !important;
}
label { font-size: 11px !important; font-weight: 600 !important; color: var(--slate) !important; }
.stMultiSelect [data-baseweb="tag"] { background: var(--tlight) !important; color: var(--teal) !important; }
.stProgress > div > div { background: var(--teal) !important; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
    border-radius: 6px 6px 0 0 !important; font-weight: 600 !important;
    font-size: 13px !important; padding: 8px 18px !important;
}
.stTabs [aria-selected="true"] { color: var(--teal) !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--card) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] .block-container { padding-top: 1rem !important; }
</style>
"""

# ── Session state ─────────────────────────────────────────────────────────────
SESSION_DEFAULTS = {
    "activities":      [],
    "sim_results":     None,
    "edit_idx":        None,
    "panel_open":      False,
    "del_confirm":     None,
    "upload_open":     False,
    "active_tab":      0,
}

def init_state():
    for k, v in SESSION_DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
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
        n = queue.popleft(); order.append(n)
        for nb in adj[n]:
            indegree[nb] -= 1
            if indegree[nb] == 0: queue.append(nb)
    return (order, adj) if len(order) == len(activities) else None

def forward_pass(activities, durations, topo):
    order, _ = topo
    lm = {a["label"]: j for j, a in enumerate(activities)}
    ef = np.zeros(len(activities))
    for i in order:
        preds = [lm[p] for p in activities[i]["predecessors"] if p in lm]
        ef[i] = max((ef[j] for j in preds), default=0.0) + durations[i]
    return ef

def backward_pass(activities, ef, topo):
    order, _ = topo
    lm = {a["label"]: j for j, a in enumerate(activities)}
    n = len(activities)
    project_end = max(ef)
    lf = np.full(n, project_end)
    adj_rev = defaultdict(list)
    for i, a in enumerate(activities):
        for p in a["predecessors"]:
            if p in lm:
                adj_rev[i].append(lm[p])
    for i in reversed(order):
        succs = [j for j in range(n) if i in [lm[p] for p in activities[j]["predecessors"] if p in lm]]
        if succs:
            lf[i] = min(lf[j] - activities[j]["avg_d"] for j in succs)
    return lf

def get_critical_path(activities):
    """Returns list of labels on critical path using te values."""
    topo = topo_sort(activities)
    if not topo: return [], {}
    order, _ = topo
    lm = {a["label"]: i for i, a in enumerate(activities)}
    durations = [te(a) for a in activities]
    ef = forward_pass(activities, durations, topo)
    project_end = max(ef)

    # ES from forward pass
    es = np.zeros(len(activities))
    for i in order:
        preds = [lm[p] for p in activities[i]["predecessors"] if p in lm]
        es[i] = max((ef[j] for j in preds), default=0.0)

    # LS / LF from backward pass
    lf_arr = np.full(len(activities), project_end)
    for i in reversed(order):
        succs = [j for j in range(len(activities))
                 if i in [lm[p] for p in activities[j]["predecessors"] if p in lm]]
        if succs:
            lf_arr[i] = min(es[j] for j in succs)

    ls = lf_arr - np.array(durations)
    total_float = ls - es

    float_map = {activities[i]["label"]: round(total_float[i], 2) for i in range(len(activities))}
    cp_labels = [activities[i]["label"] for i in range(len(activities)) if abs(total_float[i]) < 1e-6]
    return cp_labels, float_map

# ── Validation ────────────────────────────────────────────────────────────────
def validate(activities):
    errors, warnings = [], []
    if not activities:
        errors.append("No activities added yet.")
        return errors, warnings

    labels = [a["label"] for a in activities]
    seen = set()
    for lb in labels:
        if lb in seen: errors.append(f"Duplicate label '{lb}'.")
        seen.add(lb)

    for a in activities:
        lb = a["label"]
        if not is_valid_label(lb):
            errors.append(f"Label '{lb}': letters and numbers only.")
        if lb in a["predecessors"]:
            errors.append(f"Activity '{lb}' lists itself as a predecessor.")
        for p in a["predecessors"]:
            if p not in labels:
                errors.append(f"Activity '{lb}': unknown predecessor '{p}'.")
        if a["min_d"] > a["avg_d"] or a["avg_d"] > a["max_d"]:
            errors.append(f"Activity '{lb}': min ≤ most likely ≤ max required.")
        if a["min_d"] == a["avg_d"] == a["max_d"] == 0:
            warnings.append(f"Activity '{lb}': all durations are zero.")
        if a["min_d"] == a["avg_d"] == a["max_d"] and a["min_d"] > 0:
            warnings.append(f"Activity '{lb}': no uncertainty (min = likely = max).")
        if a["max_d"] > 5200:
            warnings.append(f"Activity '{lb}': max duration {a['max_d']} seems very large.")
        if not a["name"].strip():
            errors.append(f"Activity '{lb}': name cannot be blank.")

    if not errors:
        if not any(len(a["predecessors"]) == 0 for a in activities):
            errors.append("No start activity — at least one activity must have no predecessors.")
        all_preds = set(p for a in activities for p in a["predecessors"])
        if not any(a["label"] not in all_preds for a in activities):
            errors.append("No end activity — at least one activity must have no successors.")
        if topo_sort(activities) is None:
            errors.append("Circular dependency detected.")
        # Disconnected graph
        if len(activities) > 1 and topo_sort(activities):
            lm = {a["label"]: i for i, a in enumerate(activities)}
            adj_fwd = defaultdict(list)
            for i, a in enumerate(activities):
                for p in a["predecessors"]:
                    if p in lm: adj_fwd[lm[p]].append(i)
            starts = [i for i, a in enumerate(activities) if not a["predecessors"]]
            visited = set()
            q = deque(starts)
            while q:
                n = q.popleft()
                if n in visited: continue
                visited.add(n)
                for nb in adj_fwd[n]: q.append(nb)
            if len(visited) < len(activities):
                unreachable = [activities[i]["label"] for i in range(len(activities)) if i not in visited]
                warnings.append(f"Activities {unreachable} appear disconnected from the main graph.")
        # Duplicate names
        names = [a["name"].strip().lower() for a in activities]
        name_seen = set()
        for nm in names:
            if nm in name_seen: warnings.append(f"Duplicate activity name '{nm}'.")
            name_seen.add(nm)
    return errors, warnings

# ── Distribution sampling ─────────────────────────────────────────────────────
def sample_duration(a, dist_type):
    lo, mi, hi = a["min_d"], a["avg_d"], a["max_d"]
    if dist_type == "Uniform":
        return np.random.uniform(lo, hi)
    elif dist_type == "PERT Beta":
        mu = (lo + 4 * mi + hi) / 6
        sigma = (hi - lo) / 6
        if sigma < 1e-9: return mu
        mn = np.clip((mu - lo) / (hi - lo + 1e-9), 0.01, 0.99)
        vn = min((sigma / (hi - lo + 1e-9)) ** 2, mn * (1 - mn) * 0.999)
        al = max(mn * (mn * (1 - mn) / vn - 1), 0.1)
        be = max((1 - mn) * (mn * (1 - mn) / vn - 1), 0.1)
        return np.random.beta(al, be) * (hi - lo) + lo
    elif dist_type == "Triangular":
        return np.random.triangular(lo, mi, hi)
    elif dist_type == "Normal":
        mu = (lo + 4 * mi + hi) / 6
        sigma = (hi - lo) / 6
        return max(lo, np.random.normal(mu, sigma))
    elif dist_type == "Log-normal":
        mu = (lo + 4 * mi + hi) / 6
        sigma = (hi - lo) / 6
        if sigma < 1e-9: return mu
        var = sigma ** 2
        mu_ln = np.log(mu ** 2 / np.sqrt(var + mu ** 2))
        sigma_ln = np.sqrt(np.log(1 + var / mu ** 2))
        return max(lo, np.random.lognormal(mu_ln, sigma_ln))
    return mi

# ── Monte Carlo ───────────────────────────────────────────────────────────────
def monte_carlo(activities, n_sim, dist_type, progress_cb=None):
    topo = topo_sort(activities)
    if not topo: return None
    n = len(activities)
    finish_times = np.zeros(n_sim)
    path_counts = defaultdict(int)
    # Per-activity duration storage for sensitivity
    act_durations = [[] for _ in range(n)]

    for s in range(n_sim):
        if progress_cb and s % 500 == 0: progress_cb(s / n_sim)
        durations = [sample_duration(a, dist_type) for a in activities]
        for i, d in enumerate(durations): act_durations[i].append(d)
        ef = forward_pass(activities, durations, topo)
        finish_times[s] = max(ef)
        path_counts[activities[int(np.argmax(ef))]["label"]] += 1

    # Sensitivity: correlation of each activity duration with project finish
    sensitivity = {}
    for i, a in enumerate(activities):
        d_arr = np.array(act_durations[i])
        if d_arr.std() > 1e-9:
            corr = np.corrcoef(d_arr, finish_times)[0, 1]
        else:
            corr = 0.0
        sensitivity[a["label"]] = round(float(corr), 3)

    return {
        "finish_times":  finish_times,
        "path_counts":   dict(path_counts),
        "sensitivity":   sensitivity,
        "n_sim":         n_sim,
        "dist_type":     dist_type,
    }

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

def parse_csv(content, existing_labels):
    try:
        df = pd.read_csv(io.StringIO(content))
    except Exception as e:
        return [], [f"Could not parse CSV: {e}"]
    df.columns = [c.strip().lower() for c in df.columns]
    required = {"name", "label", "min_duration", "avg_duration", "max_duration"}
    missing = required - set(df.columns)
    if missing: return [], [f"Missing columns: {', '.join(missing)}"]

    rows = []; file_labels = set(); row_errors = []
    for idx, row in df.iterrows():
        line = idx + 2; errs = []
        name    = str(row.get("name", "")).strip()
        label   = str(row.get("label", "")).strip().upper()
        preds_r = str(row.get("predecessors", "")).strip()
        preds   = [p.strip().upper() for p in preds_r.split(",") if p.strip()] \
                  if preds_r and preds_r.lower() != "nan" else []
        try:
            min_d = float(row["min_duration"])
            avg_d = float(row["avg_duration"])
            max_d = float(row["max_duration"])
        except Exception:
            errs.append("Non-numeric duration."); min_d = avg_d = max_d = 0.0

        if not name:                          errs.append("Name is blank.")
        if not label:                         errs.append("Label is blank.")
        elif not is_valid_label(label):       errs.append(f"Label '{label}': invalid characters.")
        elif label in file_labels:            errs.append(f"Label '{label}' duplicated in file.")
        elif label in existing_labels:        errs.append(f"Label '{label}' already in project.")
        if label in preds:                    errs.append("Self-reference in predecessors.")
        if min_d > avg_d or avg_d > max_d:   errs.append("min ≤ most likely ≤ max required.")
        if min_d < 0:                         errs.append("Negative duration.")
        file_labels.add(label)
        rows.append({"line": line,
                     "activity": {"name": name, "label": label, "predecessors": preds,
                                  "min_d": min_d, "avg_d": avg_d, "max_d": max_d},
                     "errors": errs})

    all_labels = set(existing_labels) | {r["activity"]["label"] for r in rows if not r["errors"]}
    for r in rows:
        for p in r["activity"]["predecessors"]:
            if p not in all_labels:
                r["errors"].append(f"Unknown predecessor '{p}'.")

    if not any(r["errors"] for r in rows):
        merged = [r["activity"] for r in rows]
        if topo_sort(merged) is None:
            row_errors.append("Circular dependency within uploaded file.")
    return rows, row_errors

# ── Network diagram ───────────────────────────────────────────────────────────
def draw_network(activities, highlight_cp=True):
    topo = topo_sort(activities)
    if not topo: return None
    order, _ = topo
    lm = {a["label"]: i for i, a in enumerate(activities)}
    cp_labels, _ = get_critical_path(activities) if highlight_cp else ([], {})

    levels = [0] * len(activities)
    for idx in order:
        preds = [lm[p] for p in activities[idx]["predecessors"] if p in lm]
        if preds: levels[idx] = max(levels[p] for p in preds) + 1
    max_lv = max(levels) if levels else 0
    lv_count = defaultdict(int); lv_pos = defaultdict(int)
    for i in order: lv_count[levels[i]] += 1
    xp = [0.0] * len(activities); yp = [0.0] * len(activities)
    for i in order:
        lv = levels[i]
        xp[i] = lv / max(max_lv, 1)
        yp[i] = (lv_pos[lv] + 0.5) / lv_count[lv]; lv_pos[lv] += 1

    fig = go.Figure()
    for i, a in enumerate(activities):
        for p in a["predecessors"]:
            if p in lm:
                j = lm[p]; dx, dy = xp[i] - xp[j], yp[i] - yp[j]
                is_cp_edge = a["label"] in cp_labels and p in cp_labels
                fig.add_trace(go.Scatter(
                    x=[xp[j], xp[i]], y=[yp[j], yp[i]], mode="lines",
                    line=dict(color="#ef4444" if is_cp_edge else "#e2e8f0",
                              width=2.5 if is_cp_edge else 1.5),
                    showlegend=False, hoverinfo="skip",
                ))
                fig.add_annotation(
                    ax=xp[j]+0.72*dx, ay=yp[j]+0.72*dy,
                    x=xp[j]+0.82*dx,  y=yp[j]+0.82*dy,
                    xref="x", yref="y", axref="x", ayref="y",
                    showarrow=True, arrowhead=2, arrowsize=1.3, arrowwidth=2,
                    arrowcolor="#ef4444" if is_cp_edge else "#94a3b8",
                )

    for i, a in enumerate(activities):
        _te = te(a)
        var = round(((a["max_d"] - a["min_d"]) / 6) ** 2, 2)
        on_cp = a["label"] in cp_labels
        node_color = "#ef4444" if on_cp else "#1e2a3a"
        fig.add_trace(go.Scatter(
            x=[xp[i]], y=[yp[i]], mode="markers+text",
            marker=dict(size=52, color=node_color, line=dict(color="white", width=3)),
            text=[f"<b>{a['label']}</b>"],
            textposition="middle center",
            textfont=dict(size=13, color="white", family="DM Mono"),
            hovertemplate=(
                f"<b>{a['name']}</b><br>"
                f"Range: {a['min_d']} / {a['avg_d']} / {a['max_d']}<br>"
                f"Expected (te): <b>{_te}</b><br>Variance: {var}<br>"
                f"On critical path: {'Yes' if on_cp else 'No'}<br>"
                f"Predecessors: {', '.join(a['predecessors']) or 'None'}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))
        fig.add_annotation(
            x=xp[i], y=yp[i] - 0.1,
            text=f"<b>{a['name']}</b><br><span style='color:#64748b;font-size:10px;font-family:DM Mono'>te={_te}</span>",
            showarrow=False, font=dict(size=10, family="DM Sans", color="#1e2a3a"),
            bgcolor="rgba(255,255,255,0.92)", borderpad=3,
        )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=10, b=20), height=380,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.18, 1.18]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.25, 1.25]),
    )
    return fig


# ── Edit / Add form ───────────────────────────────────────────────────────────
def render_edit_panel(prefill=None, exclude_label=None):
    is_edit = prefill is not None
    st.markdown(f"**{'Edit' if is_edit else 'New Activity'}**")
    c1, c2 = st.columns([3, 1])
    with c1:
        name = st.text_input("Name", value=prefill["name"] if prefill else "",
                             placeholder="e.g. Design prototype", key="ep_name")
    with c2:
        label = st.text_input("Label", value=prefill["label"] if prefill else "",
                              placeholder="A", max_chars=6, key="ep_label",
                              help="Unique ID — letters/numbers only.").upper().strip()

    existing = [a["label"] for a in st.session_state.activities if a["label"] != exclude_label]
    preds = st.multiselect("Predecessors", options=existing,
                           default=[p for p in (prefill["predecessors"] if prefill else []) if p in existing],
                           key="ep_preds",
                           help="Activities that must finish before this one starts.")

    c1, c2, c3 = st.columns(3)
    with c1: min_d = st.number_input("Min", min_value=0.0, value=float(prefill["min_d"]) if prefill else 1.0, step=0.5, key="ep_min", help="Best-case duration.")
    with c2: avg_d = st.number_input("Most Likely", min_value=0.0, value=float(prefill["avg_d"]) if prefill else 3.0, step=0.5, key="ep_avg", help="Expected duration under normal conditions.")
    with c3: max_d = st.number_input("Max", min_value=0.0, value=float(prefill["max_d"]) if prefill else 5.0, step=0.5, key="ep_max", help="Worst-case duration.")

    errs = []
    if not name.strip(): errs.append("Name required.")
    if not label: errs.append("Label required.")
    elif not is_valid_label(label): errs.append("Letters/numbers only.")
    elif label != exclude_label and label in [a["label"] for a in st.session_state.activities if a["label"] != exclude_label]:
        errs.append(f"Label '{label}' in use.")
    if label and label in preds: errs.append("Cannot be its own predecessor.")
    if min_d > avg_d or avg_d > max_d: errs.append("min ≤ likely ≤ max.")

    b1, b2 = st.columns(2)
    with b1:
        save = st.button("Save", type="primary", key="ep_save", use_container_width=True)
    with b2:
        if st.button("Cancel", key="ep_cancel", use_container_width=True):
            st.session_state.panel_open = False
            st.session_state.edit_idx = None
            st.rerun()
    if save:
        if errs:
            for e in errs: st.error(e)
        else:
            return True, {"name": name.strip(), "label": label, "predecessors": preds,
                          "min_d": min_d, "avg_d": avg_d, "max_d": max_d}
    return False, None


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### 📋 Activities")
        acts = st.session_state.activities
        errs, warns = validate(acts) if acts else ([], [])

        # Validation alerts
        for e in errs:
            st.markdown(f'<div class="alert-err">✕ {e}</div>', unsafe_allow_html=True)
        for w in warns:
            st.markdown(f'<div class="alert-warn">⚠ {w}</div>', unsafe_allow_html=True)
        if acts and not errs:
            st.markdown('<div class="alert-ok">✓ Project structure valid</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Activity list
        if acts:
            for i, a in enumerate(acts):
                preds_str = "→ ".join(a["predecessors"]) + f"→{a['label']}" if a["predecessors"] else f"{a['label']} (start)"
                ci, cu, cd2, ce, cdel = st.columns([4, 0.6, 0.6, 1, 1])
                with ci:
                    st.markdown(f"""
                    <div class="sb-row">
                        <div class="sb-lbl">{a['label']}</div>
                        <div>
                            <div class="sb-name">{a['name']}</div>
                            <div class="sb-meta">{a['min_d']}/{a['avg_d']}/{a['max_d']} · te={te(a)}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with cu:
                    if i > 0 and st.button("↑", key=f"up_{i}", use_container_width=True):
                        st.session_state.activities[i-1], st.session_state.activities[i] = \
                            st.session_state.activities[i], st.session_state.activities[i-1]
                        st.session_state.sim_results = None; st.rerun()
                with cd2:
                    if i < len(acts)-1 and st.button("↓", key=f"dn_{i}", use_container_width=True):
                        st.session_state.activities[i+1], st.session_state.activities[i] = \
                            st.session_state.activities[i], st.session_state.activities[i+1]
                        st.session_state.sim_results = None; st.rerun()
                with ce:
                    if st.button("Edit", key=f"edit_{i}", use_container_width=True):
                        st.session_state.edit_idx = i
                        st.session_state.panel_open = True
                        st.session_state.del_confirm = None; st.rerun()
                with cdel:
                    if st.session_state.del_confirm == i:
                        if st.button("OK?", key=f"delok_{i}", use_container_width=True, type="primary"):
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
                        if st.button("Del", key=f"del_{i}", use_container_width=True):
                            st.session_state.del_confirm = i; st.rerun()

                # Inline edit panel
                if st.session_state.edit_idx == i and st.session_state.panel_open:
                    st.markdown('<div class="edit-panel">', unsafe_allow_html=True)
                    saved, new_act = render_edit_panel(prefill=a, exclude_label=a["label"])
                    st.markdown('</div>', unsafe_allow_html=True)
                    if saved and new_act:
                        st.session_state.activities[i] = new_act
                        st.session_state.panel_open = False
                        st.session_state.edit_idx = None
                        st.session_state.sim_results = None; st.rerun()
        else:
            st.markdown('<div style="text-align:center;padding:24px 0;color:#94a3b8;font-size:13px">No activities yet</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Add / toolbar
        add_open = st.session_state.panel_open and st.session_state.edit_idx is None
        t1, t2 = st.columns(2)
        with t1:
            if st.button("Close" if add_open else "+ Add", type="secondary" if add_open else "primary",
                         use_container_width=True, key="btn_add"):
                st.session_state.panel_open = not add_open
                st.session_state.edit_idx = None
                st.session_state.del_confirm = None; st.rerun()
        with t2:
            if st.button("Clear All", use_container_width=True):
                st.session_state.activities = []
                st.session_state.sim_results = None
                st.session_state.panel_open = False
                st.session_state.edit_idx = None; st.rerun()

        if add_open:
            st.markdown('<div class="edit-panel" style="margin-top:8px">', unsafe_allow_html=True)
            saved, new_act = render_edit_panel()
            st.markdown('</div>', unsafe_allow_html=True)
            if saved and new_act:
                st.session_state.activities.append(new_act)
                st.session_state.panel_open = False
                st.session_state.sim_results = None; st.rerun()

        if st.button("Load Example Project", use_container_width=True,
                     help="Load the Computer Design PERT example."):
            st.session_state.activities = [
                {"name":"Design","label":"A","predecessors":[],"min_d":16,"avg_d":21,"max_d":26},
                {"name":"Build Prototype","label":"B","predecessors":["A"],"min_d":3,"avg_d":6,"max_d":9},
                {"name":"Evaluate Equipment","label":"C","predecessors":["A"],"min_d":5,"avg_d":7,"max_d":9},
                {"name":"Test Prototype","label":"D","predecessors":["B"],"min_d":2,"avg_d":3,"max_d":4},
                {"name":"Write Equipment Report","label":"E","predecessors":["C","D"],"min_d":4,"avg_d":6,"max_d":8},
                {"name":"Write Methods Report","label":"F","predecessors":["C","D"],"min_d":6,"avg_d":8,"max_d":10},
                {"name":"Write Final Report","label":"G","predecessors":["E","F"],"min_d":1,"avg_d":2,"max_d":3},
            ]
            st.session_state.sim_results = None
            st.session_state.panel_open = False
            st.session_state.edit_idx = None; st.rerun()

        # CSV import
        st.markdown("<hr>", unsafe_allow_html=True)
        with st.expander("📂 CSV Import / Export"):
            st.download_button("⬇ Download Template", data=CSV_TEMPLATE,
                               file_name="project_template.csv", mime="text/csv",
                               use_container_width=True)
            uploaded = st.file_uploader("Upload CSV", type=["csv"], key="csv_up")
            if uploaded:
                content = uploaded.read().decode("utf-8")
                existing = [a["label"] for a in st.session_state.activities]
                rows, ferrs = parse_csv(content, existing)
                if ferrs:
                    for e in ferrs: st.error(e)
                else:
                    has_errs = any(r["errors"] for r in rows)
                    prev = [{"Label": r["activity"]["label"],
                             "Name": r["activity"]["name"],
                             "Status": "✕ " + "; ".join(r["errors"]) if r["errors"] else "✓"
                             } for r in rows]
                    st.dataframe(pd.DataFrame(prev), use_container_width=True, hide_index=True)
                    if has_errs:
                        st.error("Fix errors before importing.")
                    else:
                        mode = st.radio("Mode", ["Append", "Replace"], horizontal=True)
                        clean = [r["activity"] for r in rows]
                        if st.button(f"Import {len(clean)}", type="primary", use_container_width=True):
                            if mode == "Replace":
                                st.session_state.activities = clean
                            else:
                                st.session_state.activities.extend(clean)
                            st.session_state.sim_results = None; st.rerun()

# ── Result tabs ───────────────────────────────────────────────────────────────

def tab_summary(res, activities):
    ft = res["finish_times"]
    mean_ft = float(np.mean(ft)); std_ft = float(np.std(ft))
    p50  = float(np.percentile(ft, 50))
    p75  = float(np.percentile(ft, 75))
    p80  = float(np.percentile(ft, 80))
    p90  = float(np.percentile(ft, 90))
    p95  = float(np.percentile(ft, 95))

    # Hero stat + supporting stats
    hc1, hc2, hc3, hc4 = st.columns([2, 1, 1, 1])
    with hc1:
        st.markdown(f"""
        <div class="hero-card">
            <div class="hero-val">{p90:.1f}</div>
            <div class="hero-lbl">P90 — 90% Confidence Deadline</div>
        </div>
        """, unsafe_allow_html=True)
    for col, val, lbl in [
        (hc2, f"{mean_ft:.1f}", "Expected Finish"),
        (hc3, f"± {std_ft:.1f}", "Std. Deviation"),
        (hc4, f"{min(ft):.1f} – {max(ft):.1f}", "Observed Range"),
    ]:
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-val">{val}</div><div class="stat-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_hist, col_pct = st.columns([3, 2])

    with col_hist:
        st.markdown('<div class="sec-lbl">Completion Time Distribution</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=ft, nbinsx=60,
            marker=dict(color="#0d9488", opacity=0.75, line=dict(color="white", width=0.4)),
            hovertemplate="Finish: %{x:.1f}<br>Count: %{y}<extra></extra>"))
        for v, lb, col in [(mean_ft,"Mean","#1e2a3a"),(p50,"P50","#10b981"),(p90,"P90","#ef4444")]:
            fig.add_vline(x=v, line=dict(color=col, width=1.5, dash="dash"),
                          annotation_text=f" {lb}={v:.1f}",
                          annotation_font=dict(color=col, size=11, family="DM Mono"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10,r=10,t=10,b=30), height=260,
            xaxis=dict(title="Completion Time", showgrid=False, tickfont=dict(family="DM Mono",size=11)),
            yaxis=dict(title="Frequency", showgrid=True, gridcolor="#f1f5f9", tickfont=dict(family="DM Mono",size=11)),
            showlegend=False, bargap=0.04, font=dict(family="DM Sans"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_pct:
        st.markdown('<div class="sec-lbl">Confidence Intervals</div>', unsafe_allow_html=True)
        st.caption("Probability of completing by the stated time.")
        for lbl, val, bg, fg in [
            ("P50 — 50%", p50, "#f0fdf4", "#166534"),
            ("P75 — 75%", p75, "#fefce8", "#854d0e"),
            ("P80 — 80%", p80, "#fff7ed", "#9a3412"),
            ("P90 — 90%", p90, "#fef2f2", "#991b1b"),
            ("P95 — 95%", p95, "#fdf4ff", "#6b21a8"),
        ]:
            st.markdown(f"""
            <div class="pct-row" style="background:{bg};color:{fg}">
                <span>{lbl}</span>
                <span style="font-family:'DM Mono',monospace;font-size:16px">{val:.1f}</span>
            </div>""", unsafe_allow_html=True)

    # S-curve
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-lbl">S-Curve — Cumulative Completion Probability</div>', unsafe_allow_html=True)
    st.caption("Drag your target deadline to read off the probability of finishing in time.")
    sorted_ft = np.sort(ft)
    cum_pct = np.arange(1, len(sorted_ft)+1) / len(sorted_ft) * 100
    fig_s = go.Figure()
    fig_s.add_trace(go.Scatter(x=sorted_ft, y=cum_pct, mode="lines",
        line=dict(color="#0d9488", width=2.5),
        hovertemplate="By time %{x:.1f}: %{y:.1f}% probability<extra></extra>"))
    fig_s.add_hline(y=90, line=dict(color="#ef4444", width=1, dash="dot"),
                    annotation_text=" 90%", annotation_font=dict(color="#ef4444", size=11))
    fig_s.add_hline(y=50, line=dict(color="#10b981", width=1, dash="dot"),
                    annotation_text=" 50%", annotation_font=dict(color="#10b981", size=11))
    fig_s.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=10,b=30), height=240,
        xaxis=dict(title="Completion Time", showgrid=False, tickfont=dict(family="DM Mono",size=11)),
        yaxis=dict(title="Cumulative %", showgrid=True, gridcolor="#f1f5f9",
                   tickfont=dict(family="DM Mono",size=11), range=[0,101]),
        font=dict(family="DM Sans"))
    st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar": False})


def tab_critical_path(activities):
    cp_labels, float_map = get_critical_path(activities)
    if not cp_labels:
        st.info("Run simulation first or check for project errors.")
        return

    st.markdown('<div class="sec-lbl">Critical Path</div>', unsafe_allow_html=True)
    cp_names = [f"{lb} ({next(a['name'] for a in activities if a['label']==lb)})" for lb in cp_labels]
    st.markdown(" → ".join([f'<span class="badge-red">{n}</span>' for n in cp_names]), unsafe_allow_html=True)

    cp_duration = sum(te(a) for a in activities if a["label"] in cp_labels)
    st.markdown(f"<br>**Total critical path duration (te): {cp_duration:.1f} units**", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-lbl">Float Analysis — All Activities</div>', unsafe_allow_html=True)
    with st.expander("What is float?"):
        st.markdown("**Total float** is how long an activity can be delayed without delaying the project end date. "
                    "Activities with zero float are on the critical path and have no scheduling slack.")

    rows = []
    for a in activities:
        fl = float_map.get(a["label"], 0.0)
        rows.append({
            "Label": a["label"], "Name": a["name"],
            "Expected (te)": te(a),
            "Total Float": fl,
            "On Critical Path": "Yes" if a["label"] in cp_labels else "No",
            "Risk": "🔴 Critical" if a["label"] in cp_labels else ("🟡 Watch" if fl < 3 else "🟢 OK"),
        })
    df = pd.DataFrame(rows).sort_values("Total Float")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Float bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[r["Label"] for r in rows],
        y=[r["Total Float"] for r in rows],
        marker_color=["#ef4444" if r["On Critical Path"]=="Yes" else "#0d9488" for r in rows],
        hovertemplate="%{x}: float = %{y:.1f}<extra></extra>",
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=10,b=30), height=220,
        xaxis=dict(title="Activity", tickfont=dict(family="DM Mono",size=11)),
        yaxis=dict(title="Total Float", showgrid=True, gridcolor="#f1f5f9",
                   tickfont=dict(family="DM Mono",size=11)),
        showlegend=False, font=dict(family="DM Sans"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def tab_gantt(activities):
    topo = topo_sort(activities)
    if not topo:
        st.error("Fix project errors before viewing Gantt chart.")
        return
    order, _ = topo
    lm = {a["label"]: i for i, a in enumerate(activities)}
    durations = [te(a) for a in activities]
    ef = forward_pass(activities, durations, topo)
    es = np.zeros(len(activities))
    for i in order:
        preds = [lm[p] for p in activities[i]["predecessors"] if p in lm]
        es[i] = max((ef[j] for j in preds), default=0.0)

    cp_labels, _ = get_critical_path(activities)

    st.markdown('<div class="sec-lbl">Gantt Chart — Expected Timeline (using PERT te values)</div>', unsafe_allow_html=True)
    fig = go.Figure()
    for i, a in enumerate(activities):
        on_cp = a["label"] in cp_labels
        fig.add_trace(go.Bar(
            x=[durations[i]], y=[f"{a['label']}: {a['name']}"],
            base=[es[i]], orientation="h",
            marker=dict(color="#ef4444" if on_cp else "#0d9488", opacity=0.85,
                        line=dict(color="white", width=1)),
            hovertemplate=(
                f"<b>{a['name']}</b><br>"
                f"Start: {es[i]:.1f}  Finish: {ef[i]:.1f}<br>"
                f"Duration (te): {durations[i]:.1f}<br>"
                f"Critical path: {'Yes' if on_cp else 'No'}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=10,b=30), height=max(280, len(activities)*44),
        xaxis=dict(title="Time", showgrid=True, gridcolor="#f1f5f9", tickfont=dict(family="DM Mono",size=11)),
        yaxis=dict(autorange="reversed", tickfont=dict(family="DM Sans",size=12)),
        barmode="overlay", font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("🔴 Red = critical path activity. Hover for details.")


def tab_risk(res, activities):
    ft = res["finish_times"]
    sensitivity = res.get("sensitivity", {})
    n_sim = res["n_sim"]

    # ── Tornado chart ─────────────────────────────────────────────────────────
    st.markdown('<div class="sec-lbl">Sensitivity Analysis — Tornado Chart</div>', unsafe_allow_html=True)
    with st.expander("How to read this chart"):
        st.markdown("Shows the Spearman rank correlation between each activity's sampled duration and the "
                    "overall project finish time. A bar closer to 1.0 means that activity has the most "
                    "influence on whether the project finishes early or late.")

    if sensitivity:
        sorted_sens = sorted(sensitivity.items(), key=lambda x: abs(x[1]), reverse=True)
        labels_s = [f"{lb} · {next((a['name'] for a in activities if a['label']==lb), lb)}"
                    for lb, _ in sorted_sens]
        values_s = [v for _, v in sorted_sens]
        colors_s = ["#ef4444" if v >= 0.3 else "#f59e0b" if v >= 0.1 else "#0d9488" for v in values_s]

        fig = go.Figure(go.Bar(
            x=values_s, y=labels_s, orientation="h",
            marker_color=colors_s,
            hovertemplate="%{y}: correlation = %{x:.3f}<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10,r=10,t=10,b=10), height=max(240, len(activities)*36),
            xaxis=dict(title="Correlation with Project Finish Time", range=[-0.05, 1.0],
                       tickfont=dict(family="DM Mono",size=11), showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(autorange="reversed", tickfont=dict(family="DM Sans",size=12)),
            showlegend=False, font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Risk Register ─────────────────────────────────────────────────────────
    st.markdown('<div class="sec-lbl">Risk Register</div>', unsafe_allow_html=True)
    with st.expander("How is risk score calculated?"):
        st.markdown("**Probability**: % of simulation runs where this activity exceeded its most likely duration.\n\n"
                    "**Impact**: Average overrun when it did exceed most likely (in time units).\n\n"
                    "**Risk Score**: Probability × Impact — higher = greater scheduling risk.")

    topo = topo_sort(activities)
    if not topo:
        st.error("Fix project errors.")
        return

    risk_rows = []
    for a in activities:
        corr = sensitivity.get(a["label"], 0.0)
        prob_exceed = round(np.mean(np.array(ft) > (a["avg_d"] + a["min_d"]) / 2) * 100, 1)
        duration_spread = a["max_d"] - a["min_d"]
        impact = round(duration_spread * corr, 2)
        risk_score = round(prob_exceed / 100 * abs(impact), 2)
        level = "🔴 High" if risk_score > 2 else ("🟡 Medium" if risk_score > 0.5 else "🟢 Low")
        risk_rows.append({
            "Label": a["label"],
            "Activity": a["name"],
            "Duration Spread": f"{duration_spread:.1f}",
            "Sensitivity": f"{corr:.2f}",
            "Prob. Exceed Likely (%)": prob_exceed,
            "Est. Impact": f"{impact:.2f}",
            "Risk Score": risk_score,
            "Level": level,
        })

    risk_df = pd.DataFrame(risk_rows).sort_values("Risk Score", ascending=False)
    st.dataframe(risk_df, use_container_width=True, hide_index=True)

    # ── Schedule buffer recommendation ────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="sec-lbl">Schedule Buffer Recommendation</div>', unsafe_allow_html=True)
    p50 = float(np.percentile(ft, 50))
    p90 = float(np.percentile(ft, 90))
    buffer = round(p90 - p50, 1)
    pct_buffer = round(buffer / p50 * 100, 1)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-val">{p50:.1f}</div><div class="stat-lbl">P50 Estimate</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-val">{buffer:.1f}</div><div class="stat-lbl">Recommended Buffer</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-val">{pct_buffer}%</div><div class="stat-lbl">Buffer as % of P50</div></div>', unsafe_allow_html=True)
    st.caption(f"Adding {buffer:.1f} units of schedule buffer to the P50 estimate gives you a 90% confidence deadline of {p90:.1f}.")


def tab_bottleneck(res, activities):
    path_counts = res["path_counts"]
    total = sum(path_counts.values())
    if not path_counts:
        st.info("No bottleneck data available.")
        return

    st.markdown('<div class="sec-lbl">Bottleneck Frequency — % of Runs Each Activity Finished Last</div>', unsafe_allow_html=True)
    with st.expander("What does this mean?"):
        st.markdown("In each simulation run, one activity is the last to complete and determines the project end date. "
                    "This chart shows how often each activity held that position. "
                    "Activities appearing frequently are your true scheduling risk — even if they are not always on the deterministic critical path.")

    sorted_counts = sorted(path_counts.items(), key=lambda x: -x[1])
    labels_b = [f"{lb} · {next((a['name'] for a in activities if a['label']==lb), lb)}" for lb, _ in sorted_counts]
    values_b = [round(c / total * 100, 1) for _, c in sorted_counts]
    colors_b = ["#ef4444" if v > 30 else "#f59e0b" if v > 10 else "#0d9488" for v in values_b]

    fig = go.Figure(go.Bar(
        x=values_b, y=labels_b, orientation="h",
        marker_color=colors_b,
        hovertemplate="%{y}: %{x:.1f}% of runs<extra></extra>",
        text=[f"{v:.1f}%" for v in values_b],
        textposition="outside",
        textfont=dict(family="DM Mono", size=11),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=60,t=10,b=30), height=max(240, len(path_counts)*44),
        xaxis=dict(title="% of Simulation Runs", tickfont=dict(family="DM Mono",size=11),
                   showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(autorange="reversed", tickfont=dict(family="DM Sans",size=12)),
        showlegend=False, font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Comparison: deterministic CP vs simulation bottleneck
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="sec-lbl">Deterministic vs Simulation Critical Path</div>', unsafe_allow_html=True)
    st.caption("Differences between the two highlight activities whose uncertainty can shift which path becomes critical.")

    cp_labels, _ = get_critical_path(activities)
    top_sim = [lb for lb, _ in sorted_counts[:3]]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Deterministic Critical Path (PERT te)**")
        for lb in cp_labels:
            name = next((a["name"] for a in activities if a["label"] == lb), lb)
            st.markdown(f'<span class="badge-red">{lb} · {name}</span>', unsafe_allow_html=True)
    with c2:
        st.markdown("**Top Bottlenecks in Simulation**")
        for lb in top_sim:
            name = next((a["name"] for a in activities if a["label"] == lb), lb)
            pct = round(path_counts.get(lb, 0) / total * 100, 1)
            cls = "badge-red" if lb not in cp_labels else "badge"
            st.markdown(f'<span class="{cls}">{lb} · {name} · {pct}%</span>', unsafe_allow_html=True)
    if any(lb not in cp_labels for lb in top_sim):
        st.markdown('<div class="alert-warn" style="margin-top:10px">⚠ Some simulation bottlenecks are not on the deterministic critical path. Their duration uncertainty makes them latent risks worth monitoring.</div>', unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    init_state()
    st.markdown(CSS, unsafe_allow_html=True)
    render_sidebar()

    # Title
    st.markdown('<div class="app-title">📊 Project Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">PERT estimation · Monte Carlo simulation · Schedule risk analysis</div>', unsafe_allow_html=True)

    acts = st.session_state.activities
    errs, warns = validate(acts) if acts else (["No activities"], [])

    # Network diagram (always visible)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="sec-lbl">Network Diagram</div>', unsafe_allow_html=True)
    if acts and not errs:
        fig_net = draw_network(acts, highlight_cp=True)
        if fig_net:
            st.plotly_chart(fig_net, use_container_width=True, config={"displayModeBar": False})
        st.caption("🔴 Red nodes and edges = critical path (PERT te). Hover over nodes for details.")
    else:
        st.markdown('<div style="text-align:center;padding:40px;color:#94a3b8;border:1px dashed #e2e8f0;border-radius:10px;font-size:13px;">Add activities in the sidebar to see the network diagram.</div>', unsafe_allow_html=True)

    # Simulation controls
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="sim-bar">', unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns([2, 2, 1])
    with sc1:
        n_sim = st.select_slider("Iterations",
            options=[500, 1000, 5000, 10000, 25000, 50000], value=10000,
            help="More iterations = more accurate results. 10,000 is a reliable default.")
    with sc2:
        dist = st.selectbox("Duration Distribution",
            ["Uniform", "PERT Beta", "Triangular", "Normal", "Log-normal"],
            index=0,
            help=(
                "**Uniform**: Equal probability across the full min–max range. Simple and conservative.\n\n"
                "**PERT Beta**: Weights the most likely estimate 4× more than extremes. Best for project estimation.\n\n"
                "**Triangular**: Equal weight on min, likely, max. Simple but less precise than PERT.\n\n"
                "**Normal**: Symmetric bell curve centred on the most likely value.\n\n"
                "**Log-normal**: Right-skewed — models tasks that occasionally run very long."
            ))
    with sc3:
        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("▶ Run Simulation", type="primary", use_container_width=True,
                        disabled=bool(errs))
    st.markdown('</div>', unsafe_allow_html=True)

    if run and not errs:
        bar = st.progress(0, text="Running simulation...")
        results = monte_carlo(acts, n_sim, dist,
                              progress_cb=lambda p: bar.progress(p, text=f"Running... {int(p*100)}%"))
        bar.progress(1.0, text="Complete.")
        st.session_state.sim_results = results
        st.rerun()

    # Results tabs (only after simulation)
    if st.session_state.sim_results and not errs:
        res = st.session_state.sim_results
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="alert-ok">✓ {res["n_sim"]:,} iterations complete · Distribution: {res["dist_type"]}</div>',
            unsafe_allow_html=True,
        )

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Summary",
            "🔗 Critical Path",
            "📅 Gantt Chart",
            "⚠ Risk Analysis",
            "🔍 Bottleneck",
        ])
        with tab1: tab_summary(res, acts)
        with tab2: tab_critical_path(acts)
        with tab3: tab_gantt(acts)
        with tab4: tab_risk(res, acts)
        with tab5: tab_bottleneck(res, acts)

    elif errs and acts:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;padding:40px;color:#94a3b8;border:1px dashed #e2e8f0;border-radius:10px;font-size:13px;">Fix the errors in the sidebar before running the simulation.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
