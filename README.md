# Tax Optimizer (Advisor V1)

Internal advisor-focused deterministic retirement tax planning tool for Roth conversion optimization, RMD management, and scenario-driven tax strategy analysis.

## V1 capabilities

- Annual deterministic projection (federal-only).
- Weighted objective optimization:
  - minimize projected lifetime taxes,
  - maximize projected after-tax legacy.
- Projection inputs and outputs shown with currency formatting.
- Percent-based controls for return/inflation assumptions.
- Roth conversion policy uses bracket-based conversion cap (select target tax bracket).
- Output includes yearly marginal tax rate and detailed per-year calculation drilldown.
- Scenario analysis no longer clears base results; run comparison from a dedicated action button.
- Exportable PDF summary of the analysis.

## Disclaimer

This is an educational planning tool based on assumptions and simplified tax mechanics. Outcomes may not reflect future law changes or real-world performance. It is not tax, legal, or investment advice.

## Run locally (Streamlit)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Streamlit Cloud

- App file: `streamlit_app.py`.
- Dependencies: `requirements.txt`.
- Optional config: `.streamlit/config.toml`.

## Test

```bash
pytest -q
```
