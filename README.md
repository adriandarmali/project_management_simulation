# 📊 Project Simulator

A web-based project timeline simulator built with Streamlit. Define project activities, model uncertainty with three-point estimation, visualize dependencies, and run Monte Carlo simulations to estimate completion probability and schedule risk.

🔗 **[Live App]([https://your-app-name.streamlit.app](https://projectmanagementking.streamlit.app/))** *(replace with your Streamlit Cloud URL)*

---

## Features

- **Activity manager** — add, edit, delete, and reorder activities in a persistent sidebar
- **CSV bulk import** — upload activities from a spreadsheet with template download
- **Full validation** — catches circular dependencies, missing start/end nodes, self-references, disconnected graphs, duplicate labels, invalid characters, and illogical durations
- **Network diagram** — auto-generated dependency graph with critical path highlighted in red
- **5 distribution types** — Uniform, PERT Beta, Triangular, Normal, Log-normal
- **Monte Carlo simulation** — up to 50,000 iterations with live progress bar
- **5 result tabs** — Summary, Critical Path, Gantt Chart, Risk Analysis, Bottleneck

---

## Installation (Local)

```bash
pip install streamlit numpy pandas plotly scipy
streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select the repo, set `app.py` as the main file
5. Click **Deploy** — no extra configuration needed

---

## How to Use

### Layout

| Area | Purpose |
|---|---|
| **Sidebar (left 1/3)** | Add and manage activities |
| **Main canvas (right 2/3)** | Network diagram, simulation controls, results |
| **Main toolbar** | Load example, import/export CSV, clear all |

---

### Step 1 — Add Activities (Sidebar)

Click **+ Add Activity** and fill in:

| Field | Description |
|---|---|
| Name | Full name of the task |
| Label | Short unique ID, letters and numbers only (e.g. A, B, T1) |
| Predecessors | Activities that must finish before this one starts |
| Minimum | Best-case duration |
| Most Likely | Expected duration under normal conditions |
| Maximum | Worst-case duration |

Use **↑ ↓** to reorder. Click **Edit** to modify a row inline. Deleting an activity automatically removes it from all predecessor lists.

Validation runs live — errors appear in the sidebar next to the relevant activity.

---

### Step 2 — Import via CSV (Optional)

Click **📂 Import / Export CSV** on the main canvas toolbar.

1. Download the template
2. Fill it in Excel, Google Sheets, or any text editor
3. Upload the file
4. Review the row-by-row validation preview
5. Choose **Append** (add alongside existing) or **Replace** (clear and import)
6. Click **Import**

**CSV format:**

```
name,label,predecessors,min_duration,avg_duration,max_duration
Design,A,,16,21,26
Build Prototype,B,A,3,6,9
Evaluate Equipment,C,A,5,7,9
Test Prototype,D,B,2,3,4
Write Equipment Report,E,"C,D",4,6,8
Write Methods Report,F,"C,D",6,8,10
Write Final Report,G,"E,F",1,2,3
```

- `predecessors` accepts comma-separated labels in quotes (e.g. `"C,D"`), leave blank for start activities
- Import is all-or-nothing — no activities are added if any row has an error

---

### Step 3 — Review the Network Diagram

The diagram auto-updates whenever activities change.

- **Red nodes and edges** = deterministic critical path (using PERT te values)
- **Dark nodes** = non-critical activities
- Hover over any node to see: duration range, expected duration (te), variance, predecessor list

---

### Step 4 — Run the Simulation

**Distribution options:**

| Distribution | When to use |
|---|---|
| **Uniform** *(default)* | Equal probability across min–max range. Conservative and assumption-free. |
| **PERT Beta** | Weights most likely estimate 4× more than extremes. Best for project estimation. |
| **Triangular** | Equal weight on min, likely, max. Simple but less precise than PERT. |
| **Normal** | Symmetric bell curve centred on most likely. Use when data supports symmetry. |
| **Log-normal** | Right-skewed — models tasks that occasionally run very long. |

**Iteration options:** 500 / 1,000 / 5,000 / 10,000 / 25,000 / 50,000 (default: 10,000)

Click **▶ Run Simulation**.

---

### Step 5 — Read the Results

Results appear in five tabs after the simulation completes.

#### 📈 Summary
- **P90** shown as the dominant headline stat — the deadline with 90% confidence
- Expected finish, standard deviation, observed range
- Histogram of all simulated finish times with mean, P50, P90 reference lines
- S-curve showing cumulative completion probability across time
- Confidence table: P50 through P95

#### 🔗 Critical Path
- Critical path sequence highlighted with red badges
- Total critical path duration using PERT te values
- Float analysis table for every activity — shows how much each can slip before delaying the project
- Float bar chart: red = zero float (critical), teal = has slack

#### 📅 Gantt Chart
- Horizontal bar chart of expected activity timeline using PERT te
- Based on earliest start / earliest finish from forward pass
- Red bars = critical path, teal bars = non-critical
- Hover for start, finish, and duration details

#### ⚠ Risk Analysis
- **Tornado chart** — Spearman correlation between each activity's duration and the overall finish time. Activities closest to 1.0 have the most leverage on the schedule.
- **Risk register** — per-activity table showing: duration spread, sensitivity, probability of exceeding most likely, estimated impact, risk score (probability × impact), and risk level (High / Medium / Low)
- **Schedule buffer recommendation** — how much buffer to add to P50 to reach P90 confidence, expressed in both units and as a percentage

#### 🔍 Bottleneck
- Bar chart of how often each activity was the last to finish across all simulation runs
- Side-by-side comparison of deterministic critical path vs simulation bottlenecks
- Warning shown when they diverge — indicates latent schedule risks not visible in the PERT analysis

---

## Validation Rules

**Blocks simulation:**
- No activities added
- Duplicate labels
- Invalid label characters (letters and numbers only)
- Self-referencing predecessor
- Unknown predecessor reference
- No start node (every activity has a predecessor)
- No end node (every activity has a successor)
- Circular dependency
- Duration where min > most likely or most likely > max

**Advisory warnings (non-blocking):**
- All durations set to zero
- Degenerate distribution (min = most likely = max)
- Unusually large duration values (> 5,200 units)
- Disconnected graph
- Duplicate activity names

---

## File Structure

```
app.py              # Main Streamlit application
requirements.txt    # Python dependencies
README.md           # This file
```

---

## Dependencies

```
streamlit
numpy
pandas
plotly
scipy
```

---

## Method Reference

**PERT (Program Evaluation and Review Technique)** — developed by the US Navy in the 1950s for the Polaris missile program. Accounts for duration uncertainty using three estimates: minimum, most likely, and maximum.

**PERT expected duration formula:**
```
te = (min + 4 × most_likely + max) / 6
```

**Variance formula:**
```
variance = ((max − min) / 6)²
```

**Monte Carlo simulation** — repeatedly samples random durations from each activity's chosen distribution, runs a forward pass to compute project finish time, and aggregates thousands of results into a probability distribution. More informative than a single deterministic estimate because it explicitly models uncertainty.

**Critical path** — the sequence of activities with zero total float. Any delay on the critical path directly delays the project end date.

**Total float** — how long an activity can be delayed without delaying the project end date.

**Sensitivity (Tornado chart)** — Spearman rank correlation between each activity's sampled duration and the project finish time across all simulation runs. Identifies which activities have the most influence on schedule outcomes.
