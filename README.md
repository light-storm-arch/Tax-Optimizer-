# Tax Optimizer (Advisor V1)

Internal advisor-focused deterministic retirement tax planning tool for Roth conversion optimization, RMD management, and scenario-driven tax strategy analysis.

## V1 capabilities

- Annual deterministic projection (federal-only).
- Weighted objective optimization:
  - minimize projected lifetime taxes,
  - maximize projected after-tax legacy.
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

## Disclaimer

This is an educational planning tool based on assumptions and simplified tax mechanics. Outcomes may not reflect future law changes or real-world performance. It is not tax, legal, or investment advice.

## Run locally (Streamlit)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Test

```bash
pytest -q
```
