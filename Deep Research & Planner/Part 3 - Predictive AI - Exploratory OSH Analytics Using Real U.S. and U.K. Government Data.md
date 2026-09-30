# Predictive AI / Exploratory OSH Analytics Using Real U.S. and U.K. Government Data

## Executive summary

The strongest project I found is **not** an OSHA incident-text classifier and not an LLM fine-tuning exercise. I recommend building a longitudinal **MSHA Mine-Quarter Risk Forecasting System** from several U.S. Mine Safety and Health Administration datasets.

The portfolio question would be:

> **Can historical operational, exposure, inspection, enforcement, and injury signals help identify mines with elevated injury risk in the next quarter?**

This is unusually strong for a portfolio because MSHA publishes separate but joinable datasets for accidents/injuries, quarterly employment and production, mine characteristics, inspections, and violations. The accident, employment/production, inspection, and violation series begin in 2000; the mines file covers mines under MSHA jurisdiction since 1970. MSHA explicitly documents `MINE_ID` as the common mine identifier and `EVENT_NO` as the inspections-to-violations join. The portal says its datasets are refreshed weekly. citeturn15view0turn14view1turn14view3turn14view5turn14view7turn15view1

**This would actually train machine-learning models.** The main model should be tabular ML—an interpretable logistic-regression baseline followed by a gradient-boosted tree model such as LightGBM. The target should be genuinely forward-looking: information available by the end of quarter \(t\) predicts an injury outcome in quarter \(t+1\). That distinction makes the project much more defensible than predicting injury severity using descriptions written *after* an accident.

For an additional “AI” layer, I would add an **optional NLP exploratory track** over MSHA accident narratives. MSHA's accident schema includes a narrative description field plus accident classification, equipment, activity, occupation, injury source, nature, and body-part fields. citeturn14view1 An English SentenceTransformer such as MiniLM is conceptually suitable here for embedding/clustering narratives. **IndoBERT is not the appropriate model** because these U.S. government narratives are English; there is no reason to introduce an Indonesian-language encoder simply to make the project sound more “AI.”

The top three project candidates are:

| Priority | Project | Portfolio strength | Primary use |
|---|---|---:|---|
| **Recommended** | **MSHA Mine-Quarter Next-Quarter Injury Risk** | ★★★★★ | Prospective risk prioritization |
| Second | **OSHA ITA Establishment-Year Next-Year Elevated Injury Rate** | ★★★★½ | Establishment risk surveillance |
| Third | **OSHA Severe Injury + BLS QCEW Spatiotemporal Forecasting** | ★★★★ | Industry/geographic hotspot monitoring |

For your specific goal—**very complex underneath, but runnable from one Colab workflow**—the MSHA project is the clear winner. It is relational, longitudinal, geospatial, exposure-adjustable, predictive, explainable, and can support an optional NLP layer without making transformers the centerpiece. MSHA provides the raw data as compressed pipe-delimited files with headers and separate definition files, which is particularly convenient for automated ingestion. citeturn15view0

One important caveat: because you asked me **not to execute/download the datasets**, I have not invented row counts. Where an official landing page does not publish the number of records, the inventory below says **“unspecified.”** That is preferable to claiming “millions” without evidence. The project can still be technically complex; longitudinal joins and leakage control matter far more than making a flat dataset artificially enormous.

## Authoritative dataset inventory

The inventory below prioritizes original agency sources rather than data.gov/data.gov.uk mirrors. The national portals are useful discovery layers, but for reproducibility I would make the notebook download directly from OSHA, MSHA, BLS, CDC/NIOSH, or HSE whenever the agency exposes the original file.

| Dataset | Official source | Rows | Coverage | Unit of observation | Key fields / join keys | License/reuse | Best-suited target |
|---|---|---:|---|---|---|---|---|
| **MSHA Accident Injuries** | MSHA/DOL | **Unspecified** | 2000–present | Reported accident/injury/illness | `MINE_ID`, `DOCUMENT_NO`, dates, quarter, injury degree, classification, occupation, activity, narrative | Dataset page does not state a specific license | Next-quarter mine injury; injury taxonomy; narrative exploration |
| **MSHA Quarterly Employment/Production** | MSHA/DOL | **Unspecified** | 2000–present | Mine × subunit × quarter | `MINE_ID`, `CAL_YR`, `CAL_QTR`, employees, hours, production | Not specifically stated | Exposure denominator / leading predictors |
| **MSHA Inspections** | MSHA/DOL | **Unspecified** | 2000–present | Inspection/event | `EVENT_NO`, `MINE_ID`, dates, activity, inspection hours, sample counts | Not specifically stated | Prior inspection intensity → future injury |
| **MSHA Violations** | MSHA/DOL | **Unspecified** | 2000–present | Citation/order/violation | `EVENT_NO`, `MINE_ID`, issue date, S&S, likelihood, negligence, persons affected | Not specifically stated | Enforcement-history leading indicators |
| **MSHA Mines** | MSHA/DOL | **Unspecified** | Mines since 1970 | Mine | `MINE_ID`, state/county, commodity, mine type, lat/lon, operating attributes | Not specifically stated | Static context / geography |
| **OSHA ITA 300A Summary** | OSHA/DOL | **Unspecified** | 2016–2025 available as of research date | Establishment-year | `establishment_ID`, NAICS, state, employees, hours, death/DAFW/DJTR counts | No specific dataset license stated on reviewed page | Next-year DART/TCR or recordable-case risk |
| **OSHA ITA Case Detail** | OSHA/DOL | **Unspecified** | 2023–2025 | Recordable case | `establishment_ID`, incident date/outcome, narratives, OIICS, occupation | No specific dataset license stated | NLP / case taxonomy; post-incident analytics |
| **OSHA Severe Injury Reports** | OSHA/DOL | **Unspecified** | 2015–Nov. 30, 2025 on current dashboard | Severe-injury report | event date, NAICS, establishment, state/city, incident description, OIICS, geocode | No specific dataset license stated | State/NAICS/quarter severe-injury forecasting |
| **BLS QCEW** | BLS | **Unspecified** | Recent five years via open CSV slices; all years through downloadable archives | Area × industry × period | area, NAICS, year/quarter, employment, establishments, wages | **Public domain** | Exposure/context denominator for OSHA joins |
| **BLS SOII** | BLS | Aggregate tables | Multi-year; 2024 current tables available | Published estimate/cell | industry, case type, incidence rate, hours, employment, occupation/demographic dimensions | **Public domain** | Benchmarking and industry-risk context |
| **BLS CFOI** | BLS | Aggregate tables | Multi-year; current fatality tables published | Published estimate/cell | industry, occupation, geography, demographic, event | **Public domain** | Fatality trend benchmark |
| **NIOSH Worker Health Charts** | CDC/NIOSH | Aggregate; exact count unspecified | Depends on source | Aggregated chart/data cell | industry, occupation, state, year, event, nature, source, demographic dimensions | Specific license not stated on page reviewed | Benchmarking/exploration |
| **NIOSH FACE** | CDC/NIOSH | **Unspecified** | Program began 1982 | Selected fatality investigation/report | report text, circumstances, recommendations | Specific license not stated on page reviewed | Semantic search/clustering of fatality narratives |
| **HSE RIDDOR statistical tables** | U.K. HSE | Aggregate spreadsheet cells; exact count unspecified | Historical tables extend to 1974; current RIDDOR tables updated regularly | Industry/region/event/year aggregate | SIC/industry, geography, kind of accident, year | **Open Government Licence** | U.K. trend analysis / time-series forecasting |

MSHA is unusually suitable for relational modeling. Its official portal says the accident file contains all accidents, injuries and illnesses reported by operators and contractors since January 2000; the quarterly employment/production file reports employment and hours by mine, quarter, and subunit; inspections contain every MSHA inspection in the published scope from 2000; and violations connect directly to inspection events. citeturn15view0 The dictionaries confirm that accidents can join mines through `MINE_ID`; quarterly production uses `MINE_ID`, year and quarter; inspections use `MINE_ID` and `EVENT_NO`; violations contain both `MINE_ID` and `EVENT_NO`. citeturn14view1turn14view3turn14view5turn14view7turn15view1

The MSHA accident file is rich enough to support both structured and text work. Its dictionary includes injury degree, accident classification, equipment, occupation, activity, source of injury, nature of injury, affected body part, days restricted, days lost, experience variables, and a narrative description. citeturn14view1 The quarterly employment file supplies the crucial exposure terms—average employee count and hours worked—as well as coal production. MSHA notes that metal/non-metal operators are not required to report production, so production cannot be treated as a universal exposure denominator. citeturn14view3turn15view0

The inspections and violations files add genuinely interesting leading-signal candidates. Inspection records include activity type, areas inspected, inspector count, on-site hours, total inspection hours, and sample counts. Violation records include significant-and-substantial status, regulatory section, likelihood, potential injury severity, number affected, negligence, enforcement area, and issue date. citeturn14view5turn15view1 The violations portal explicitly excludes vacated violations, while the inspections dataset excludes Compliance Assistance Visits, both of which should appear in the limitations section. citeturn15view0

**OSHA ITA is the next-best source.** OSHA has collected annual Form 300A establishment summaries since 2016 and case-detail Form 300/301 information beginning with calendar year 2023. Summary and case-detail files can be related through `establishment_ID`. citeturn15view2turn15view3turn15view4 Summary fields include establishment location and NAICS, annual average employment, total hours, deaths, DAFW/DJTR/other cases, days away/restricted, and illness categories. Case detail provides incident outcome and multiple redacted narrative fields plus machine-assigned occupation and OIICS classifications. citeturn15view3

OSHA itself warns against treating ITA records as a census of the U.S. workforce: filing requirements depend on establishment size and industry, the files consist of employer-submitted data, and OSHA's guidance discusses data quality and representativeness limitations. citeturn15view2turn15view4 That does not make the data bad; it means a portfolio project should explicitly frame its model as **risk estimation within the reporting universe**, not a universal American-worker risk model.

The **Severe Injury Report** data are also useful but have a narrower universe. OSHA requires reports for in-patient hospitalization, amputation, or eye loss, and the current dashboard provides data from January 1, 2015 through November 30, 2025. The dataset covers federal OSHA jurisdiction only, excludes State Plan jurisdiction, excludes fatalities from the SIR dashboard, and contains third-party geocodes whose accuracy OSHA does not guarantee. citeturn18view9turn19view0 For that reason it is much better for **spatiotemporal severe-injury surveillance** than individual worker risk prediction.

BLS is strongest as a denominator/context source rather than the main row-level ML corpus. QCEW exposes CSV slices by industry, geography, and establishment size and provides recent data programmatically, with historical ZIP downloads available separately. citeturn20view2 SOII provides nonfatal occupational injury and illness estimates and CFOI provides fatal occupational injury tables. citeturn15view5turn15view6 BLS explicitly states that its published material is in the public domain, apart from previously copyrighted photos/illustrations. citeturn20view3

For the U.K., HSE publishes extensive official RIDDOR tables by industry, region, age/gender, accident kind, nature, site, and long-run historical series; the page states that the figures are generally representative of Great Britain unless otherwise stated. citeturn17view0 These are excellent for descriptive and time-series work, but the publicly surfaced material I found is **aggregated statistical tables, not an incident-level RIDDOR microdataset** comparable to MSHA or OSHA case detail. HSE's website states that Crown material may be reused under the Open Government Licence and gives a preferred attribution statement. citeturn19view1

NIOSH's Worker Health Charts similarly provides aggregated worker health and injury information across dimensions including industry, occupation, event, nature, source, state and year, while FACE provides selected fatality investigations dating back to 1982. citeturn15view8turn15view9 FACE is attractive as an NLP corpus, but because it consists of selected fatality investigations it is not an appropriate source for estimating the probability that an ordinary workplace will experience an injury.

## Prediction targets, leakage, joins, and the NLP decision

The central methodological rule should be:

> **Define the prediction moment first. Only then decide which variables are legal predictors.**

That is especially important for safety data because government incident databases contain extremely informative variables that are only known **after an incident occurred**. A model using those variables may produce spectacular AUC while being completely useless as a predictive safety system.

| Source | Descriptive / diagnostic question | Defensible predictive target | Feasibility | Main leakage risk |
|---|---|---|---|---|
| MSHA multi-table | What operational/enforcement patterns precede injuries? | **Any qualifying injury in mine during quarter \(t+1\)** | **Excellent** | Accident/inspection/violation records dated after cutoff; current mine attributes |
| MSHA | What precedes more serious events? | Lost-time/severe injury in \(t+1\) | Good, likely more imbalanced | Using injury severity fields from target period |
| OSHA ITA summary | Which establishments show persistent elevated rates? | Next-year DART/TCR class | Very good if cross-year identity is reliable | Using year \(t+1\) hours/counts; unstable establishment matching |
| OSHA case detail | What types of incidents/narratives recur? | OIICS/type classification | Good as NLP taxonomy | OIICS and outcome generated from post-event information |
| OSHA SIR + QCEW | Where could severe-injury burden be elevated next period? | State/NAICS/quarter count or rate | Good | Future QCEW denominator; jurisdiction changes; incomplete U.S. coverage |
| BLS SOII/CFOI | Which sectors have elevated published rates? | Aggregate time-series rate | Moderate | Revision/future values; ecological interpretation |
| HSE RIDDOR | How have injuries changed across industry/region? | Aggregate annual/quarterly rate/count | Moderate | Structural/reporting changes; aggregated data |
| NIOSH FACE | What recurring fatal-event themes appear? | Better as clustering/search than prediction | Low for prospective risk | Every case is selected after a fatal event |

**The MSHA join should be built as a time-indexed star schema:**

```text
                           MINES
                         MINE_ID
                            │
                            │ stable/context fields only
                            ▼
                  ┌───────────────────┐
                  │  MINE × QUARTER   │
                  │      PANEL        │
                  └───────────────────┘
                    ▲       ▲       ▲
                    │       │       │
                    │       │       │
      EMPLOYMENT/PROD   INSPECTIONS   ACCIDENTS
      MINE_ID            MINE_ID       MINE_ID
      YEAR+QUARTER       EVENT_NO      DATE/QTR
                             │
                             ▼
                         VIOLATIONS
                         EVENT_NO
                         MINE_ID
```

MSHA's dictionaries explicitly support these joins: `MINE_ID` connects mines to accidents, inspections and quarterly employment/production; `EVENT_NO` is the inspection-to-violation key. citeturn14view1turn14view3turn14view5turn14view7turn15view1

I would create the prediction record at the **mine-quarter** level. At the close of quarter \(t\), the model sees only information with dates no later than that quarter-end. It then predicts whether a qualifying injury occurs in quarter \(t+1\).

Core predictor families would be:

| Signal family | Examples |
|---|---|
| Exposure | hours worked, employee count, production where applicable |
| Mine context | state, commodity group, physical mine type, geography |
| Prior safety history | injuries in past 1/4/8 quarters, days lost, time since last injury |
| Inspection history | inspections, inspection hours, sample counts, time since last inspection |
| Enforcement history | violation count, S&S proportion, likelihood/negligence mix, persons affected |
| Derived trend | change in hours, workforce, violations, injury frequency |
| Seasonality | calendar quarter, year trend |
| Optional narrative signal | embeddings/clusters from **historical** incident narratives |

There is an important subtlety in the Mines table. Many fields are explicitly named `CURRENT_*`—current status, current operator, current controller, current 103(i) status—rather than historical values. citeturn14view7 Using their 2026 values to characterize a mine in 2005 could leak future information. The model should therefore exclude mutable `CURRENT_*` fields from historical prediction unless they can be reconstructed from MSHA's dated operator/controller history. That leakage audit itself would be an excellent portfolio artifact.

For OSHA ITA, case-detail-to-summary linkage inside a reporting year is documented through `establishment_ID`. citeturn15view2turn15view3 But for a next-year establishment model I would **first empirically validate identifier persistence across reporting years** before assuming `establishment_ID` is a perfect longitudinal establishment key. If persistence is weak, a deterministic/probabilistic match using EIN, location, establishment name and NAICS would introduce substantial data-engineering complexity and matching uncertainty.

For SIR, I would aggregate severe injuries into **state/county × NAICS × quarter** cells and bring in QCEW employment/establishment context using time, geography and industry. QCEW is specifically designed to publish area/industry employment data in downloadable CSV form. citeturn20view2 But the model must retain a jurisdiction mask because SIR does not cover State Plan incidents. citeturn19view0 Otherwise, a model could incorrectly interpret “not reported to federal OSHA” as “safe.”

**MiniLM vs. IndoBERT vs. tabular ML:** for the main project, use tabular ML. The strongest claim is not “I fine-tuned a transformer”; it is “I created a leakage-safe prospective safety-risk dataset from five government tables and evaluated whether historical signals predict the next period.”

For narrative work, the right hierarchy is:

```text
TF-IDF + Logistic Regression
        ↓ baseline
English MiniLM embeddings
        ↓
PCA / clustering / semantic similarity
        ↓
optional supervised model
        ↓
fine-tuned transformer only if genuinely justified
```

An accident narrative is useful for **semantic exploration of historical event patterns**. It should not be smuggled into a pre-incident risk model if that narrative was written after the accident. MSHA's narrative is explicitly an accident/injury/illness description, and OSHA's detailed narratives are likewise collected as incident records; OSHA also uses narrative information in coding occupational classifications. citeturn14view1turn15view3

That is why I would keep the text model as a **second analytical track**, not use it to artificially inflate predictive performance.

## Prioritized project architecture

**Top choice — MSHA MineRisk-Q: Predicting Next-Quarter Injury Risk.**

The portfolio headline could eventually become:

> **Can twenty-five years of operational and enforcement signals tell us where to look earlier?**

The source history supports a 2000-present modeling window for accidents, quarterly employment, inspections and violations, while the mine registry is older. citeturn15view0

The primary target should be:

> **At the end of each mine-quarter, predict whether at least one qualifying worker injury/illness will be reported in the following quarter.**

The accident dictionary contains injury-degree categories including fatality, permanent disability, days-away cases, restricted activity, no-days-away injuries and occupational illness, as well as categories such as accident-only, natural causes, non-employees and other cases. citeturn14view1 Rather than hard-coding a questionable interpretation from memory, the notebook should explicitly validate the final “qualifying reportable worker case” mapping against MSHA Part 50 documentation before creating the target. A useful secondary target is **next-quarter lost-time/severe case**, once class balance is observed.

The most valuable model comparison would be:

**Prevalence baseline → Logistic Regression → LightGBM/gradient-boosted trees → calibrated final model.**

The evaluation should emphasize PR-AUC when the positive class is rare, ROC-AUC for rank discrimination, Brier score and a reliability curve for probability quality, and operational metrics such as **recall in the top 10% of scored mines** and **lift in the highest-risk decile**. This framing is more meaningful than reporting accuracy.

The especially strong experiment is a **feature-family ablation study**:

```text
MODEL A
Exposure + mine context

MODEL B
A + prior injury history

MODEL C
B + inspections

MODEL D
C + violations

MODEL E
D + trend features
```

That answers a much more interesting question than “Which algorithm wins?”:

> **How much predictive information is added by each layer of safety history?**

A second robustness experiment should compare performance **with vs. without previous-injury features**. If most predictive value disappears when prior injuries are removed, that is itself a major finding: the model may primarily identify persistence rather than novel leading indicators.

**Second choice — OSHA ITA next-year establishment risk.**

This would use Form 300A summary data, which OSHA has collected since 2016, to build establishment-year histories and predict an elevated next-year DART/TCR outcome. OSHA's summary fields include employee counts, hours worked, deaths, days-away/restricted-job cases, injury types and industry/location data. citeturn15view2turn15view4 This has excellent relevance for conventional HSE practitioners, and BLS SOII could supply industry benchmarking. The drawback is that the longitudinal establishment identity problem must be verified before we can promise a clean panel.

**Third choice — OSHA SIR + BLS QCEW severe-injury hotspot forecasting.**

This would aggregate federal OSHA severe-injury reports by industry, geography and period, merge QCEW exposure/employment context, forecast the next quarter's severe-injury burden, and show the result on an interactive map. SIR contains severe events from 2015 onward and provides incident, establishment, OIICS and geographic information, but its jurisdiction limitation needs to remain visible in every interpretation. citeturn19view0turn20view2 This could be visually spectacular but is less clean than MSHA for nationwide prospective risk because State Plan states are absent.

The **executive figure** for the MSHA project should not be a generic dashboard. I would create one wide analytical composition containing:

```text
┌──────────────────────────────────────────────────────────────┐
│ CAN SAFETY DATA HELP US LOOK EARLIER?                        │
│ Mine-level historical risk forecasting                      │
│                                                              │
│  OPERATION       SAFETY HISTORY       MODEL        DECISION  │
│                                                              │
│  Hours worked ─┐ Prior injuries ─┐                           │
│  Workforce    ─┼ Inspections    ─┼─► Risk model ─► HIGH      │
│  Production   ─┘ Violations     ─┘              ├► MEDIUM    │
│                                                  └► LOW       │
│                                                              │
│  [Temporal trend] [PR curve] [Calibration] [SHAP drivers]    │
│                                                              │
│                     [U.S. mine risk map]                      │
│                                                              │
│  TOP DECILE LIFT  │  RECALL  │  CALIBRATION  │ LIMITATION   │
└──────────────────────────────────────────────────────────────┘
```

The bottom line should explicitly say:

> **This is decision support for prioritizing investigation—not an automated safety decision system.**

That framing matters because inspection, enforcement and injury data are observational and can reflect reporting, enforcement intensity and historical policy as well as underlying hazard.

## Colab feasibility, visualization stack, and outputs

A one-shot Colab implementation is realistic **provided the workflow aggregates the raw relational tables early instead of repeatedly joining raw event-level records in memory**. Google describes Colab as a hosted Jupyter environment suitable for data science and ML, but it also states that free resources are not guaranteed, are not unlimited, and usage limits fluctuate. citeturn17view2 Therefore the notebook should adapt to available RAM/GPU rather than assume a fixed machine.

Because the official MSHA portal does not publish row counts on the pages reviewed, runtime estimates necessarily have to be treated as **planning estimates, not measured benchmarks**. I would use these design budgets:

| Stage | Colab strategy | Planning target |
|---|---|---|
| Download ZIPs | stream/cache each file once | a few minutes, network-dependent |
| Raw ingestion | Polars lazy scan / selective columns | avoid holding all raw tables simultaneously |
| Quarterly aggregation | aggregate each raw table separately | keep event tables out of final join |
| Final panel | Pandas or Polars + Parquet | ideally comfortably below available RAM |
| Logistic baseline | CPU | typically light |
| LightGBM | CPU | suitable for medium/large tabular panel |
| Calibration | validation subset | light/moderate |
| SHAP | sample 5k–10k rows | avoid full-dataset SHAP |
| MiniLM branch | max 50k narratives; GPU if available | optional/adaptive |
| Plotly | aggregated points/records | interactive |
| Static exports | Matplotlib + Kaleido/Plotly export | 300-DPI portfolio output |

The NLP step should be automatically disabled or sampled more aggressively if no GPU is available. The **core risk model must run without NLP**, so a transformer failure never makes the entire notebook fail.

For very large raw files, the notebook should:

```text
ZIP
 ↓
extract once
 ↓
Polars lazy scan
 ↓
select required columns
 ↓
parse dates
 ↓
filter modeling years
 ↓
aggregate by MINE_ID + YEAR + QUARTER
 ↓
write Parquet
 ↓
discard raw frame from RAM
```

This gives us one clean `mine_quarter_panel.parquet` before conventional ML starts.

The visual output should include both interactive and publication-ready figures:

| Visual | Why it matters |
|---|---|
| Plotly mine map | geographic exploration |
| Historical injury/exposure trend | temporal context |
| Mine-quarter risk distribution | model behavior |
| Precision–recall curve | imbalanced-target evaluation |
| ROC curve | discrimination |
| Calibration/reliability curve | whether risk probabilities are trustworthy |
| Lift/gains chart | operational prioritization |
| Confusion/threshold plot | consequence of threshold choice |
| SHAP beeswarm | global explanation |
| SHAP dependence | nonlinear feature behavior |
| Local SHAP waterfall | individual mine-quarter explanation |
| Subgroup performance | coal vs metal/non-metal / mine class |
| Error-analysis figure | where the model fails |
| NLP semantic map | optional narrative pattern exploration |
| Executive composite | portfolio hero visual |

The recommended output structure is:

```text
/osh_msha_predictive_ai/
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│       └── mine_quarter_panel.parquet
│
├── metadata/
│   ├── data_dictionary.csv
│   ├── leakage_audit.csv
│   ├── feature_dictionary.csv
│   └── data_provenance.json
│
├── models/
│   ├── logistic_baseline.joblib
│   ├── lightgbm_model.txt
│   └── calibration_model.joblib
│
├── outputs/
│   ├── data_quality/
│   ├── eda/
│   ├── temporal/
│   ├── geographic/
│   ├── model_performance/
│   ├── calibration/
│   ├── explainability/
│   ├── error_analysis/
│   ├── nlp/
│   └── portfolio/
│
├── tables/
│   ├── model_comparison.csv
│   ├── subgroup_performance.csv
│   ├── top_risk_cases.csv
│   └── ablation_results.csv
│
└── README.md
```

The entire research flow should be:

```mermaid
flowchart LR
    A[Official MSHA data] --> B[Schema & provenance audit]
    B --> C[Temporal mine-quarter panel]
    C --> D[Leakage audit]
    D --> E[Exploratory OSH analytics]
    E --> F[Temporal train / validation / test]
    F --> G[Baseline model]
    G --> H[Gradient-boosted model]
    H --> I[Calibration & threshold analysis]
    I --> J[SHAP & error analysis]
    J --> K[Robustness / ablation tests]
    K --> L[Optional MiniLM narrative exploration]
    L --> M[Decision-support visuals]
    M --> N[Portfolio exports]
```

## One-shot Google Colab master prompt

The prompt below is tailored to the **MSHA MineRisk-Q** design and the official MSHA schemas described above. The URLs and join logic are based on the MSHA Open Government portal and its accident, employment/production, inspection, mine and violation definition files. citeturn15view0turn14view1turn14view3turn14view5turn14view7turn15view1

```text
MASTER PROMPT
MSHA MINERISK-Q
Predictive AI + Exploratory Occupational Safety Analytics
Google Colab End-to-End Build

============================================================
ROLE
============================================================

You are working as a:

- Senior Data Scientist
- Occupational Safety & Health Analyst
- Machine Learning Engineer
- Statistical Reviewer
- Data Engineer
- Explainable-AI Specialist
- Data Visualization Designer

Build and EXECUTE a complete Google Colab project using official
U.S. Mine Safety and Health Administration public data.

Do not merely write sample code.

Create notebook cells, execute them sequentially, inspect outputs,
repair errors, and continue until the notebook can run end-to-end.

The final artifact must be suitable for a professional
OSH/Data Science portfolio.

PROJECT TITLE:

MineRisk-Q:
Exploratory and Predictive Analytics for
Next-Quarter Mine Injury Risk

PRIMARY RESEARCH QUESTION:

"Using information available by the end of a mine-quarter,
can historical operational, exposure, injury, inspection,
and enforcement signals identify mines with elevated risk
of a qualifying injury/illness in the following quarter?"

Core philosophy:

QUESTION FIRST.
PREDICTION MOMENT SECOND.
LEAKAGE AUDIT THIRD.
MODEL LAST.

Never optimize presentation at the expense of methodology.

============================================================
OFFICIAL DATA SOURCES
============================================================

Use ONLY the official MSHA files below for the primary analysis.

SOURCE PORTAL:

https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp

ACCIDENTS:

https://arlweb.msha.gov/OpenGovernmentData/DataSets/Accidents.zip

Dictionary:

https://arlweb.msha.gov/OpenGovernmentData/DataSets/Accidents_Definition_File.txt

QUARTERLY MINE EMPLOYMENT / PRODUCTION:

https://arlweb.msha.gov/OpenGovernmentData/DataSets/MinesProdQuarterly.zip

Dictionary:

https://arlweb.msha.gov/OpenGovernmentData/DataSets/MineSProdQuarterly_Definition_File.txt

INSPECTIONS:

https://arlweb.msha.gov/OpenGovernmentData/DataSets/Inspections.zip

Dictionary:

https://arlweb.msha.gov/OpenGovernmentData/DataSets/Inspections_Definition_File.txt

MINES:

https://arlweb.msha.gov/OpenGovernmentData/DataSets/Mines.zip

Dictionary:

https://arlweb.msha.gov/OpenGovernmentData/DataSets/Mines_Definition_File.txt

VIOLATIONS:

Attempt the official portal-linked violations archive:

https://arlweb.msha.gov/OpenGovernmentData/DataSets/Violations.zip

Dictionary:

https://arlweb.msha.gov/OpenGovernmentData/DataSets/violations_Definition_File.txt

If any hard-coded archive URL changes:

1. do NOT substitute Kaggle or a third-party mirror;
2. inspect the official MSHA portal;
3. resolve the current official download URL;
4. document the changed URL in the provenance log.

============================================================
REPRODUCIBILITY
============================================================

The notebook must be restart-safe.

It should ideally reproduce through:

Runtime
→ Restart session
→ Run all

At the beginning:

- detect Python version
- detect available RAM
- detect GPU
- set random seed = 42
- print package versions
- create project folders
- create provenance log

Use a minimal dependency stack.

Preferred:

pandas
polars
numpy
pyarrow
scipy
statsmodels
scikit-learn
lightgbm
matplotlib
plotly
shap
joblib

Optional NLP:

sentence-transformers
scikit-learn

Do NOT install heavy NLP dependencies unless the NLP branch runs.

============================================================
PROJECT DIRECTORY
============================================================

Create:

/content/osh_msha_predictive_ai/

    data/
        raw/
        interim/
        processed/

    metadata/

    models/

    tables/

    outputs/
        data_quality/
        eda/
        temporal/
        geographic/
        model_performance/
        calibration/
        explainability/
        error_analysis/
        nlp/
        portfolio/

Save every final artifact there.

============================================================
DOWNLOAD LOGIC
============================================================

Download each source only if it is not already cached.

Use robust HTTP requests with:

- timeout
- retries
- status checking
- descriptive failure messages

Record:

URL
download timestamp
compressed file size
SHA256 checksum

Do NOT silently continue after a failed download.

Extract ZIP files programmatically.

Do not assume the internal filename.

Inspect archive contents and locate the actual delimited file.

MSHA files are expected to be pipe-delimited.

Verify delimiter and header automatically.

============================================================
BIG-DATA INGESTION STRATEGY
============================================================

Never blindly load every raw table into pandas at once.

Prefer:

Polars lazy scan
or
chunked reading

especially for:

violations
inspections
accidents

For each raw table:

1. inspect schema;
2. normalize column names to lowercase;
3. select only required fields;
4. parse dates;
5. aggregate early;
6. write an interim Parquet table;
7. release the raw frame from memory.

Report:

raw row count
selected row count
number of columns
memory footprint where measurable

These counts must be ACTUAL results,
not assumptions.

============================================================
DATA DICTIONARY
============================================================

Parse the official definition files when feasible.

Create:

metadata/data_dictionary.csv

Columns:

dataset
column
official_type
official_length
official_description
analytical_role
potential_leakage
included_final_model
reason

Never infer an undocumented definition without marking it
as an interpretation.

============================================================
PREDICTION UNIT
============================================================

Primary unit:

MINE_ID × CALENDAR_YEAR × CALENDAR_QUARTER

Prediction moment:

END OF QUARTER t

Forecast horizon:

QUARTER t+1

All features must be known by the end of quarter t.

Target information must come exclusively from quarter t+1.

============================================================
TARGET DESIGN
============================================================

Use the MSHA Accident Injuries data.

First inspect:

degree_injury_cd
degree_injury

Use official definitions to determine which codes represent
reportable worker injury/illness cases.

Do NOT casually hard-code the target.

Create a TARGET DESIGN TABLE showing:

degree code
description
included?
reason

Potential preliminary mapping to investigate:

01 Fatality
02 Permanent disability
03 Days away from work
04 Days away + restricted activity
05 Restricted activity
06 No days away / no restriction
07 Occupational illness

Potential exclusions to investigate:

00 accident only
08 natural causes
09 non-employees
10 other / first aid

VALIDATE THIS MAPPING before proceeding.

Primary binary target:

next_q_any_reportable_injury

= 1 if at least one qualifying worker injury/illness
occurs at the mine in quarter t+1.

Secondary target, only if sample size permits:

next_q_lost_time_or_severe_injury

Do not allow the secondary target to derail the project
if positive examples are too sparse.

============================================================
MASTER MINE-QUARTER PANEL
============================================================

Use quarterly employment/production as the principal
mine-quarter exposure spine.

Aggregate subunits to:

mine_id
calendar_year
calendar_quarter

Compute:

avg_employee_cnt
hours_worked
coal_production where available

Do NOT interpret missing metal/non-metal production as zero
without confirming reporting rules.

Create a continuous quarter index.

Generate lag and rolling features strictly from past data.

============================================================
ACCIDENT HISTORY FEATURES
============================================================

Aggregate accidents by mine-quarter.

Candidate historical features:

injury_count_q
lost_time_case_count_q
fatal_case_count_q
days_lost_q
days_restricted_q

rolling_4q_injury_count
rolling_8q_injury_count

rolling_4q_days_lost
rolling_8q_days_lost

quarters_since_last_injury

previous_q_injury_flag

historical_injury_rate_per_200k_hours

Only calculate exposure-normalized rates when denominator
hours are valid and positive.

Cap or flag unstable rates produced by tiny denominators.

NEVER include any accident occurring in target quarter t+1
as a predictor.

============================================================
INSPECTION FEATURES
============================================================

Aggregate inspections using dates available by the prediction cutoff.

Candidate features:

inspection_count_q
inspection_hours_q
onsite_hours_q
inspectors_q
air_sample_count_q
noise_sample_count_q
resp_dust_sample_count_q

rolling_4q_inspections
rolling_4q_inspection_hours

quarters_since_last_inspection

activity-code distributions if useful

Inspect activity categories.

Identify inspection/investigation types closely tied to accidents.

Create sensitivity analyses if necessary:

MODEL INCLUDING all valid historical inspection activity

versus

MODEL EXCLUDING accident-investigation-like activities

Never use an inspection ending after the prediction cutoff.

============================================================
VIOLATION FEATURES
============================================================

Aggregate only violations issued by the prediction cutoff.

Candidate features:

violation_count_q
s_and_s_count_q
s_and_s_share_q

likelihood category counts
negligence category counts
injury_illness_gravity counts

people_affected_sum

rolling_4q_violation_count
rolling_4q_s_and_s_count

quarters_since_last_violation

Use:

violation_issue_dt

as the primary knowledge-time variable unless the
documentation demonstrates another date is more appropriate.

Exclude information generated after the prediction cutoff.

Treat later assessment/payment/legal fields as leakage.

Examples of fields that should NOT enter the prospective model
unless proven available at prediction time:

amount_paid
future final-order information
later docket outcomes
later termination information
last_action fields

Create a formal decision for every violation feature family.

============================================================
MINE CHARACTERISTICS
============================================================

Join Mines on:

mine_id

Use caution.

The Mines table includes fields explicitly labeled CURRENT_*.

These may reflect information updated after historical periods.

DO NOT use historically mutable CURRENT_* fields in a
2000-era prediction simply because they are present today.

Create:

metadata/leakage_audit.csv

For every mine field classify:

SAFE / STABLE
QUESTIONABLE
HISTORICAL LEAKAGE RISK
EXCLUDED IDENTIFIER

Potentially useful relatively stable context to evaluate:

state
county
latitude
longitude
coal/metal indicator
primary commodity
portable-operation flag

Mine type or commodity must be excluded if historical validity
cannot be justified.

Exclude current operator/controller/status/103i variables
unless historical reconstruction is available.

============================================================
LEAKAGE AUDIT
============================================================

This section is mandatory.

Create a table:

feature
source table
feature timestamp
prediction cutoff
available at prediction time?
leakage risk
decision
reason

Also detect:

TARGET LEAKAGE
FUTURE LEAKAGE
HISTORICAL-SNAPSHOT LEAKAGE
POST-ENFORCEMENT LEAKAGE
IDENTIFIER LEAKAGE

Export:

metadata/leakage_audit.csv

and

outputs/portfolio/leakage_audit.png

This should be portfolio-quality.

============================================================
DATA-QUALITY AUDIT
============================================================

Report:

duplicate keys
missing values
invalid dates
zero-hour quarters
negative/impossible values
category cardinality
outliers
min/max years
number of unique mines
quarter coverage
positive-target prevalence

Check whether raw datasets have different latest complete quarters.

Use the latest common COMPLETE quarter.

Drop any final quarter whose reporting appears incomplete.

Document the decision.

============================================================
EXPLORATORY ANALYSIS
============================================================

Do rigorous EDA before machine learning.

At minimum examine:

injuries over time
hours worked over time
injuries by coal/metal category
injury degree
injury classifications
mine geography
quarter seasonality

injury count vs exposure hours

prior injury history vs next-quarter target

inspection intensity vs future outcomes

violation burden vs future outcomes

S&S violation history vs future outcomes

Avoid calling raw counts "risk."

Distinguish:

COUNT
RATE
PROPORTION
PREDICTED PROBABILITY

Generate both static and interactive visuals.

============================================================
TEMPORAL SPLIT
============================================================

DO NOT randomly split the main dataset.

Use temporal validation.

Determine the most recent complete quarters dynamically.

Preferred strategy:

TEST:
last 8 complete target quarters

VALIDATION:
8 complete target quarters immediately preceding test

TRAIN:
all earlier eligible quarters

If data availability makes this unreasonable,
choose another chronological split and document why.

Never fit preprocessing on validation/test periods.

============================================================
BASELINES
============================================================

Create:

BASELINE 0
constant prevalence prediction

BASELINE 1
simple prior-injury rule

BASELINE 2
regularized Logistic Regression

The project is not allowed to claim ML value unless
the complex model is compared with simple baselines.

============================================================
PRIMARY MODEL
============================================================

Primary advanced model:

LightGBM binary classifier

If LightGBM cannot be installed or executed,
fall back to a defensible sklearn gradient-boosted model.

Handle categorical variables appropriately.

Address imbalance initially through:

class weights

Do NOT automatically use SMOTE.

Do NOT generate synthetic future observations.

Tune only a small, defensible hyperparameter space.

Avoid massive hyperparameter searches.

============================================================
FEATURE-FAMILY ABLATION
============================================================

Train and compare:

MODEL A
Exposure + safe mine context

MODEL B
A + historical injury features

MODEL C
B + inspection features

MODEL D
C + violation features

MODEL E
D + engineered trend features

Report:

ROC-AUC
PR-AUC
Brier score
precision
recall
F1
top-decile recall
top-decile lift

This experiment is a central part of the project.

Answer:

Which information layer actually adds predictive signal?

============================================================
CALIBRATION
============================================================

Evaluate raw probability calibration.

Generate reliability diagrams.

Calculate Brier score.

If calibration is inadequate:

use a validation-only calibration procedure
such as sigmoid or isotonic calibration.

Never fit calibration using the held-out test period.

Compare:

raw
versus
calibrated

probabilities.

============================================================
OPERATIONAL RANKING
============================================================

Because the project is about prioritization,
evaluate ranking usefulness.

For the held-out test period compute:

top 1%
top 5%
top 10%
top 20%

For each:

number of mines flagged
fraction of future injury-positive mines captured
precision
lift relative to prevalence

Create:

cumulative gains curve
lift curve
recall-at-capacity curve

Do not choose a threshold without an operational rationale.

============================================================
MODEL EXPLAINABILITY
============================================================

For Logistic Regression:

show standardized coefficient directions where appropriate.

For LightGBM:

use:

SHAP TreeExplainer

Limit SHAP to a representative sample,
default maximum:

10,000 rows

unless memory permits more.

Create:

SHAP global bar
SHAP beeswarm
SHAP dependence for key variables

Select representative examples:

true positive
true negative
false positive
false negative
high-risk correctly predicted mine-quarter

Create local SHAP waterfall plots.

Never describe SHAP as causal.

Use phrasing:

"contributed to predicted risk"

not:

"caused injuries."

============================================================
ERROR ANALYSIS
============================================================

Analyze false negatives and false positives.

Evaluate subgroup performance by available valid groups such as:

coal vs metal/non-metal
mine size band
state/region
exposure-hours band
historical injury/no-history group

Only use groups supported by legitimate fields.

Report:

n
prevalence
ROC-AUC where estimable
PR-AUC where estimable
recall
precision
Brier score

Flag small-n groups.

============================================================
ROBUSTNESS TESTS
============================================================

Mandatory analyses:

1. model without previous-injury variables

2. model without enforcement/violation variables

3. model on mines with no injury in recent history

4. alternate temporal cutoff if computationally practical

5. performance across early versus late test periods

Determine whether apparent performance depends mostly on
prior accident persistence.

Do not hide negative robustness results.

============================================================
OPTIONAL NLP EXPLORATION
============================================================

This is NOT part of the primary predictive target.

It is an exploratory AI layer.

Use only historical MSHA Accident NARRATIVE text.

Do NOT use target-quarter narratives to predict target-quarter risk.

Goal:

discover semantic patterns in historical accident narratives.

Workflow:

1. clean narrative
2. remove empty/very short narratives
3. stratified sample, maximum 50,000 texts by default
4. baseline TF-IDF representation
5. if GPU or reasonable CPU resources are available:
   encode with

   sentence-transformers/all-MiniLM-L6-v2

6. PCA for compression
7. KMeans or another stable clustering method
8. inspect representative narratives nearest cluster centroids
9. calculate distinctive terms per cluster
10. compare clusters with structured accident classifications

Generate:

semantic cluster scatter
cluster-size chart
representative pattern table

Do NOT use IndoBERT.

The corpus is English.

Skip or downsample this NLP branch automatically
if compute resources are insufficient.

The main project must still finish successfully.

============================================================
GEOGRAPHIC VISUALIZATION
============================================================

If latitude/longitude quality is sufficient:

create an interactive U.S. mine map.

Possible encodings:

mine type
historical injury count
held-out predicted next-quarter risk
actual future outcome

Use aggregated/filterable data.

Avoid plotting an unreadable cloud of millions of marks.

Also create a static portfolio map.

Clearly distinguish:

observed historical outcomes

from

predicted future risk.

============================================================
REQUIRED FIGURES
============================================================

Export at minimum:

01_data_source_architecture.png

02_data_quality_overview.png

03_target_definition.png

04_leakage_audit.png

05_injury_trend.png

06_exposure_adjusted_trend.png

07_geographic_pattern.png

08_prior_history_risk_gradient.png

09_model_comparison.png

10_precision_recall_curve.png

11_calibration_curve.png

12_lift_curve.png

13_top_decile_capture.png

14_shap_global.png

15_shap_beeswarm.png

16_local_explanation.png

17_error_analysis.png

18_subgroup_performance.png

19_ablation_results.png

20_executive_summary.png

Optional:

21_narrative_semantic_map.png

Use high-resolution:

300 DPI for static portfolio exports.

Also retain interactive Plotly HTML files where useful.

============================================================
EXECUTIVE FIGURE
============================================================

Create one publication-quality final figure communicating:

OPERATION
+
EXPOSURE
+
PRIOR INJURY HISTORY
+
INSPECTIONS
+
VIOLATIONS

            ↓

LEAKAGE-SAFE
MINE-QUARTER PANEL

            ↓

TEMPORAL
PREDICTIVE MODEL

            ↓

CALIBRATED RISK

            ↓

EXPLANATION
+
PRIORITIZATION

Include:

test-period metric summary
top-decile lift
calibration result
top SHAP drivers
small geographic element
clear limitation note

Do not overcrowd it.

============================================================
PORTFOLIO DESIGN
============================================================

Use a restrained palette:

Warm White #FAF8F5
Deep Navy  #0F172A
Blue       #0284C7
Slate      #64748B

Use semantic alert colors sparingly.

Avoid:

rainbow palettes
3D charts
generic AI brains
decorative dashboards
unnecessary gradients

Finding-based chart titles may only be written AFTER the
actual analysis demonstrates the finding.

============================================================
STATISTICAL LANGUAGE
============================================================

Never claim:

causation

from observational predictive results.

Never write:

"violations cause injuries"

unless there is causal evidence,
which this project does not provide.

Preferred:

"higher historical violation burden was associated with..."

"the model assigned greater predicted risk when..."

"this feature contributed to..."

"the association may reflect..."

============================================================
LIMITATIONS
============================================================

Explicitly discuss:

reporting bias
missingness
observational design
changes through time
mine closures/openings
historically mutable mine fields
inspection/enforcement intensity
underreporting
exposure denominator issues
coal vs metal/non-metal differences
target definition
class imbalance
concept drift
probability calibration
generalizability

State clearly:

THIS MODEL IS AN EXPLORATORY DECISION-SUPPORT ANALYSIS.

IT IS NOT AN AUTOMATED ENFORCEMENT,
COMPLIANCE, OR SAFETY DECISION SYSTEM.

============================================================
FILES TO SAVE
============================================================

metadata/data_dictionary.csv
metadata/leakage_audit.csv
metadata/feature_dictionary.csv
metadata/provenance.json

data/processed/mine_quarter_panel.parquet

tables/model_comparison.csv
tables/ablation_results.csv
tables/subgroup_performance.csv
tables/top_risk_cases.csv

models/logistic_baseline.joblib
models/final_model.*
models/calibration_model.joblib

outputs/**/*
README.md

============================================================
FINAL REPORT
============================================================

At the end of the notebook produce a Markdown executive report
with exactly these elements:

PROJECT QUESTION

DATA SOURCES

ACTUAL RAW ROW COUNTS

FINAL MINE-QUARTER ROW COUNT

MODELING YEARS

TARGET DEFINITION

TARGET PREVALENCE

LEAKAGE VARIABLES REMOVED

FEATURE FAMILIES

TEMPORAL SPLIT

BASELINE PERFORMANCE

ADVANCED MODEL PERFORMANCE

CALIBRATION RESULT

TOP-DECILE CAPTURE

ABLATION FINDINGS

SHAP FINDINGS

ERROR ANALYSIS

SUBGROUP FINDINGS

ROBUSTNESS FINDINGS

NLP FINDINGS
(if executed)

PRACTITIONER INTERPRETATION

LIMITATIONS

WHAT WE MUST NOT CLAIM

BEST PORTFOLIO FIGURES

REPRODUCIBILITY STATUS

============================================================
FAIL-SAFE BEHAVIOR
============================================================

Do not stop simply because one optional stage fails.

If a package fails:
use a documented fallback.

If NLP fails:
skip NLP and finish tabular analysis.

If map export fails:
save HTML and continue.

If LightGBM fails:
use sklearn HistGradientBoosting or another defensible fallback.

If the target is extremely imbalanced:
do not fake balance.
Use appropriate metrics and explain the issue.

If advanced ML does not meaningfully beat the baselines:
REPORT THAT RESULT.

Do not manipulate the split,
feature set,
or target merely to produce an impressive score.

A scientifically honest negative result is acceptable.

============================================================
SUCCESS CRITERIA
============================================================

The project succeeds if it demonstrates:

DATA ENGINEERING
multiple official government datasets joined correctly

OSH REASONING
exposure and reporting context understood

TEMPORAL REASONING
future outcome separated from historical features

LEAKAGE CONTROL
future and current-snapshot leakage identified

ANALYTICS
meaningful exploratory findings

ML
baselines and advanced models compared fairly

VALIDATION
chronological holdout used

CALIBRATION
risk probabilities evaluated

EXPLAINABILITY
model behavior analyzed responsibly

ERROR ANALYSIS
failure modes investigated

DECISION SUPPORT
risk translated into prioritization without causal overclaim

COMMUNICATION
high-quality figures exported

Begin now.

First create the directory structure,
install/check only necessary packages,
download and verify official MSHA files,
parse their schemas,
and report ACTUAL dataset dimensions before
creating any prediction target.
```

The most important instruction in that entire prompt is arguably **not** the LightGBM section. It is the requirement to construct the target *after* a prediction-time and leakage audit. MSHA's own schemas include several fields that describe consequences after an injury, later enforcement outcomes, and “current” mine attributes; blindly feeding those into a model would create exactly the sort of misleading AI project we want to avoid. citeturn14view1turn14view7turn15view1

## Exact data URLs and recommended reading

These are the links I would actually preserve in the notebook's provenance section.

**MSHA — primary project**

Official open-data catalog:  
`https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp`  
The portal documents update frequency, time coverage, keys, formats and available source tables. citeturn15view0

Accident Injuries archive:  
`https://arlweb.msha.gov/OpenGovernmentData/DataSets/Accidents.zip`

Accident dictionary:  
`https://arlweb.msha.gov/OpenGovernmentData/DataSets/Accidents_Definition_File.txt`  
The dictionary documents `MINE_ID`, `DOCUMENT_NO`, dates, injury degree, equipment, occupation/activity, injury source/nature/body part, lost days and narrative. citeturn14view1

Quarterly mine employment/production:  
`https://arlweb.msha.gov/OpenGovernmentData/DataSets/MinesProdQuarterly.zip`

Quarterly employment dictionary:  
`https://arlweb.msha.gov/OpenGovernmentData/DataSets/MineSProdQuarterly_Definition_File.txt`  
The file defines mine/subunit/quarter employee count, hours worked and coal production. citeturn14view3

Inspections archive:  
`https://arlweb.msha.gov/OpenGovernmentData/DataSets/Inspections.zip`

Inspections dictionary:  
`https://arlweb.msha.gov/OpenGovernmentData/DataSets/Inspections_Definition_File.txt`  
`EVENT_NO` identifies inspection events and links them to violations; `MINE_ID` links to Mines. citeturn14view5

Mines archive:  
`https://arlweb.msha.gov/OpenGovernmentData/DataSets/Mines.zip`

Mines dictionary:  
`https://arlweb.msha.gov/OpenGovernmentData/DataSets/Mines_Definition_File.txt`  
MSHA identifies `MINE_ID` as the unique mine key and provides geography, commodity and operating attributes. citeturn14view7

Violations dictionary:  
`https://arlweb.msha.gov/OpenGovernmentData/DataSets/violations_Definition_File.txt`  
It documents `EVENT_NO`, `MINE_ID`, issue date, S&S status, likelihood, potential injury severity, negligence and other enforcement fields. citeturn15view1

The safest way to retrieve the current Violations ZIP is also through the official MSHA catalog above because the static archive URL was not successfully rendered by the research browser; the notebook prompt therefore explicitly verifies the link rather than silently substituting a mirror.

**OSHA Injury Tracking Application**

Main ITA data hub:  
`https://www.osha.gov/itadata`  
OSHA currently exposes annual summary files and case-detail files, plus technical guidance and historical downloads. citeturn15view2

2024 Summary ZIP:  
`https://www.osha.gov/sites/default/files/ITA_300A_Summary_Data_2024_through_12-31-2025.zip`

2024 Case Detail ZIP:  
`https://www.osha.gov/sites/default/files/ITA_Case_Detail_Data_2024_through_12-31-2025.zip`

2023 Summary ZIP:  
`https://www.osha.gov/sites/default/files/ITA_300A_Summary_Data_2023_through_12-31-2024.zip`

2023 Case Detail with OIICS:  
`https://www.osha.gov/sites/default/largefiles/ITA_Case_Detail_Data_2023_through_12-31-2023OIICS.zip`

Summary dictionary:  
`https://www.osha.gov/sites/default/files/ITA_Data_Dictionary.pdf`

Case-detail dictionary:  
`https://www.osha.gov/sites/default/files/case_detail_data_dictionary.pdf`  
The case-detail dictionary defines one record per injury/illness and documents incident outcome, job information, redacted narratives and OIICS fields. citeturn15view3

ITA Data User Guide:  
`https://www.osha.gov/sites/default/files/ITA_data_users_guide.pdf`  
This is the most important methodological reading before attempting longitudinal ITA analysis. citeturn15view4

**OSHA Severe Injury Reports**

Dataset information:  
`https://www.osha.gov/severeinjury`

Interactive dashboard/full-download entry point:  
`https://www.osha.gov/severe-injury-reports`

The current dashboard explicitly offers a full dataset download and states its time coverage and jurisdiction constraints. citeturn19view0 The file URL itself is generated through the dashboard rather than exposed as a stable static link in the HTML I could inspect, so the dashboard URL should be treated as the canonical download endpoint.

**BLS exposure and benchmarking data**

QCEW open data:  
`https://www.bls.gov/cew/additional-resources/open-data/home.htm`

QCEW downloadable archives:  
`https://www.bls.gov/cew/downloadable-data-files.htm`

QCEW's open-data page documents CSV slices by industry, area and establishment size and points to archives for historical years. citeturn20view2

BLS public API documentation:  
`https://www.bls.gov/developers/home.htm`  
BLS documents GET/POST access and JSON/XLSX retrieval for published time-series data. citeturn19view2

SOII nonfatal injury tables:  
`https://www.bls.gov/iif/nonfatal-injuries-and-illnesses-tables.htm` citeturn15view5

CFOI fatality tables:  
`https://www.bls.gov/iif/fatal-injuries-tables.htm` citeturn15view6

BLS copyright/public-domain statement:  
`https://www.bls.gov/bls/linksite.htm`  
BLS explicitly states that its published material is public domain except previously copyrighted photographs and illustrations. citeturn20view3

**NIOSH / CDC**

NIOSH Worker Health Charts:  
`https://wwwn.cdc.gov/NIOSH-WHC/`  
The portal supports occupational injury/illness/fatality exploration across multiple worker and event dimensions. citeturn15view9

NIOSH FACE:  
`https://www.cdc.gov/niosh/face/about/index.html`  
FACE has operated since 1982 and publishes selected fatality investigations, making it more useful for qualitative/NLP exploration than prospective injury probability modeling. citeturn15view8

**U.K. HSE**

HSE statistical table index:  
`https://www.hse.gov.uk/statistics/tables/index.htm`  
It contains RIDDOR injury data by industry, geography, age/gender, event type, injury nature and historical series. citeturn17view0

Detailed industry RIDDOR XLSX:  
`https://www.hse.gov.uk/statistics/assets/docs/ridind.xlsx`

Regional/local-authority RIDDOR XLSX:  
`https://www.hse.gov.uk/statistics/assets/docs/ridreg.xlsx`

Kind-of-accident RIDDOR XLSX:  
`https://www.hse.gov.uk/statistics/assets/docs/ridkind.xlsx`

HSE reuse/copyright policy:  
`https://www.hse.gov.uk/help/copyright.htm`  
HSE permits reuse of Crown material under the Open Government Licence, except where otherwise indicated. citeturn19view1

**Google Colab execution reference**

Colab FAQ:  
`https://research.google.com/colaboratory/faq.html`  
Google describes Colab as a hosted Jupyter service with access to compute including GPUs/TPUs, while warning that resources and usage limits are variable rather than guaranteed. citeturn17view2

For the project itself, the order of priority should be **MSHA official dictionaries first, raw MSHA files second, MSHA Part 50 reporting definitions third, and ML documentation only after the panel has been constructed**. The real intellectual work here is not choosing between XGBoost and a transformer; it is defining a valid prospective dataset from longitudinal safety records.

## Final recommendation for the portfolio

I would name the project something like:

**Predictive AI / Exploratory OSH Analytics**  
**MineRisk-Q — From Historical Safety Signals to Next-Quarter Risk**

The actual analytical story would be:

```text
OFFICIAL GOVERNMENT DATA
        ↓
5 RELATIONAL SAFETY DATASETS
        ↓
TIME-AWARE MINE-QUARTER PANEL
        ↓
LEAKAGE AUDIT
        ↓
EXPLORATORY SAFETY PATTERNS
        ↓
LOGISTIC BASELINE
        ↓
GRADIENT-BOOSTED RISK MODEL
        ↓
TEMPORAL VALIDATION
        ↓
CALIBRATION
        ↓
SHAP EXPLAINABILITY
        ↓
ERROR + SUBGROUP ANALYSIS
        ↓
OPTIONAL MINILM NARRATIVE CLUSTERS
        ↓
RISK PRIORITIZATION
```

That is considerably stronger than:

> “I trained an AI to predict accidents.”

Instead, your claim becomes:

> **I engineered a longitudinal OSH dataset from multiple official government systems, defined a prospective prediction problem, audited temporal leakage, compared interpretable and nonlinear models, tested calibration and failure modes, and translated the output into risk-oriented decision support.**

MSHA's official files make that architecture genuinely possible because injury records, exposure hours, inspections, violations and mine metadata have documented relational keys and long temporal coverage. citeturn15view0turn14view1turn14view3turn14view5turn14view7turn15view1

And on the earlier “**IndoBERT or MiniLM?**” question, my recommendation is unambiguous:

**Main predictive engine:** tabular gradient-boosted ML.  
**Interpretable baseline:** logistic regression.  
**Explainability:** SHAP + calibration + ablation + error analysis.  
**Text AI:** English MiniLM as an optional semantic-analysis layer.  
**IndoBERT:** no—save it for a genuinely Indonesian-language OSH corpus.

That combination gives the project both **technical complexity** and **methodological credibility**, while remaining realistic to build as a single reproducible Colab workflow.