# 📊 Project Simulator

A web-based project timeline simulator built with Streamlit. Define project activities, model uncertainty using three-point estimation, visualize dependencies, and run Monte Carlo simulations to estimate completion probability.

---

## Features

- **Activity builder** — add, edit, delete, and reorder project activities manually
- **CSV bulk import** — upload activities from a spreadsheet with template download
- **Dependency validation** — catches circular dependencies, missing start/end nodes, self-references, disconnected graphs, and invalid inputs before simulation
- **Network diagram** — auto-generated visual of the activity dependency graph
- **Monte Carlo simulation** — samples durations across thousands of iterations using PERT Beta or Triangular distributions
- **Results dashboard** — expected finish time, standard deviation, confidence intervals (P50–P95), and bottleneck analysis

---

## Installation

**Requirements:** Python 3.8+

```bash
pip install streamlit numpy pandas plotly scipy
```

---

## Running the App

```bash
streamlit run app.py
```

Opens at `http://localhost:8501` in your browser.

---

## How to Use

### Step 1 — Project Setup

Add each activity in your project:

| Field | Description |
|---|---|
| Activity Name | Full name of the task |
| Label | Short unique identifier (e.g. A, B, T1) |
| Predecessors | Activities that must finish before this one starts |
| Minimum | Best-case duration |
| Most Likely | Expected duration under normal conditions |
| Maximum | Worst-case duration |

Use **↑ ↓** buttons to reorder activities. Click **Edit** to modify any row inline. Deleting an activity automatically removes it from all predecessor lists.

Click **Load Example Project** to pre-load a 7-activity Computer Design project for reference.

---

### Step 1b — CSV Import (Optional)

1. Click **Download CSV Template** to get a pre-filled example file
2. Edit the file in Excel, Google Sheets, or any text editor
3. Upload it via the **Upload CSV** section
4. Review the row-by-row validation preview
5. Choose **Append** (add to existing) or **Replace** (clear and import)
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

- `predecessors` column accepts comma-separated labels (e.g. `"C,D"`), leave blank for start activities
- Import is all-or-nothing — no activities are added if any row contains an error

---

### Step 2 — Network Diagram

Displays the activity dependency graph. Hover over any node to see:
- Duration range (min / most likely / max)
- PERT expected duration (te)
- Variance
- Predecessor list

Also shows a summary table with computed te and variance for every activity.

**PERT expected duration formula:**
```
te = (min + 4 × most_likely + max) / 6
```

**Variance formula:**
```
variance = ((max − min) / 6)²
```

---

### Step 3 — Monte Carlo Simulation

**Settings:**

| Setting | Options | Default |
|---|---|---|
| Iterations | 500 / 1,000 / 5,000 / 10,000 / 25,000 / 50,000 | 10,000 |
| Distribution | PERT Beta, Triangular | PERT Beta |

**PERT Beta** — weights the most likely estimate four times more than the extremes. More accurate for project estimation.

**Triangular** — treats all three points equally. Simpler but less statistically rigorous.

**Results:**

- **Expected Finish** — mean completion time across all simulations
- **Std. Deviation** — spread of uncertainty
- **Minimum / Maximum** — observed range across all runs
- **Confidence intervals** — P50 through P95: the time by which X% of simulations completed
- **Bottleneck analysis** — which activity was last to finish most often across all runs

---

## Validation Rules

The app blocks progression if any of the following are detected:

- No activities added
- Duplicate labels
- Invalid label characters (only letters and numbers allowed)
- Self-referencing predecessor
- Unknown predecessor reference
- No start node (every activity has a predecessor)
- No end node (every activity has a successor)
- Circular dependency
- Duration values where min > most likely or most likely > max

Warnings (non-blocking) are shown for:

- All durations set to zero
- Degenerate distribution (min = most likely = max)
- Unusually large duration values
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

This tool implements **PERT (Program Evaluation and Review Technique)** three-point estimation combined with **Monte Carlo simulation**.

PERT was developed by the US Navy in the 1950s for the Polaris missile program. It accounts for uncertainty in task duration by requiring three estimates rather than one, and has been widely adopted in project management ever since.

Monte Carlo simulation repeatedly samples random durations from each activity's distribution and computes the resulting project finish time. Aggregating thousands of runs produces a probability distribution over possible completion dates, which is more informative than a single deterministic estimate.
