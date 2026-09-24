#!/usr/bin/env python3
"""Generate a detailed V2G project Gantt chart (PNG + SVG data for HTML)."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch

OUT = Path(__file__).resolve().parent

# (label, owner, start, end, task_group, phase)
# Dates inclusive start, exclusive-ish end shown as through end date
TASKS = [
    # Task 0
    ("0.1 Kickoff meeting — roles & norms", "All", date(2026, 9, 24), date(2026, 9, 24), "0 Kickoff", "kickoff"),
    ("0.2 Freeze document schema + label enums", "All", date(2026, 9, 24), date(2026, 9, 25), "0 Kickoff", "kickoff"),
    ("0.3 Choose tech stack & repo layout", "All", date(2026, 9, 24), date(2026, 9, 25), "0 Kickoff", "kickoff"),
    ("0.4 Draft sources.yaml v1 (5–8 sources)", "Anahid, Sandeep", date(2026, 9, 24), date(2026, 9, 26), "0 Kickoff", "kickoff"),
    ("0.5 Create 15–20 mock documents", "All", date(2026, 9, 24), date(2026, 9, 26), "0 Kickoff", "kickoff"),
    ("0.6 MVP definition-of-done one-pager", "All", date(2026, 9, 25), date(2026, 9, 26), "0 Kickoff", "kickoff"),
    # Task 1
    ("1.1 SQL/schema migrations (core tables)", "Frank, Isaac", date(2026, 9, 27), date(2026, 9, 29), "1 Database", "phase1"),
    ("1.2 Content hash + versioning API", "Frank, Isaac", date(2026, 9, 28), date(2026, 9, 30), "1 Database", "phase1"),
    ("1.3 upsert / list / get repository layer", "Frank", date(2026, 9, 29), date(2026, 10, 1), "1 Database", "phase1"),
    ("1.4 Seed DB with mocks + unit tests", "Isaac", date(2026, 9, 30), date(2026, 10, 1), "1 Database", "phase1"),
    ("1.5 JSONL export / snapshot for eval", "Frank", date(2026, 9, 30), date(2026, 10, 1), "1 Database", "phase1"),
    # Task 2
    ("2.1 Source registry wired to collectors", "Anahid", date(2026, 9, 27), date(2026, 9, 30), "2 Ingestion", "phase1"),
    ("2.2 ToS / robots access notes", "Anahid", date(2026, 9, 27), date(2026, 10, 1), "2 Ingestion", "phase1"),
    ("2.3 HTML collector (first 2 sources)", "Sandeep", date(2026, 9, 29), date(2026, 10, 3), "2 Ingestion", "phase1"),
    ("2.4 PDF + Excel extractors", "Sandeep", date(2026, 10, 1), date(2026, 10, 5), "2 Ingestion", "phase1"),
    ("2.5 Persist via DB API + run logs", "Anahid, Sandeep", date(2026, 10, 2), date(2026, 10, 6), "2 Ingestion", "phase1"),
    ("2.6 Expand to ≥5 sources; CLI ingest", "Anahid", date(2026, 10, 4), date(2026, 10, 8), "2 Ingestion", "phase1"),
    ("2.7 Optional: schedule cron (if stable)", "Anahid", date(2026, 10, 7), date(2026, 10, 8), "2 Ingestion", "phase1"),
    # Task 3
    ("3.1 Classification prompt + schema map", "Isaac", date(2026, 10, 8), date(2026, 10, 10), "3 Classification", "phase1"),
    ("3.2 Classify-on-change job (hash trigger)", "Isaac", date(2026, 10, 9), date(2026, 10, 12), "3 Classification", "phase1"),
    ("3.3 Backfill labels on existing docs", "Isaac", date(2026, 10, 11), date(2026, 10, 14), "3 Classification", "phase1"),
    ("3.4 Spot-check 10 docs; calibrate prompt", "Isaac", date(2026, 10, 13), date(2026, 10, 15), "3 Classification", "phase1"),
    # Task 4
    ("4.1 Chunker + metadata on chunks", "Sandeep", date(2026, 10, 1), date(2026, 10, 6), "4 RAG", "phase2"),
    ("4.2 Embeddings + vector store (mocks)", "Sandeep", date(2026, 10, 4), date(2026, 10, 10), "4 RAG", "phase2"),
    ("4.3 Retrieve API + date/label filters", "Sandeep", date(2026, 10, 8), date(2026, 10, 15), "4 RAG", "phase2"),
    ("4.4 Hash-aware re-index; skip unchanged", "Sandeep", date(2026, 10, 13), date(2026, 10, 18), "4 RAG", "phase2"),
    ("4.5 Smoke test 5 questions on real docs", "Sandeep", date(2026, 10, 16), date(2026, 10, 22), "4 RAG", "phase2"),
    # Task 5
    ("5.1 Streamlit shell (Q box, filters)", "Frank", date(2026, 10, 8), date(2026, 10, 14), "5 UI", "phase2"),
    ("5.2 Grounded answer prompt + citations", "Frank", date(2026, 10, 12), date(2026, 10, 22), "5 UI", "phase2"),
    ("5.3 Wire retrieve API; corpus-as-of banner", "Frank", date(2026, 10, 20), date(2026, 10, 29), "5 UI", "phase2"),
    ("5.4 Q&A logging for evaluation", "Frank", date(2026, 10, 27), date(2026, 11, 2), "5 UI", "phase2"),
    ("5.5 UI polish + Fuse demo dry-run", "Frank", date(2026, 11, 2), date(2026, 11, 5), "5 UI", "phase2"),
    # Task 6
    ("6.1 Draft ~30 gold questions (buckets)", "Anahid", date(2026, 10, 8), date(2026, 10, 17), "6 Evaluation", "eval"),
    ("6.2 Expected cites / must-refuse notes", "Anahid", date(2026, 10, 15), date(2026, 10, 24), "6 Evaluation", "eval"),
    ("6.3 Eval runner (accuracy + citations)", "Anahid", date(2026, 10, 27), date(2026, 11, 5), "6 Evaluation", "eval"),
    ("6.4 Optional RAGAs scorecard pass", "Anahid", date(2026, 11, 3), date(2026, 11, 8), "6 Evaluation", "eval"),
    ("6.5 2-model comparison + eval report", "Anahid", date(2026, 11, 6), date(2026, 11, 12), "6 Evaluation", "eval"),
    # Task 7
    ("7.1 README runbook (ingest, index, UI)", "All", date(2026, 11, 12), date(2026, 11, 15), "7 Docs & demo", "docs"),
    ("7.2 Architecture diagram + limitations", "All", date(2026, 11, 13), date(2026, 11, 16), "7 Docs & demo", "docs"),
    ("7.3 Deck, demo script, presentation", "All", date(2026, 11, 14), date(2026, 11, 18), "7 Docs & demo", "docs"),
    # Stretch
    ("S.1 Diff query (new/changed last 7 days)", "TBD", date(2026, 11, 12), date(2026, 11, 15), "S Stretch digest", "stretch"),
    ("S.2 Weekly digest generation + page", "TBD", date(2026, 11, 14), date(2026, 11, 18), "S Stretch digest", "stretch"),
]

COLORS = {
    "kickoff": "#1e4d6b",
    "phase1": "#2a6f6f",
    "phase2": "#b45309",
    "eval": "#6b3fa0",
    "docs": "#374151",
    "stretch": "#9ca3af",
}

MILESTONES = [
    ("Kickoff done / schema freeze", date(2026, 9, 26)),
    ("DB ready (Task 1)", date(2026, 10, 1)),
    ("Ingest MVP ≥5 sources", date(2026, 10, 8)),
    ("Labels on store", date(2026, 10, 15)),
    ("Queryable RAG", date(2026, 10, 22)),
    ("UI + citations demo", date(2026, 11, 5)),
    ("Eval report (MVP)", date(2026, 11, 12)),
    ("Presentation / handover", date(2026, 11, 18)),
]


def main() -> None:
    n = len(TASKS)
    fig_h = max(12, n * 0.32 + 2.5)
    fig, ax = plt.subplots(figsize=(16, fig_h), dpi=160)

    # Row 0 at top = first subtask
    for y, (label, owner, start, end, _group, phase) in enumerate(TASKS):
        duration = (end - start).days + 1
        ax.barh(
            y,
            duration,
            left=mdates.date2num(start),
            height=0.65,
            color=COLORS[phase],
            edgecolor="white",
            linewidth=0.4,
            alpha=0.92,
        )
        ax.text(
            mdates.date2num(end) + 0.35,
            y,
            owner,
            va="center",
            ha="left",
            fontsize=6.5,
            color="#4b5563",
        )

    ax.set_yticks(list(range(n)))
    ax.set_yticklabels([t[0] for t in TASKS], fontsize=7.5)
    ax.set_xlim(mdates.date2num(date(2026, 9, 22)), mdates.date2num(date(2026, 11, 22)))
    ax.set_ylim(n - 0.5, -0.5)  # first task on top
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_minor_locator(mdates.DayLocator())
    ax.grid(axis="x", which="major", linestyle="-", alpha=0.25)
    ax.grid(axis="x", which="minor", linestyle=":", alpha=0.12)
    ax.set_axisbelow(True)

    for name, d in MILESTONES:
        x = mdates.date2num(d)
        ax.axvline(x, color="#dc2626", linestyle="--", linewidth=0.9, alpha=0.75)
        ax.text(
            x,
            -1.1,
            name,
            rotation=90,
            va="bottom",
            ha="right",
            fontsize=6,
            color="#b91c1c",
        )

    # Today-ish project start marker
    ax.axvline(mdates.date2num(date(2026, 9, 24)), color="#111827", linewidth=1.2, alpha=0.5)

    legend = [
        Patch(facecolor=COLORS["kickoff"], label="0 Kickoff"),
        Patch(facecolor=COLORS["phase1"], label="Phase 1 — Ingestion"),
        Patch(facecolor=COLORS["phase2"], label="Phase 2 — RAG / UI"),
        Patch(facecolor=COLORS["eval"], label="6 Evaluation"),
        Patch(facecolor=COLORS["docs"], label="7 Docs & demo"),
        Patch(facecolor=COLORS["stretch"], label="Stretch digest"),
    ]
    ax.legend(handles=legend, loc="lower right", fontsize=8, framealpha=0.95)
    ax.set_title(
        "V2G Intelligence Platform — Detailed Gantt\n"
        "Team: Anahid · Sandeep · Frank · Isaac  |  Fuse Capstone  |  Sep 24 – Nov 18, 2026",
        fontsize=12,
        pad=12,
        fontweight="bold",
    )
    ax.set_xlabel("2026 calendar")
    fig.tight_layout()
    png = OUT / "V2G_Gantt_Detailed.png"
    svg = OUT / "V2G_Gantt_Detailed.svg"
    fig.savefig(png, bbox_inches="tight", facecolor="white")
    fig.savefig(svg, bbox_inches="tight", facecolor="white")
    plt.close()
    print("wrote", png, svg)


if __name__ == "__main__":
    main()
