# Authoritative OSH Data Inventory for a Predictive AI / Exploratory Analytics Project

## Executive summary

The strongest foundation for a serious portfolio project is **U.S. OSHA data rather than UK HSE data**, because OSHA currently exposes several large, incident- or sample-level public datasets that can be downloaded directly without authentication. OSHA's Injury Tracking Application alone reported **392,735 establishment submissions and 1,478,310 recordable cases for calendar year 2024**, while its case-detail collection contained **688,575 incident reports** in the 2024 report snapshot. citeturn5view0turn22view0

For a genuinely predictive—not merely post-incident classification—project, my strongest recommendation is **OSHA Severe Injury Reports + BLS QCEW employment data**, aggregated into industry–geography–time cells and used to forecast future severe-injury burden from lagged historical information. OSHA's ITA Case Detail dataset is the richest alternative for incident-level ML/NLP and explainability, while the OSHA Chemical Exposure dataset offers an unusually deep industrial-hygiene regression project spanning 1984 onward. citeturn17view4turn19view2turn19view3

The UK HSE sources are excellent official statistics and openly licensed under the **Open Government Licence v3.0**, but the readily downloadable RIDDOR/LFS products I found are primarily published statistical tables rather than a comparable 100k+ row-level incident microdataset. They are therefore better suited to external context, benchmark visualizations, or a separate epidemiological analysis than to our main one-shot predictive ML project. citeturn18view2turn19view1turn16search2

For U.S. federal datasets, government works are generally in the U.S. public domain; Data.gov's official licensing guidance states that works created by federal employees within their employment default to the U.S. Public Domain. OSHA's ITA user guidance additionally states that anyone may use the ITA data. citeturn21search0turn4view4

## Prioritized dataset inventory

| Priority | Dataset | Publisher | Access / API | Unit, coverage, scale | Key variables / documentation | Usage and important limitations |
|---|---|---|---|---|---|---|
| **A+** | **Injury Tracking Application — Case Detail** | U.S. OSHA | Landing page: `https://www.osha.gov/itadata`  • 2024 ZIP: `https://www.osha.gov/sites/default/files/ITA_Case_Detail_Data_2024_through_12-31-2025.zip` • 2023 ZIP: `https://www.osha.gov/sites/default/largefiles/ITA_Case_Detail_Data_2023_through_12-31-2023OIICS.zip` • no auth/API required | **One recordable injury/illness case per row.** Case detail begins with 2023 incidents; OSHA's 2024 report counted **688,575 incident reports** as of May 31, 2025. U.S.; federal and State Plan establishments that submit to ITA. Posted ZIP size is not stated on the landing page. citeturn22view0turn5view0 | Establishment/industry/size, date/time, case outcome, job description, SOC, five redacted narrative fields, and AI-generated OIICS nature/body/event/source codes. Current dictionary: `https://www.osha.gov/sites/default/files/case_detail_data_dictionary_2026.pdf` citeturn5view3turn22view0 | **Best incident-level ML dataset.** Major leakage risk: days-away counts, outcome fields, death date, narratives describing consequences, and OIICS injury/body/nature features may reveal the target. Public fields also omit some attributes OSHA uses internally, including worker age and sex. ITA is not representative of all U.S. workers because submission requirements depend on establishment size and industry. citeturn4view4turn22view0 |
| **A+** | **Injury Tracking Application — OSHA 300A Summary** | U.S. OSHA | 2024 ZIP: `https://www.osha.gov/sites/default/files/ITA_300A_Summary_Data_2024_through_12-31-2025.zip` • 2023 ZIP: `https://www.osha.gov/sites/default/files/ITA_300A_Summary_Data_2023_through_12-31-2024.zip` • landing page contains 2016–2025 files; no auth | **Establishment-year.** Summary collection starts in 2016. OSHA reports **392,735 establishments** submitted 2024 summary data, covering about **1.48M cases**. A combined 2016–2024 file should therefore be comfortably million-row scale, although the exact concatenated count should be computed rather than assumed. citeturn22view0turn5view0 | Establishment, NAICS, state/location, annual average employment, hours worked, deaths, DAFW/DJTR/other cases, injury categories. Dictionary: `https://www.osha.gov/sites/default/files/summary_data_dictionary.pdf` citeturn5view2 | Excellent for longitudinal EDA and rates. OSHA explicitly warns it does not validate reported employee or injury counts and that high/low rates alone should not be interpreted as “most/least dangerous.” `establishment_id` links summary to case detail within submitted data, but may not reliably identify the same establishment longitudinally if profiles change. citeturn22view0turn4view4 |
| **A** | **Severe Injury Reports — SIR** | U.S. OSHA | Dashboard: `https://www.osha.gov/severe-injury-reports` • full ZIP currently linked as `https://www.osha.gov/sites/default/files/January2015toNovember2025.zip` • no auth | **One severe-injury report/event.** Coverage begins Jan. 1, 2015. Severe injury means inpatient hospitalization, amputation, or loss of an eye. The downloadable dashboard snapshot runs through Nov. 30, 2025. OSHA's 2024 annual report alone counted **9,034 reports**; across a decade the corpus is therefore on the order of \(10^5\), but the exact current total should be measured after download. citeturn17view4turn19view4turn2search22 | Event date, NAICS, establishment/location, incident description, OIICS categories, geocodes and severe-injury type. The dashboard itself provides a small record preview with event date, NAICS, city, state and establishment name. citeturn17view4 | **Excellent for longitudinal/spatial forecasting.** Critical limitation: only incidents under **federal OSHA jurisdiction**; State Plan jurisdiction incidents are excluded, and fatalities are not part of this dashboard. OSHA also cautions that third-party geocodes vary in precision. citeturn19view4turn17view4 |
| **A** | **Chemical Exposure Health Data / OSHA Health Samples** | U.S. OSHA | Page: `https://www.osha.gov/opengov/health-samples` • full file: `https://www.osha.gov/sites/default/files/healthsamples.zip` • **93 MB compressed**; no auth | **One industrial-hygiene sample.** 1984–2026 files are published, with full multi-decade data available as a 93 MB ZIP. Exact record count is not stated on the page and should be calculated after parsing. citeturn19view3 | Inspection number, establishment, location, SIC/NAICS, sample number/type, date, instrument, duration, air volume, IMIS substance code/name, result, unit, qualifier. Dictionary: `https://www.osha.gov/opengov/osha-health-samples-dataset-field-definitions` citeturn11view1turn19view3 | Very strong for advanced regression/exposure modeling. But it is **not a random worker-exposure sample**: OSHA inspections target particular establishments/industries and may emphasize worst-case exposures. Individual measurements also are not automatically comparable with an 8-hour PEL unless sampling design/duration supports that comparison. citeturn19view3 |
| **A as auxiliary** | **Quarterly Census of Employment and Wages — QCEW** | U.S. Bureau of Labor Statistics | Main: `https://www.bls.gov/cew/` • open-data docs: `https://www.bls.gov/cew/additional-resources/open-data/home.htm` • 2024 annual file: `https://data.bls.gov/cew/data/files/2024/csv/2024_annual_singlefile.zip` • no auth | Aggregate **area × industry × ownership × period** data. QCEW covers **more than 95% of U.S. jobs**, with county/MSA/state/national industry data; NAICS files go back to 1990, with earlier limited files. The full annual single file is large and its row count varies by year. citeturn15search3turn17view1 | Employment, establishment counts, wages, geography/FIPS, NAICS, ownership, quarter/year. File layouts/data guide are linked from the official download page. citeturn17view1turn19view2 | Not an OSH-outcome dataset by itself; **extremely valuable denominator/exposure data** for OSHA joins. This is what lets us avoid treating “more injuries” as automatically meaning “higher risk” simply because an industry employs more people. citeturn15search35turn19view2 |
| **B / benchmark** | **Survey of Occupational Injuries and Illnesses — SOII / Census of Fatal Occupational Injuries — CFOI** | U.S. BLS | `https://www.bls.gov/iif/` • Public Data API: `https://api.bls.gov/publicAPI/v2/timeseries/data/` | Official annual statistical estimates. For 2024 BLS reported about **2.488 million private-industry nonfatal cases** and **5,070 fatal work injuries**. These are statistical estimates/counts, not millions of downloadable incident-level microrecords. citeturn14view0 | Injury rates/counts by industry, case type and other published dimensions; series can be retrieved through BLS data tools/API. BLS API v1 can be used without registration; v2 supports registration for expanded limits/features. citeturn14view1 | Best as a **national benchmark/external sanity check**, not the primary ML training table. OSHA itself recommends BLS SOII when the goal is generalizable population-level injury rates because ITA is selectively collected. citeturn22view0 |
| **B–C / UK benchmark** | **RIDDOR Official Statistical Tables** | UK Health and Safety Executive | Index: `https://www.hse.gov.uk/statistics/tables/index.htm` • history: `https://www.hse.gov.uk/statistics/assets/docs/ridhist.xlsx` • detailed industry: `https://www.hse.gov.uk/statistics/assets/docs/ridind.xlsx` • region: `https://www.hse.gov.uk/statistics/assets/docs/ridreg.xlsx` • accident type: `https://www.hse.gov.uk/statistics/assets/docs/ridkind.xlsx` | **Aggregated published tables**, not open row-level RIDDOR incident microdata. Historical tables run back to **1974** for fatal/nonfatal injury series; tables include industry, region, age/sex, accident kind, injury nature/site and dangerous occurrences. citeturn18view2 | RIDDOR fatal/nonfatal injury counts and rates across industry/geography/demographics; documentation/source caveats at `https://www.hse.gov.uk/statistics/sources.htm`. citeturn19view0turn18view2 | Open under **OGL v3.0** unless otherwise stated. Reporting rules changed over time—for example, over-7-day reporting replaced over-3-day reporting in 2012 and RIDDOR categories changed in 2013—so long time-series modeling requires structural-break handling. citeturn19view0turn16search2 |
| **C / UK contextual** | **HSE Labour Force Survey OSH tables** | UK HSE / source survey run by ONS | `https://www.hse.gov.uk/statistics/lfs/index.htm` | Published estimates/tables based on a national survey of roughly **31,000 households each quarter**; injury questions have been collected annually since 1993/94 and ill-health questions mostly annually since 2001/02. citeturn19view0turn19view1 | Self-reported workplace injuries, work-related illness, days lost, occupation/industry and population rates in published tables. citeturn19view0 | Excellent population context and a useful counterpoint to mandatory-reporting data; not a frictionless 100k+ open microrecord ML source from the HSE site. OGL v3.0 applies to HSE-published content unless otherwise stated. citeturn19view1 |

**Bottom line on the UK:** HSE provides unusually strong official tables and documentation, but for the particular goal of a **large, one-shot, row-level predictive portfolio project**, the U.S. OSHA sources are materially easier to operationalize. citeturn18view2turn22view0

## Recommended project directions

### Best overall — Severe-injury burden forecasting with OSHA SIR + BLS QCEW

This is the one I would choose for the portfolio.

**Working project title**

> **Can historical safety signals tell us where severe-injury burden may rise next?**

Instead of taking a post-accident record and asking whether it was severe—an easy way to produce leakage—we aggregate OSHA Severe Injury Reports into something like:

```text
STATE / REGION
×
NAICS 2- or 3-digit INDUSTRY
×
QUARTER
```

Then join each cell to BLS QCEW employment and establishment counts and predict the **next quarter's severe-injury count or burden** using only information available before that future quarter. SIR supplies more than a decade of severe-event history; QCEW supplies broad employment/exposure context and is downloadable programmatically. citeturn17view4turn19view2

A possible modeling table:

```text
state
naics2
year
quarter

employment
establishments
avg_weekly_wage

sir_count_t
sir_count_t_minus_1
sir_count_t_minus_2
sir_count_rolling_4q
sir_count_same_quarter_last_year

industry_trend
state_trend
quarter_sin
quarter_cos

TARGET:
sir_count_next_quarter
```

A statistically serious version would compare a **naive lag baseline**, Poisson or negative-binomial model, and gradient-boosted count model. If you model counts, employment can serve as exposure/context; if you create rates, denominator compatibility must be checked carefully because SIR covers federal OSHA jurisdiction rather than every worker represented in QCEW. citeturn17view4turn15search3

**Why this is the strongest portfolio story:** it is truly forward-looking, naturally time-split, supports geographic and industry visualizations, avoids the worst post-outcome leakage problem, and gives us a legitimate reason to combine multiple official government sources.

**Main caveat:** do not call the forecast “the probability a worker will be injured.” It is a forecast of **reported severe-injury burden in the observed OSHA surveillance system**, subject to federal-jurisdiction coverage and reporting limitations. citeturn19view4

### Strongest incident-level AI — ITA Case Detail + Summary

This gives us the richest dataset and the biggest “AI” canvas. OSHA's 2024 case-detail collection alone contained roughly 689k reports in the published annual snapshot, including occupational codes, temporal information, narratives and standardized OIICS classifications. citeturn5view0turn22view0

A defensible project could deliberately create **two model tracks**:

```text
TRACK A — STRICT / PRE-OUTCOME MODEL

industry
state
establishment size
employment
hours
occupation / SOC
calendar / time variables

→ predict DAFW or another severity class
```

and:

```text
TRACK B — POST-INCIDENT TRIAGE / NLP MODEL

Track A variables
+
event narrative
+
job description
+
selected event-context fields

→ classify expected severity / case type
```

That separation itself becomes a great portfolio artifact:

> **What the model is allowed to know changes what the model is allowed to claim.**

The strict model must exclude variables that directly encode the consequence, such as `dafw_num_away`, `djtr_num_tr`, `date_of_death`, the target outcome itself, and likely many injury/body/nature descriptors if the target is severity. OSHA also warns ITA is selective rather than population-representative. citeturn5view3turn22view0

This is best if you want:

**classification + NLP + SHAP + leakage audit + calibration + fairness/subgroup/error analysis**.

### Most technically distinctive — Industrial-hygiene exposure modeling

The Chemical Exposure Health Data would make the portfolio unusually sophisticated because it is not the generic accident-classification project everybody builds. OSHA publishes sample-level industrial hygiene data from 1984 onward, including industry, substance, sample type, instrument, duration, volume, result and qualifiers; the complete compressed dataset is 93 MB. citeturn19view3turn11view1

A defensible prediction could be:

> **Given information available when an industrial-hygiene sample is planned, what range of measured airborne concentration should we expect?**

Possible target:

```text
log(sample_result)
```

with modeling performed within compatible substance/unit groups.

A more ambitious classification target is:

```text
measured_exposure_above_applicable_reference_level
```

but only after building strict rules around sampling duration, units and the relevant standard. OSHA explicitly says individual samples are not necessarily directly comparable to PELs, while a proper full-shift integrated 8-hour sample can be compared to an 8-hour TWA standard. citeturn19view3

That caveat is exactly why this project would look serious rather than Kaggle-like.

## Defensible joins and prediction targets

### High-value joins

| Join | Keys | Feasibility | What it adds |
|---|---|---:|---|
| **ITA Case Detail ↔ ITA Summary** | `establishment_id` + filing/year context | **Very high** | Establishment-level denominator and summary context around incident cases. OSHA explicitly documents `establishment_id` linkage. citeturn22view0 |
| **SIR ↔ BLS QCEW** | state/county geography + NAICS level + year/quarter | **High after aggregation** | Employment/establishment exposure context; enables industry/geography forecasting rather than raw event counts. QCEW publishes these dimensions. citeturn17view4turn15search35 |
| **ITA aggregate ↔ BLS QCEW** | state + NAICS + year | **High after aggregation** | Compare reported OSHA burden against labor-market scale; useful for industry-normalized EDA. |
| **Chemical samples ↔ OSHA enforcement/inspection data** | OSHA `Inspection_Number` | **Conceptually high** | Adds inspection type, enforcement and violation context. OSHA's public data catalog includes inspection/enforcement data and the health-sample dictionary contains inspection number. citeturn3view2turn11view1 |
| **SIR ↔ ITA** | geography + establishment name/address/NAICS + date window | **Low–medium** | Interesting validation/context, but no documented universal stable case key. Treat as probabilistic entity resolution, not an exact relational join. |
| **HSE RIDDOR ↔ UK employment denominators** | industry/region/year | **Medium at aggregate level** | Rates/trends for UK benchmarking; not needed for the first project. citeturn18view2 |

A key warning with ITA longitudinal joins: OSHA says `establishment_id` can change if an establishment creates another profile, so it should not blindly be treated as a permanent establishment identifier across years. citeturn4view4

### Prediction targets worth considering

**Recommended target:**

```text
NEXT-QUARTER SEVERE-INJURY COUNT
for state × NAICS industry cells
```

Features:

```text
lagged SIR counts
rolling 4-quarter counts
same quarter previous year
employment
establishment count
wage / industry indicators
seasonality
region
industry
```

Leakage risk: **low**, provided all features are shifted so quarter \(t+1\) is predicted strictly from information available through quarter \(t\).

A second option:

```text
NEXT-QUARTER ELEVATED-BURDEN FLAG
1 = future count/rate exceeds a predefined historical percentile
0 = otherwise
```

Leakage risk: **low–medium**. The threshold must be fitted on training data only; calculating the percentile using future/test periods would leak information.

For ITA:

```text
DAFW vs NON-DAFW CASE
```

Leakage risk: **high unless disciplined**. Never include days-away counts, final case outcome, death information or descriptors that are effectively consequence labels. Narratives require special review because many explicitly describe injury severity. citeturn5view3

For chemical exposure:

```text
LOG MEASURED CONCENTRATION
```

Leakage risk: **low** if result/qualifier and post-lab variables are removed. Selection bias remains substantial because OSHA sampling is targeted rather than representative. citeturn19view3

For SIR incident records:

```text
AMPUTATION vs HOSPITALIZATION vs EYE LOSS
```

This is technically easy but **not my preferred portfolio target**. Once the incident description is known, this becomes post-event classification rather than preventive prediction. OSHA defines SIR itself around these already-realized severe outcomes. citeturn17view4

## Ready-to-run Colab retrieval recipes

None of the OSHA/HSE static downloads below requires an API key. BLS QCEW static files also require no authentication; the general BLS Public Data API can be used without registration under its basic access mode, while registration is available for the higher-capability API workflow. citeturn14view1turn19view2

### Common Colab setup

```python
from pathlib import Path
import io
import os
import zipfile
import requests
import pandas as pd

ROOT = Path("/content/osh_predictive_project")
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
OUTPUT = ROOT / "outputs"

for p in [RAW, PROCESSED, OUTPUT]:
    p.mkdir(parents=True, exist_ok=True)

def download(url: str, filename: str) -> Path:
    """Download a public file and save it without modifying the source."""
    path = RAW / filename

    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    print(f"{filename}: {path.stat().st_size / 1e6:.1f} MB")
    return path


def inspect_zip(path: Path):
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            print(
                f"{info.filename:70s} "
                f"{info.file_size / 1e6:9.1f} MB uncompressed"
            )
```

This automatically gives us the actual file size rather than relying on stale website metadata.

### OSHA ITA Case Detail

```python
ITA_CASE_2024 = (
    "https://www.osha.gov/sites/default/files/"
    "ITA_Case_Detail_Data_2024_through_12-31-2025.zip"
)

case_zip = download(ITA_CASE_2024, "ita_case_detail_2024.zip")
inspect_zip(case_zip)

with zipfile.ZipFile(case_zip) as z:
    csv_names = [
        n for n in z.namelist()
        if n.lower().endswith(".csv")
    ]

    if not csv_names:
        raise RuntimeError("No CSV found in OSHA ITA ZIP.")

    print(csv_names)

    with z.open(csv_names[0]) as f:
        case_2024 = pd.read_csv(f, low_memory=False)

print(case_2024.shape)
display(case_2024.head())
display(case_2024.dtypes.to_frame("dtype"))
```

2023:

```python
ITA_CASE_2023 = (
    "https://www.osha.gov/sites/default/largefiles/"
    "ITA_Case_Detail_Data_2023_through_12-31-2023OIICS.zip"
)

case23_zip = download(ITA_CASE_2023, "ita_case_detail_2023.zip")
```

The direct URLs above are OSHA's current historical download links. citeturn23view1turn23view3

### OSHA ITA Summary

```python
ITA_SUMMARY_2024 = (
    "https://www.osha.gov/sites/default/files/"
    "ITA_300A_Summary_Data_2024_through_12-31-2025.zip"
)

summary_zip = download(
    ITA_SUMMARY_2024,
    "ita_summary_2024.zip"
)

inspect_zip(summary_zip)

with zipfile.ZipFile(summary_zip) as z:
    csv_names = [
        n for n in z.namelist()
        if n.lower().endswith(".csv")
    ]

    with z.open(csv_names[0]) as f:
        summary_2024 = pd.read_csv(f, low_memory=False)

print(summary_2024.shape)
display(summary_2024.head())
```

The current 2024 summary ZIP is the historical link exposed by OSHA's ITA page. citeturn23view0

Then test the documented join:

```python
print("case rows:", len(case_2024))
print("summary rows:", len(summary_2024))

common_ids = (
    set(case_2024["establishment_id"].dropna())
    & set(summary_2024["establishment_id"].dropna())
)

print("linked establishment IDs:", len(common_ids))
```

OSHA specifically documents `establishment_id` for summary-to-case-detail linkage. citeturn22view0

### OSHA Severe Injury Reports

```python
SIR_URL = (
    "https://www.osha.gov/sites/default/files/"
    "January2015toNovember2025.zip"
)

sir_zip = download(SIR_URL, "osha_sir_2015_2025.zip")
inspect_zip(sir_zip)

with zipfile.ZipFile(sir_zip) as z:
    names = z.namelist()
    print(names)

    # Robustly try tabular files.
    csv_names = [n for n in names if n.lower().endswith(".csv")]
    xlsx_names = [n for n in names if n.lower().endswith((".xlsx", ".xls"))]

    if csv_names:
        with z.open(csv_names[0]) as f:
            sir = pd.read_csv(f, low_memory=False)
    elif xlsx_names:
        with z.open(xlsx_names[0]) as f:
            sir = pd.read_excel(io.BytesIO(f.read()))
    else:
        raise RuntimeError(
            "Unexpected SIR archive format. Inspect ZIP contents above."
        )

print(sir.shape)
display(sir.head())
display(sir.isna().mean().sort_values(ascending=False).head(20))
```

OSHA's dashboard identifies this as the full SIR file for Jan. 2015 through Nov. 2025. citeturn17view4turn18view0

### BLS QCEW employment denominator

```python
QCEW_2024 = (
    "https://data.bls.gov/cew/data/files/2024/csv/"
    "2024_annual_singlefile.zip"
)

qcew_zip = download(QCEW_2024, "qcew_2024_annual.zip")
inspect_zip(qcew_zip)

with zipfile.ZipFile(qcew_zip) as z:
    csv_names = [n for n in z.namelist() if n.lower().endswith(".csv")]

    with z.open(csv_names[0]) as f:
        qcew_2024 = pd.read_csv(f, low_memory=False)

print(qcew_2024.shape)
display(qcew_2024.head())
```

That annual single-file endpoint is directly exposed by BLS's official QCEW download table; BLS also provides programmatic CSV slices by area and industry. citeturn25view0turn19view2

A multi-year downloader:

```python
def download_qcew_year(year: int) -> Path:
    url = (
        f"https://data.bls.gov/cew/data/files/{year}/csv/"
        f"{year}_annual_singlefile.zip"
    )
    return download(url, f"qcew_{year}_annual.zip")


qcew_files = {
    year: download_qcew_year(year)
    for year in range(2015, 2025)
}
```

For a quarterly SIR forecast, I would eventually use **quarterly QCEW files/slices**, not only the annual file. BLS documents CSV access by area, industry and time period. citeturn19view2

### OSHA Chemical Exposure Health Data

```python
CHEM_URL = (
    "https://www.osha.gov/sites/default/files/"
    "healthsamples.zip"
)

chem_zip = download(
    CHEM_URL,
    "osha_health_samples_1984_2026.zip"
)

inspect_zip(chem_zip)
```

OSHA says the archive contains data suitable for database import and that the complete file is roughly 93 MB compressed. citeturn19view3

Because the full source is XML-oriented and large, first inspect the archive rather than forcing `pandas.read_xml()` blindly:

```python
with zipfile.ZipFile(chem_zip) as z:
    xml_names = [
        n for n in z.namelist()
        if n.lower().endswith(".xml")
    ]
    print(xml_names[:20])
```

Then use streaming XML parsing for memory safety:

```python
from lxml import etree

def inspect_xml_structure(zip_path: Path, xml_name: str, max_events=30):
    with zipfile.ZipFile(zip_path) as z:
        with z.open(xml_name) as f:
            for i, (_, elem) in enumerate(
                etree.iterparse(f, events=("end",))
            ):
                if i >= max_events:
                    break

                print(
                    elem.tag,
                    list(elem.attrib.keys()),
                    (elem.text or "").strip()[:100]
                )
                elem.clear()

inspect_xml_structure(chem_zip, xml_names[0])
```

We should inspect the real schema first, then write the production parser around the actual record element.

### UK HSE RIDDOR tables

```python
HSE_FILES = {
    "history": (
        "https://www.hse.gov.uk/statistics/assets/docs/"
        "ridhist.xlsx"
    ),
    "industry": (
        "https://www.hse.gov.uk/statistics/assets/docs/"
        "ridind.xlsx"
    ),
    "region": (
        "https://www.hse.gov.uk/statistics/assets/docs/"
        "ridreg.xlsx"
    ),
    "accident_kind": (
        "https://www.hse.gov.uk/statistics/assets/docs/"
        "ridkind.xlsx"
    ),
}

for name, url in HSE_FILES.items():
    path = download(url, f"hse_riddor_{name}.xlsx")
    book = pd.ExcelFile(path)
    print(name, book.sheet_names)
```

These are the official HSE RIDDOR workbooks indexed by HSE's statistics site, which is licensed under OGL v3.0 unless otherwise stated. citeturn18view2turn24view0turn24view1turn24view2turn24view3

### Optional BLS API example

```python
import requests

endpoint = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

payload = {
    "seriesid": [
        # Insert verified IIF series IDs after selecting
        # the exact industry/rate measures needed.
    ],
    "startyear": "2020",
    "endyear": "2024",
}

# Add registrationkey only if using a registered BLS API key:
# payload["registrationkey"] = os.environ["BLS_API_KEY"]

if payload["seriesid"]:
    response = requests.post(
        endpoint,
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    bls_json = response.json()
    bls_json
```

I would not hard-code an arbitrary SOII series ID into the master notebook until the analytical industry/rate definition has been selected. BLS's Public Data API is official and programmatic, while SOII is best used here as a benchmark rather than our primary row-level ML source. citeturn14view1turn14view0

## Recommended analytical design and visual outputs

For the actual portfolio project, my preferred architecture is:

```text
OSHA SIR
incident-level severe injuries
2015–2025
        │
        ├── clean NAICS
        ├── clean geography
        ├── parse date
        └── aggregate
                ↓
       STATE × NAICS × QUARTER
                │
                │
BLS QCEW        │
employment ─────┤
establishments  │
wages           │
                ↓
       ANALYTICAL PANEL
                │
       lagged features only
                ↓
       ┌──────────────────┐
       │ BASELINE         │
       │ Previous quarter │
       └──────────────────┘
                ↓
       ┌──────────────────┐
       │ COUNT MODEL      │
       │ Poisson / NB     │
       └──────────────────┘
                ↓
       ┌──────────────────┐
       │ ML MODEL         │
       │ Gradient Boost   │
       └──────────────────┘
                ↓
       TEMPORAL HOLDOUT
                ↓
       EXPLAINABILITY
                ↓
       RISK / BURDEN MAP
                ↓
       DECISION SUPPORT
```

That design makes the prediction moment unambiguous:

> **At the end of quarter \(t\), use information available through quarter \(t\) to estimate reported severe-injury burden in quarter \(t+1\).**

That is far more defensible than predicting the severity of an accident after reading a narrative that already describes the injury.

### Visuals worth building

The first strong visual should be a **temporal ribbon / line chart** showing severe-injury reports by quarter, ideally split by major NAICS sector. A second should be a **state × industry heatmap** showing where reported burden concentrates. Because SIR does not provide nationwide State Plan coverage, maps must visually distinguish or explicitly filter the federal OSHA jurisdiction used in analysis. citeturn17view4

For modeling, create a **rolling temporal-validation diagram**, an **actual-vs-predicted time series**, a **predicted-vs-observed scatter/hexbin**, and a **top-decile lift chart** answering whether high-predicted-burden cells actually contain disproportionate future events. Count models should also get residual and calibration-style diagnostics appropriate to the target distribution.

For explainability, use **SHAP global importance**, dependence plots for lagged history/employment/industry effects, and 2–4 **local forecast explanations**:

```text
STATE × INDUSTRY
Manufacturing · Region X

Previous 4Q burden          ↑
Seasonal pattern            ↑
Employment base             ↑
Recent downward trend       ↓
────────────────────────────
Predicted next-quarter
burden: elevated
```

Interpret these strictly as **model contributions**, not causes.

For the final portfolio image, I would create:

```text
1,000s OF RAW REPORTS
        ↓
INDUSTRY × LOCATION × TIME
        ↓
LAGGED SAFETY SIGNALS
        ↓
FUTURE BURDEN FORECAST
        ↓
EXPLAINED RISK DRIVERS
        ↓
PRIORITIZED SURVEILLANCE
```

The headline could eventually become:

> **Can safety data tell us where to look earlier?**

But we should only finalize the portfolio wording **after seeing the actual out-of-time performance**.

### Recommended Colab structure

```text
/content/osh_predictive_project/

├── data/
│   ├── raw/
│   │   ├── osha_sir_2015_2025.zip
│   │   ├── qcew_2015_annual.zip
│   │   ├── ...
│   │   └── provenance.json
│   │
│   └── processed/
│       ├── sir_clean.parquet
│       ├── qcew_clean.parquet
│       ├── industry_quarter_panel.parquet
│       └── model_dataset.parquet
│
├── metadata/
│   ├── data_dictionary.csv
│   ├── source_registry.csv
│   ├── leakage_audit.csv
│   └── feature_dictionary.csv
│
├── models/
│   ├── naive_baseline.joblib
│   ├── negative_binomial/
│   └── gradient_boosting.joblib
│
├── tables/
│   ├── data_quality.csv
│   ├── model_comparison.csv
│   ├── temporal_validation.csv
│   └── subgroup_performance.csv
│
└── outputs/
    ├── 01_data_quality/
    ├── 02_temporal/
    ├── 03_industry/
    ├── 04_geography/
    ├── 05_model_performance/
    ├── 06_explainability/
    ├── 07_error_analysis/
    ├── 08_decision_support/
    └── 09_portfolio/
```

The **one-shot Colab is absolutely feasible**, but the right “complexity” is not throwing twenty algorithms at a CSV. The strongest version is complex because it combines **two official systems, temporal feature engineering, exposure adjustment, count modeling, ML comparison, out-of-time validation, explainability, error analysis, and geospatial decision visualization**—while keeping the prediction question simple and auditable.

For this portfolio, I would therefore lock the working direction as:

> **OSHA Severe Injury Reports + BLS QCEW**  
> **Spatiotemporal Forecasting of Future Severe-Injury Burden Across U.S. Industry–Geography Cells**

with **ITA Case Detail** retained as Plan B if initial SIR/QCEW harmonization reveals jurisdiction/denominator problems too severe for a defensible forecasting analysis.