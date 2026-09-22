#!/usr/bin/env python3
"""Download 50 open-access PDFs using curl (urllib hits 406/403 on some hosts)."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path(__file__).resolve().parent
PDF_DIR = OUT / "pdfs"
NS = {"a": "http://www.w3.org/2005/Atom"}
UA = "Mozilla/5.0 (compatible; FuseV2GLitReview/1.0; +https://northeastern.edu)"

REPORTS = [
    {
        "id": "csa-vgi-canada",
        "title": "Charging Ahead: Unlocking Vehicle-Grid Integration in Canada",
        "year": 2024,
        "theme": "canada-vgi",
        "source": "CSA Group",
        "url": "https://www.csagroup.org/wp-content/uploads/CSA-Group-Research-Charging-Ahead-Unlocking-Vehicle-Grid-Integration-in-Canada.pdf",
    },
    {
        "id": "ubc-walgama-2025",
        "title": "Barriers and Opportunities to Energy Sharing Between Vehicles and Buildings During an Emergency, and Vehicles and Grids at Other Times",
        "year": 2025,
        "theme": "canada-vgi",
        "source": "UBC Sustainability Scholars",
        "url": "https://sustain.ubc.ca/sites/default/files/2025-022_Energy%20Sharing%20Opportunities%20V2B%20%26%20V2G_Walgama.pdf",
    },
    {
        "id": "ieso-gif-sky-clean",
        "title": "Optimal Vehicle to Grid Charging System Considering Solar, Storage, and User Privacy (IESO Grid Innovation Fund final report)",
        "year": 2024,
        "theme": "canada-pilot",
        "source": "IESO",
        "url": "https://www.ieso.ca/-/media/Files/IESO/Document-Library/funding/Grid-Innovation-Fund/Sky-Clean-Energy-GIF-final-report.pdf",
    },
    {
        "id": "ieso-v2g-memo-2025",
        "title": "Memorandum on Consideration of Bidirectional Charging in Local Achievable Potential Studies for Toronto and Ottawa",
        "year": 2025,
        "theme": "canada-policy",
        "source": "IESO",
        "url": "https://www.ieso.ca/-/media/Files/IESO/Document-Library/regional-planning/Toronto/toronto-20250821-Memorandum.pdf",
    },
    {
        "id": "doi:10.3390/en17030679",
        "title": "Feasibility and Challenges for Vehicle-to-Grid in Electricity Market: A Review",
        "year": 2024,
        "theme": "v2g-market",
        "source": "MDPI Energies",
        "url": "https://mdpi-res.com/d_attachment/energies/energies-17-00679/article_deploy/energies-17-00679.pdf",
    },
    {
        "id": "nrcan-grid-readiness",
        "title": "What we heard: NRCan request for information on grid readiness for electric vehicles",
        "year": 2024,
        "theme": "canada-policy",
        "source": "NRCan",
        "url": "https://natural-resources.canada.ca/sites/nrcan/files/energy/pdf/What%20we%20heard%20-%20NRCan%20RFI%20on%20grid%20readiness%20for%20EVs.pdf",
    },
]

# arXiv ids chosen for V2G/VGI/ISO 15118/policy + RAG/citations/energy RAG
ARXIV = {
    "v2g": [
        "2508.06752",
        "2005.06042",
        "2110.12225",
        "2504.09657",
        "2106.05837",
        "2307.07399",
        "2309.11118",
        "2301.12041",
        "2406.19296",
        "2507.21154",
        "1609.01437",
        "1607.06906",
        "2407.16180",
        "1410.1282",
        "2112.15006",
        "1701.01527",
        "2204.05545",
        "2101.10518",
        "2401.10194",
        "2009.12201",
        "2210.10522",
        "2403.06632",
        "2203.05266",
        "2404.06635",
        "2008.08939",
        "2111.01294",
        "2504.01423",
        "2509.05940",
        "2404.02361",
        "1808.03897",
        "2204.11565",
        "2405.00947",
        "1901.06406",
        "2501.14397",
        "2202.02104",
        "1703.04552",
    ],
    "rag": [
        "2508.12682",
        "2312.10997",
        "2405.07437",
        "2407.13193",
        "2410.11217",
        "2305.14627",
        "2005.11401",
        "2401.18059",
        "2401.05856",
        "2405.06211",
        "2402.19473",
        "2404.10981",
        "2211.09260",
        "2310.06825",
        "2401.15884",
        "2312.05708",
        "2004.04906",
        "2405.14831",
        "2312.05725",
        "2402.01763",
        "2301.12652",
        "2210.11416",
        "2202.01110",
        "2406.04744",
        "2502.04342",
        "2402.12366",
        "2412.03981",
        "2308.07107",
        "2404.00610",
        "2311.09476",
    ],
}


def curl(url: str, dest: Path | None = None, accept: str = "*/*") -> subprocess.CompletedProcess:
    cmd = [
        "curl",
        "-fsSL",
        "-A",
        UA,
        "-H",
        f"Accept: {accept}",
        "-L",
        "--retry",
        "3",
        "--retry-delay",
        "2",
        "--max-time",
        "90",
    ]
    if dest:
        cmd += ["-o", str(dest)]
    cmd.append(url)
    return subprocess.run(cmd, capture_output=True)


def slug(s: str, n: int = 70) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:n] or "article"


def arxiv_meta(arxiv_id: str) -> dict | None:
    url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}&max_results=1"
    p = curl(url, accept="application/atom+xml,application/xml,text/xml,*/*")
    if p.returncode != 0:
        return None
    root = ET.fromstring(p.stdout)
    entry = root.find("a:entry", NS)
    if entry is None:
        return None
    title_el = entry.find("a:title", NS)
    pub = entry.find("a:published", NS)
    summary = entry.find("a:summary", NS)
    title = re.sub(r"\s+", " ", (title_el.text or "")).strip() if title_el is not None else arxiv_id
    year = int(pub.text[:4]) if pub is not None and pub.text else None
    abstract = re.sub(r"\s+", " ", (summary.text or "")).strip() if summary is not None else ""
    return {"title": title, "year": year, "abstract": abstract[:400]}


def is_pdf(path: Path) -> bool:
    with path.open("rb") as f:
        return f.read(5) == b"%PDF-"


def main() -> None:
    if PDF_DIR.exists():
        for p in PDF_DIR.glob("*.pdf"):
            p.unlink()
    else:
        PDF_DIR.mkdir(parents=True)

    records: list[dict] = []
    seen_ids: set[str] = set()

    def add_downloaded(rec: dict, idx: int) -> bool:
        dest = PDF_DIR / f"{idx:02d}_{rec.get('year') or 'nd'}_{slug(rec['title'])}.pdf"
        print(f"GET {idx}/50 {rec['title'][:90]}")
        p = curl(rec["url"], dest)
        if p.returncode != 0 or not dest.exists() or not is_pdf(dest):
            err = (p.stderr or b"").decode("utf-8", "ignore")[:200]
            print(f"  FAIL {err}")
            if dest.exists():
                dest.unlink()
            return False
        rec = dict(rec)
        rec["filename"] = dest.name
        rec["bytes"] = dest.stat().st_size
        rec["status"] = "ok"
        records.append(rec)
        print(f"  OK {rec['bytes']}")
        return True

    idx = 1
    for rec in REPORTS:
        if idx > 50:
            break
        if add_downloaded(rec, idx):
            seen_ids.add(rec["id"])
            idx += 1
        time.sleep(0.2)

    # Prefer V2G first so the set is project-shaped, then fill with RAG.
    queue: list[tuple[str, str]] = [("v2g", i) for i in ARXIV["v2g"]] + [("rag", i) for i in ARXIV["rag"]]
    for theme, aid in queue:
        if idx > 50:
            break
        ident = f"arxiv:{aid}"
        if ident in seen_ids:
            continue
        meta = arxiv_meta(aid)
        time.sleep(0.4)
        if not meta or not meta.get("title"):
            print(f" skip meta {aid}")
            continue
        rec = {
            "id": ident,
            "title": meta["title"],
            "year": meta["year"],
            "theme": theme,
            "source": "arXiv",
            "url": f"https://arxiv.org/pdf/{aid}.pdf",
            "abstract": meta.get("abstract"),
        }
        if add_downloaded(rec, idx):
            seen_ids.add(ident)
            idx += 1
        time.sleep(0.2)

    with (OUT / "catalog.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["filename", "title", "year", "theme", "source", "id", "url", "bytes", "status"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(records)
    (OUT / "catalog.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"TOTAL {len(records)}")


if __name__ == "__main__":
    main()
