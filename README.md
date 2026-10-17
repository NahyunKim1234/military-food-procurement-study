# Bid Participation and Price Distribution in Military Food Procurement

An exploratory study of 35 South Korean military food-purchase tenders opening in 2024-2025, with 5,458 submitted bid records. The package reproduces the paper's descriptive numerical results and figure; it does not establish causal savings.

## Read the study

- [Read the paper (PDF)](paper.pdf): five-page A4 English exploratory paper.
- `PAPER.md`: editable paper text.
- `results/summary.json`: headline statistics and sensitivity checks.
- `figures/participation_prices.png`: publication-resolution figure.

## Reproduce

Use Python 3.12 (the tested version) in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analysis.py
```

This reads the included tables and writes `results/summary.json`, `results/tender_metrics.csv` and the figure. No API key, account or network connection is needed after dependencies are installed. The script checks tender totals, bid totals, award identities, within-tender bidder uniqueness and headline coefficients.

Optionally rebuild the paper after the analysis:

```bash
python build_paper.py
```

The paper layout uses ReportLab and embedded DejaVu fonts available with Matplotlib. `build_paper.py` contains the editable narrative and tables. If the data or methods change, update narrative statistics as well as rerunning the analysis: narrative tables are intentionally reviewed text, not automatically generated conclusions.

## Data and audit scope

`data/tenders.csv` has 35 tender rows. `data/bids.csv` has 5,458 bid rows with stable opaque bidder labels. `data/soy_notice_metadata.csv` contains selected metadata for the two soy-sauce notices. See `DATA_DICTIONARY.md` for field definitions.

The original private archive was reconciled against 78 XML bidder pages across eight key fields. The uploaded summary, bidder CSVs and source XML agreed on the 35 selected tenders. Source-archive SHA-256 values are in `data/provenance.json`. This package contains curated data, not those original archives; independent repetition of the original XML audit requires the researcher-held source files. A checksum alone does not grant access to a source file or prove source accuracy.

Business identifiers and names, representatives, staff contacts, submission timestamps and credentials are not included. Opaque bidder codes preserve cross-tender overlap. This is pseudonymization, not guaranteed anonymization: public tender and amount combinations may be linkable to source records. No individual firm is accused of misconduct.

## Interpret the results

The units of analysis are tenders, not 5,458 independent observations. Tender names are not proof of matching goods or delivery conditions. Ranked, nonexcluded records are not proof of final qualification. The fixed-subset diagnostic samples from already observed ranked bids; it is not an experiment in reducing actual competition. The 20-participant descriptive threshold and case selection were not preregistered.

## Researcher and tool roles

The researcher directed the inquiry, operated the portal and collection scripts, provided saved responses, and reviewed and discussed results. ChatGPT supported programming, reconciliation, statistical analysis, chart generation and English drafting. Do not represent this repository as entirely independent coding or analysis. See the disclosure in the paper; the researcher must review it before actual submission.

## GitHub or portfolio use

The directory is ready to upload into a researcher-owned repository. Choose a repository name such as `military-food-procurement-study`; add the researcher's name and an appropriate license decision before public publication. Use the actual repository URL in the accompanying portfolio description. The PDF can be opened through the link above.

The primary data portals describe unrestricted use of their API data. That does not automatically select a software license for this repository. All publication decisions remain with the researcher.

## Sources

1. DAPA Bid Results Information_GW: https://www.data.go.kr/data/15158417/openapi.do
2. DAPA Bid Notices Information_GW: https://www.data.go.kr/data/15158416/openapi.do
3. Electronic bidding rules, Article 16, effective 2025-04-16: https://www.law.go.kr/LSW/admRulInfoP.do?admRulSeq=2100000257968

Data snapshot: 2026-10-12. Manuscript revision: 2026-10-18. The sample is purposeful and not a census of all military or public procurement.
