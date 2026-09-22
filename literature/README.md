# V2G Intelligence Platform — literature corpus (50 open-access PDFs)

Local copies of **50** open-access papers and public reports for the Fuse V2G Intelligence capstone literature review.

These are **author-accepted / preprint / public-agency** PDFs only (arXiv, MDPI OA, IESO, UBC). Paywalled publisher PDFs were not downloaded.

## Layout

- `pdfs/` — 50 PDF files, numbered `01`–`50`
- `catalog.csv` / `catalog.json` — title, year, theme, source, URL
- `download_articles.py` — re-download script (curl-based)

## Mix

- **v2g**: 35
- **rag**: 11
- **canada-pilot**: 1
- **canada-policy**: 1
- **canada-vgi**: 1
- **v2g-market**: 1

## How to use in the lit-review chapter

1. Start with Canada/policy items (`01`–`04`) plus the V2G reviews (`04`, `09`).
2. Use ISO 15118 / CCS security papers (`26`–`28`, `38`–`39`) as the *standards-and-trust* strand, not as the core of the chapter.
3. Use `41` (GridCodex) plus `42`–`50` (RAG surveys, citations, RAPTOR, failure points) to justify the retrieval assistant.
4. Skip deep optimal-control / battery-circuit papers except as *barrier* citations (degradation, frequency regulation).

## Catalog

| # | Year | Theme | Title | Source |
|---|------|-------|-------|--------|
| 01 | 2025 | canada-vgi | Barriers and Opportunities to Energy Sharing Between Vehicles and Buildings During an Emergency, and Vehicles and Grids at Other Times | `ubc-walgama-2025` |
| 02 | 2024 | canada-pilot | Optimal Vehicle to Grid Charging System Considering Solar, Storage, and User Privacy (IESO Grid Innovation Fund final report) | `ieso-gif-sky-clean` |
| 03 | 2025 | canada-policy | Memorandum on Consideration of Bidirectional Charging in Local Achievable Potential Studies for Toronto and Ottawa | `ieso-v2g-memo-2025` |
| 04 | 2024 | v2g-market | Feasibility and Challenges for Vehicle-to-Grid in Electricity Market: A Review | `doi:10.3390/en17030679` |
| 05 | 2025 | v2g | Electric Vehicle Scheduling and Vehicle-to-Grid Integration in Microgrids | `arxiv:2508.06752` |
| 06 | 2020 | v2g | Reliable Frequency Regulation through Vehicle-to-Grid: Encoding Legislation with Robust Constraints | `arxiv:2005.06042` |
| 07 | 2021 | v2g | A Comprehensive Electric Vehicle Model for Vehicle-to-Grid Strategy Development | `arxiv:2110.12225` |
| 08 | 2025 | v2g | Online Aging-Aware Energy Optimization for Vehicle-Home-Grid Integration | `arxiv:2504.09657` |
| 09 | 2021 | v2g | Niche to normality -- an interdisciplinary review of Vehicle-to-Grid | `arxiv:2106.05837` |
| 10 | 2023 | v2g | Vehicle-to-grid plug-in forecasting for participation in ancillary services markets | `arxiv:2307.07399` |
| 11 | 2023 | v2g | Vehicle-to-Grid and ancillary services:a profitability analysis under uncertainty | `arxiv:2309.11118` |
| 12 | 2023 | v2g | Vehicle-to-Grid Fleet Service Provision considering Nonlinear Battery Behaviors | `arxiv:2301.12041` |
| 13 | 2024 | v2g | Vehicle-to-Grid Technology meets Packetized Energy Management: A Co-Simulation Study | `arxiv:2406.19296` |
| 14 | 2025 | v2g | Assessment of Quantitative Cyber-Physical Reliability of SCADA Systems in Autonomous Vehicle to Grid (V2G) Capable Smart Grids | `arxiv:2507.21154` |
| 15 | 2016 | v2g | A multi-layer market for vehicle-to-grid energy trading in the smart grid | `arxiv:1609.01437` |
| 16 | 2016 | v2g | Profit-aware Online Vehicle-to-Grid Decentralized Scheduling under Multiple Charging Stations | `arxiv:1607.06906` |
| 17 | 2024 | v2g | Addressing Trust Issues for Vehicle to Grid in Distributed Power Grids Using Blockchains | `arxiv:2407.16180` |
| 18 | 2014 | v2g | Capacity Estimation for Vehicle-to-Grid Frequency Regulation Services with Smart Charging Mechanism | `arxiv:1410.1282` |
| 19 | 2021 | v2g | Using Mobility Patterns for the Planning of Vehicle-to-Grid Infrastructures that Support Photovoltaics in Cities | `arxiv:2112.15006` |
| 20 | 2017 | v2g | Coordinated Autonomous Vehicle Parking for Vehicle-to-Grid Services: Formulation and Distributed Algorithm | `arxiv:1701.01527` |
| 21 | 2022 | v2g | A Reinforcement Learning Approach for Electric Vehicle Routing Problem with Vehicle-to-Grid Supply | `arxiv:2204.05545` |
| 22 | 2021 | v2g | Autonomous Vehicle-to-Grid Design for Provision of Frequency Control Ancillary Service and Distribution Voltage Regulation | `arxiv:2101.10518` |
| 23 | 2024 | v2g | Impact of Flexible and Bidirectional Charging in Medium- and Heavy-Duty Trucks on California's Decarbonization Pathway | `arxiv:2401.10194` |
| 24 | 2020 | v2g | Integrating Battery Aging in the Optimization for Bidirectional Charging of Electric Vehicles | `arxiv:2009.12201` |
| 25 | 2022 | v2g | Potentials of Electric Vehicles for the Provision of Active and Reactive Power Flexibilities as Ancillary Services at Vertical Power System Interconnections | `arxiv:2210.10522` |
| 26 | 2024 | v2g | Self-Sovereign Identity for Electric Vehicle Charging | `arxiv:2403.06632` |
| 27 | 2022 | v2g | EVExchange: A Relay Attack on Electric Vehicle Charging System | `arxiv:2203.05266` |
| 28 | 2024 | v2g | Current Affairs: A Security Measurement Study of CCS EV Charging Deployments | `arxiv:2404.06635` |
| 29 | 2020 | v2g | Distributed Vehicle Grid Integration Over Communication and Physical Networks | `arxiv:2008.08939` |
| 30 | 2021 | v2g | Learning to Operate an Electric Vehicle Charging Station Considering Vehicle-grid Integration | `arxiv:2111.01294` |
| 31 | 2025 | v2g | Dynamic Incentive Strategies for Smart EV Charging Stations: An LLM-Driven User Digital Twin Approach | `arxiv:2504.01423` |
| 32 | 2025 | v2g | An Integrated Optimization Framework for Smart Charging of Electric Bus Fleets under Dynamic Electricity Prices with On-Site Solar Generation, Energy Storage, and V2G operations | `arxiv:2509.05940` |
| 33 | 2024 | v2g | EnergAIze: Multi Agent Deep Deterministic Policy Gradient for Vehicle to Grid Energy Management | `arxiv:2404.02361` |
| 34 | 2018 | v2g | Engineering and Economic Analysis for Electric Vehicle Charging Infrastructure --- Placement, Pricing, and Market Design | `arxiv:1808.03897` |
| 35 | 2022 | v2g | Value of Optimal Trip and Charging Scheduling of Commercial Electric Vehicle Fleets with Vehicle-to-Grid in Future Low Inertia Systems | `arxiv:2204.11565` |
| 36 | 2024 | v2g | Co-Optimization of EV Charging Control and Incentivization for Enhanced Power System Stability | `arxiv:2405.00947` |
| 37 | 2024 | rag | HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models | `arxiv:2405.14831` |
| 38 | 2025 | v2g | Streamlining Plug-and-Charge Authorization for Electric Vehicles with OAuth2 and OIDC | `arxiv:2501.14397` |
| 39 | 2022 | v2g | Brokenwire : Wireless Disruption of CCS Electric Vehicle Charging | `arxiv:2202.02104` |
| 40 | 2017 | v2g | Distributed Optimal Vehicle Grid Integration Strategy with User Behavior Prediction | `arxiv:1703.04552` |
| 41 | 2025 | rag | GridCodex: A RAG-Driven AI Framework for Power Grid Code Reasoning and Compliance | `arxiv:2508.12682` |
| 42 | 2023 | rag | Retrieval-Augmented Generation for Large Language Models: A Survey | `arxiv:2312.10997` |
| 43 | 2024 | rag | Evaluation of Retrieval-Augmented Generation: A Survey | `arxiv:2405.07437` |
| 44 | 2024 | rag | Retrieval-Augmented Generation for Natural Language Processing: A Survey | `arxiv:2407.13193` |
| 45 | 2024 | rag | On the Capacity of Citation Generation by Large Language Models | `arxiv:2410.11217` |
| 46 | 2023 | rag | Enabling Large Language Models to Generate Text with Citations | `arxiv:2305.14627` |
| 47 | 2020 | rag | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | `arxiv:2005.11401` |
| 48 | 2024 | rag | RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval | `arxiv:2401.18059` |
| 49 | 2024 | rag | Seven Failure Points When Engineering a Retrieval Augmented Generation System | `arxiv:2401.05856` |
| 50 | 2024 | rag | A Survey on RAG Meeting LLMs: Towards Retrieval-Augmented Large Language Models | `arxiv:2405.06211` |

## Notes

- CSA Group *Charging Ahead* (public report) returned HTTP 403 from this environment; cite from the landing page if needed: https://www.csagroup.org/article/research/charging-ahead-unlocking-vehicle-grid-integration-in-canada
- NRCan *What we heard* PDF URL was not stable (404); use the HTML: https://natural-resources.canada.ca/climate-change/what-heard-nrcas-request-information-grid-readiness-electric-vehicles
