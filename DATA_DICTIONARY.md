# Curated data dictionary

All money values are Korean won. Dates are strings in YYYYMMDD format; identifiers remain strings. A percentage-point gap is distinct from a percentage change in money.

## data/tenders.csv

| Field | Definition |
|---|---|
| event_id | Demand year, agency code, decision number, opening date and notice order joined by underscores. |
| announcement_id | Source notice code; may be reused across years or procurement types. |
| announcement_name_ko | Source Korean tender title, retained as evidence of scope; not a product-specification match. |
| agency | SCP, HCM or MCS. |
| opening_date | Actual opening date; use its first four digits for analysis year. |
| demand_year | Source administrative identifier; can differ from opening year. |
| award_floor_pct | Tender-specific lower award rate, expressed in percent, e.g. 87.995. |
| base_amount_krw | Basic preliminary/base amount; not the budget or reconstructed estimate. |
| selected_price_mean_before_rounding_krw | Exact mean of four preliminary prices marked selected. |
| award_amount_krw | Amount for the record marked awarded. |
| contract_method | general or restricted, mapped from the result metadata. |
| record_count | Submitted bidder records within the tender. |

## data/bids.csv

| Field | Definition |
|---|---|
| event_id | Join key to the tender table. |
| bidder_id | Stable opaque label generated from distinct source business identifiers; the mapping is not supplied. |
| amount_krw | Submitted total bid amount. |
| display_rate_pct | API's displayed bid rate, preserved as a source value; calculations use amounts and the reconstructed estimate. |
| display_rank | API rank string, potentially blank. A rank is not proof of qualification. |
| status | awarded, invalid, below_floor, above_estimate, ranked or unclassified; derived from the source result marker and note. |
| awarded | 1 for the single marked award, otherwise 0. |
| ranked_nonexcluded | 1 when a numeric rank or award marker is present and the note is not invalid, below-floor or above-estimate. |

`status` records the source note category. A submission can have a computed negative price gap but be labeled invalid rather than below_floor. There are 116 such records; do not relabel them as a data error. Ten invalid records had numeric ranks and are excluded from ranked_nonexcluded.

## data/soy_notice_metadata.csv

Selected notice fields: announcement identifier, source Korean competition method, source Korean license list, budget, publication date and the two submission deadlines. The license-list joining syntax does not establish whether licenses are alternatives or joint requirements. Product quantities and original attachments were unavailable.

## Analysis outputs

The reconstructed estimate is the selected-price mean truncated below one won. Bid gap in pp is `100 * amount / estimate - award_floor_pct`. `median_all`, `median_noninvalid` and `median_ranked` are tender-level medians. Quantiles use NumPy's linear interpolation. `selection_difference_krw` is the award minus the minimum ranked, nonexcluded amount; it is not estimated waste or obtainable savings.

Partial rank correlations residualize average ranks against agency, floor-rate category, base-amount rank and opening year, with an intercept. No causal interpretation or independent-observation claim is attached.
