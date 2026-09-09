# Business Support Operations Console

**Project type:** Internal tooling prototype — Business Support / Business Management function

**Prepared by:** Emmanuel R. Simbulan

**Status:** Completed — deployed in https://emmanuelsimbulan.github.io/business-support-console/


**Last updated:** September 2026

---

## ⚠️ Disclosure

This repository is a **demonstration prototype**, built to illustrate how a Business Support function could structure its reporting, workspace planning, stakeholder coordination, and risk tracking. It was created as part of interview preparation and as a portfolio piece.

- All data — task names, occupancy figures, initiatives, risks, people, and teams — is **synthetic**. None of it reflects any real company, project, or individual.
- The system is **not connected to any live source system** (HRIS, badge data, ticketing, or otherwise). Figures shown are illustrative only.
- No claim is made that this was deployed in production or used to manage a real business function.

Where this document uses project-management language (objectives, stakeholders, outcomes), it is written in the voice a real deployment would use, so the document itself demonstrates the kind of documentation I would produce on the job — not because the underlying project happened.

---

## 1. Executive Summary

Business Support functions typically sit at the center of four recurring demands: **recurring reporting**, **workspace and site planning**, **cross-functional coordination** (often across teams with no reporting relationship to one another, such as Real Estate, Facilities, and Technology), and **risk and initiative tracking**. In most organizations, these four demands are handled through disconnected tools — a spreadsheet for tasks, a deck for the scorecard, a hallway conversation for status, a notebook for risks.

This prototype consolidates all four into a single, lightweight console to demonstrate what "good" looks like when they're treated as one connected system rather than four separate habits. It is deliberately built without any external software dependency, so it can be opened, reviewed, and modified by anyone with a browser.

---

## 2. Business Context

### 2.1 The problem this pattern addresses

| Observed symptom | Root cause |
|---|---|
| Leadership learns an initiative has stalled only when asked directly | No standing, decision-ready scorecard — status exists verbally or in scattered decks |
| Space or headcount requests are approved or denied on anecdote | Occupancy and utilization are not reconciled against actual usage data before a decision is made |
| A cross-team initiative slips because two groups each assumed the other owned a step | No explicit, shared ownership model across teams that do not report to one another |
| A risk becomes an issue before anyone raised it formally | Risks are discussed informally rather than logged, owned, and tracked to resolution |
| The same recurring process is rebuilt from memory each cycle | No standardized, version-controlled documentation of how the work actually gets done |

### 2.2 Why this matters for a Business Support Manager specifically

A Business Support Manager is frequently the only role with visibility across all of the above simultaneously — the person translating between data, stakeholders, and leadership, and the person accountable for making sure nothing falls into the gap between two teams. The cost of *not* solving this pattern isn't a single failure; it's a steady accumulation of small misalignments that eventually surface as a missed deadline, a wrong space decision, or a risk that reaches leadership too late to act on cheaply.

---

## 3. Objectives

| # | Objective | How the prototype demonstrates it |
|---|---|---|
| O1 | Give leadership a single, current view of initiative health | Overview & Scorecard module |
| O2 | Base space and staffing decisions on reconciled usage data, not anecdote | Workspace & Occupancy module |
| O3 | Make cross-team ownership explicit before work starts, not after it stalls | Stakeholder Coordination module (RACI + phase timeline) |
| O4 | Keep day-to-day work visible without manual status-chasing | Task Planner module |
| O5 | Surface risk early, with a recommendation attached | Risk Register module |
| O6 | Make recurring reporting reproducible in the tools the business actually uses | Reporting & Analytics module |
| O7 | Make process improvements durable rather than one-time fixes | Process Improvement module |

### 3.1 Out of scope

To keep the prototype legible, the following were deliberately excluded:

- Integration with any real system of record (HRIS, badge readers, ticketing, financial systems)
- User authentication, permissions, or multi-user editing
- Persistent storage — all data is defined in-file and resets on reload
- Mobile-native app packaging (the console is responsive, but built as a web page, not an app)

---

## 4. Stakeholders

| Stakeholder | Interest in this system |
|---|---|
| Business unit leadership | Consumes the Overview & Scorecard for decisions and business reviews |
| Real Estate | Co-owns space-planning workstreams shown in Stakeholder Coordination |
| Facilities | Co-owns build-out and occupancy-related workstreams |
| Technology | Co-owns systems, network/AV, and access-control items referenced in Task Planner and Risk Register |
| Accounting / Operations | Source of the recurring process work shown in Task Planner and Process Improvement |
| Business Support (this role) | Owns the system end to end — data quality, cadence, and escalation |

---

## 5. Solution Design

The console is organized into seven modules, grouped by audience and cadence:

### Executive view
**5.1 Overview & Scorecard**
A single page built for a leadership review: KPI tiles, a written executive summary that leads with the interpretation rather than the raw numbers, an initiative status table using RAG (Red/Amber/Green) coding, and quarterly goal-progress tracking.

### Workspace & operations
**5.2 Workspace & Occupancy**
Occupancy broken out by floor and by day of week — the latter specifically to surface demand clustering (for example, mid-week peaks) that a simple average would hide — plus a sample seat-utilization view and a tracker for active site initiatives.

**5.3 Stakeholder Coordination**
A single initiative followed end to end, including a RACI matrix assigning Responsible / Accountable / Consulted / Informed status across every workstream and stakeholder group, a phase-based timeline, and a coordination log demonstrating how status is actually communicated across teams.

**5.4 Task Planner**
A filterable register of active work items, each with an owner, priority, status, due date, and a link back to the goal or initiative it supports.

### Insights & governance
**5.5 Reporting & Analytics**
Task-volume and completion-rate visualizations, plus a pivot-style summary table. This module includes an explicit note that, in a real deployment, this same view would be produced in Excel (PivotTables) or Power BI / Tableau depending on the audience and refresh cadence — the in-browser charts here are a stand-in for those tools, not a proposed replacement for them.

This module also links to a Python companion script (`analysis/reporting_analysis.py`) that derives the same rollups — plus a couple this page doesn't show, like an overdue-item flag — from the identical sample data using pandas, renders the charts with matplotlib, and exports a formatted Excel workbook. See §7.1 below.

**5.6 Risk Register**
A RAID-style (Risks, Assumptions, Issues, Dependencies) log, with each entry linked to the initiative it threatens, an owner, and a current status, so a risk is never just a description without accountability attached.

**5.7 Process Improvement**
A generalized before/after case study and timeline, modeled on the shape of a documentation-standardization effort, showing how a one-time fix is converted into a durable standard.

---

## 6. Methodology

The system is organized around an eight-stage operating model for Business Support work, grouped into four phases:

```
LISTEN            LOOK              LEAD                    LOCK IT IN
Intake      →   Data          →   Recommend        →   Track & Escalate
Discovery   →   Analysis      →   Coordinate        →   Embed & Improve
```

Each module in the console corresponds to one or more of these stages — the Task Planner captures Intake, Workspace & Occupancy captures Data and Analysis, Stakeholder Coordination captures Recommend and Coordinate, and the Risk Register and Process Improvement modules capture Track & Escalate and Embed & Improve, respectively. This loop is treated as continuous: outputs from "Embed & Improve" feed back into the next cycle's "Intake."

---

## 7. Technical Notes

| Aspect | Detail |
|---|---|
| Format | Self-contained `index.html`, plus one pre-rendered chart image the Reporting & Analytics module embeds from `analysis/output/charts/` |
| Dependencies | One Google Fonts import (Fraunces, Inter); no JavaScript frameworks or build tools |
| Data layer | Plain JavaScript arrays of objects, defined near the end of the file — one array per table or chart |
| Hosting | Static hosting compatible (GitHub Pages); no backend or database required |
| Modification | Editing the data arrays changes the displayed content directly; no compilation step |
| Accessibility | Responsive layout; keyboard-navigable controls; color choices checked for contrast |

This structure was chosen deliberately: a near-dependency-free file can be opened, reviewed, or shared in any environment without setup, which matters for a tool meant to demonstrate reporting practice rather than to run as production software.

### 7.1 Python analysis layer

| Aspect | Detail |
|---|---|
| Format | `analysis/reporting_analysis.py` — single script, standard library + pandas/matplotlib/openpyxl |
| What it does | Recomputes the console's KPI rollups, status × priority pivot, and volume-by-function ranking from the same sample data using pandas; flags overdue open items; renders the completion-trend, occupancy, and volume charts with matplotlib; exports a formatted multi-sheet Excel workbook |
| Why it exists | The HTML page hardcodes its rollups for portability; this script shows the same numbers derived rather than typed, and is the piece of the prototype that maps most directly to the JD's data-analysis and Excel/reporting-automation language |
| Output | `analysis/output/business_support_report.xlsx` and `analysis/output/charts/*.png` — one chart from this output is embedded directly in the Reporting & Analytics module |
| Run it | `pip install -r analysis/requirements.txt && python analysis/reporting_analysis.py` |

---

## 8. Risks and Assumptions of the Prototype Itself

| Item | Type | Note |
|---|---|---|
| All figures are illustrative | Assumption | No real usage or performance data underlies any chart |
| No data persistence | Limitation | Refreshing the page resets any in-session interaction (filters, tab state) |
| Single-user design | Limitation | Not built for concurrent editing or multi-user workflows |
| Static dataset | Limitation | Would require a real data pipeline (HRIS export, badge system, ticketing API) to move from demonstration to production use |

---

## 9. Reflection

Building this surfaced a distinction worth stating plainly: the *reporting discipline* behind a system like this — reconcile the data, find the actual driver rather than the surface symptom, make the recommendation decision-ready, track whether it worked — is the same regardless of whether the underlying subject is workforce attendance, accounting reconciliation, or desk occupancy. What changes is the domain vocabulary and the specific stakeholders in the room, not the method.

Where this prototype is honest about its limits: it does not simulate the harder, less structured parts of the job — a stakeholder who disagrees with the numbers, a timeline that slips for a reason no dashboard predicted, a leader who wants the story behind the metric rather than the metric itself. Those are judgment calls that a static demo can illustrate but not truly replicate.

---

## 10. How to Run

**The console**
1. Download `index.html` (and the `analysis/output/charts/` folder alongside it, if you want the embedded chart on the Reporting & Analytics page to render)
2. Open `index.html` in any modern browser — no installation, server, or internet connection required after the initial font load
3. To modify sample data, edit the arrays defined in the `<script>` section near the bottom of the file

To view the hosted version instead of running it locally, see the GitHub Pages link (https://emmanuelsimbulan.github.io/business-support-console/).

**The Python analysis layer**
1. `pip install -r analysis/requirements.txt`
2. `python analysis/reporting_analysis.py`
3. Review the console summary it prints, and the workbook/charts written to `analysis/output/`

---

*This document and the system it describes are demonstration materials created for professional portfolio purposes. All names, figures, and scenarios are fictional.*
