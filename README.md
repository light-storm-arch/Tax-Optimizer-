# Tax Optimizer (Advisor V1)

Internal advisor-focused deterministic retirement tax planning tool for Roth conversion optimization, RMD management, and scenario-driven tax strategy analysis.

## V1 capabilities

- Annual deterministic projection (federal-only).
- Weighted objective optimization:
  - minimize projected lifetime taxes,
  - maximize projected after-tax legacy.
<<<<<<< codex/design-long-term-tax-planning-tool-83pl5j
- Projection inputs and outputs shown with currency formatting.
- Percent-based controls for return/inflation assumptions.
- Roth conversion policy uses bracket-based conversion cap (select target tax bracket).
- Output includes yearly marginal tax rate and detailed per-year calculation drilldown.
- Scenario analysis no longer clears base results; run comparison from a dedicated action button.
- Exportable PDF summary of the analysis.
=======
- Configurable objective weights (legacy vs tax minimization).
- Roth conversion constraints:
  - conversion age window,
  - annual conversion upper bound,
  - optimization step size.
- Uses 2026 bracket assumptions and inflates brackets annually (default 2.5%, user-adjustable).
- Advanced planning inputs include Social Security timing, spouse longevity assumptions, return/inflation assumptions, and spending requirement.
- Advisor Streamlit interface with:
  - recommendation and rationale,
  - key metrics,
  - scenario analysis,
  - long year-by-year output table,
  - charts for taxes, balances, and conversions.
>>>>>>> main

## Disclaimer

This is an educational planning tool based on assumptions and simplified tax mechanics. Outcomes may not reflect future law changes or real-world performance. It is not tax, legal, or investment advice.

## Run locally (Streamlit)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
<<<<<<< codex/design-long-term-tax-planning-tool-83pl5j
streamlit run streamlit_app.py
=======
streamlit run app.py
>>>>>>> main
```

Then open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Streamlit Cloud

<<<<<<< codex/design-long-term-tax-planning-tool-83pl5j
- App file: `streamlit_app.py`.
- Dependencies: `requirements.txt`.
- Optional config: `.streamlit/config.toml`.
=======
- App file: `streamlit_app.py` (recommended cloud entrypoint).
- Dependencies: `requirements.txt`.
- Optional config is in `.streamlit/config.toml`.

If you previously saw an error referencing `wsgiref.simple_server.make_server`, that was from an old WSGI version of this app. This repository is now Streamlit-native and should be launched with `streamlit run ...`, not `python app.py` on a server process manager.
>>>>>>> main

## Test

```bash
pytest -q
```
