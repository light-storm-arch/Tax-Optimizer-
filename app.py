from html import escape
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from tax_optimizer.model import HouseholdConfig, ProjectionConfig, optimize_plan


def get_float(data, key, default):
    try:
        return float(data.get(key, [default])[0])
    except (TypeError, ValueError):
        return float(default)


def get_int(data, key, default):
    return int(get_float(data, key, default))


def render_table(rows):
    if not rows:
        return "<p>No rows generated.</p>"
    headers = list(rows[0].keys())
    thead = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
        tds = "".join(f"<td>{row[h]:,.2f}</td>" if isinstance(row[h], float) else f"<td>{escape(str(row[h]))}</td>" for h in headers)
        body_rows.append(f"<tr>{tds}</tr>")
    return f"<table border='1' cellpadding='4' cellspacing='0'><thead><tr>{thead}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def app(environ, start_response):
    if environ["REQUEST_METHOD"] == "POST":
        size = int(environ.get("CONTENT_LENGTH", 0) or 0)
        payload = environ["wsgi.input"].read(size).decode("utf-8")
        form = parse_qs(payload)
    else:
        form = parse_qs(environ.get("QUERY_STRING", ""))

    hh = HouseholdConfig(
        current_age_1=get_int(form, "current_age_1", 62),
        current_age_2=get_int(form, "current_age_2", 60),
        death_age_1=get_int(form, "death_age_1", 90),
        death_age_2=get_int(form, "death_age_2", 92),
        social_security_age_1=get_int(form, "ss_age_1", 67),
        social_security_age_2=get_int(form, "ss_age_2", 67),
        social_security_benefit_1=get_float(form, "ss_benefit_1", 32000),
        social_security_benefit_2=get_float(form, "ss_benefit_2", 25000),
        pension_income=get_float(form, "pension", 0),
        other_ordinary_income=get_float(form, "other", 0),
        annual_spending_need=get_float(form, "spending", 120000),
        trad_balance=get_float(form, "trad", 1500000),
        roth_balance=get_float(form, "roth", 300000),
        taxable_balance=get_float(form, "taxable", 500000),
    )
    legacy_weight_pct = get_float(form, "legacy_weight", 60)
    cfg = ProjectionConfig(
        annual_return=get_float(form, "annual_return", 0.05),
        inflation=get_float(form, "inflation", 0.025),
        bracket_inflation=get_float(form, "bracket_inflation", 0.025),
        horizon_years=get_int(form, "horizon", 35),
        weight_legacy=legacy_weight_pct / 100,
        weight_tax=(100 - legacy_weight_pct) / 100,
        conversion_min_age=get_int(form, "conv_min_age", 60),
        conversion_max_age=get_int(form, "conv_max_age", 75),
        annual_conversion_cap=get_float(form, "conv_cap", 150000),
        conversion_step=get_float(form, "conv_step", 5000),
    )

    result = optimize_plan(hh, cfg)
    rows = result["projection"]

    html = f"""
    <html><head><title>Tax Optimizer</title></head><body>
    <h1>Advisor Tax Optimizer (Deterministic V1)</h1>
    <p><b>Disclaimer:</b> Educational planning tool with simplified assumptions; validate before implementation.</p>
    <form method='post'>
      <h3>Inputs</h3>
      Current age 1 <input name='current_age_1' value='{hh.current_age_1}' />
      Current age 2 <input name='current_age_2' value='{hh.current_age_2}' />
      Death age 1 <input name='death_age_1' value='{hh.death_age_1}' />
      Death age 2 <input name='death_age_2' value='{hh.death_age_2}' /><br/>
      SS age 1 <input name='ss_age_1' value='{hh.social_security_age_1}' />
      SS age 2 <input name='ss_age_2' value='{hh.social_security_age_2}' />
      SS benefit 1 <input name='ss_benefit_1' value='{hh.social_security_benefit_1}' />
      SS benefit 2 <input name='ss_benefit_2' value='{hh.social_security_benefit_2}' /><br/>
      Trad <input name='trad' value='{hh.trad_balance}' />
      Roth <input name='roth' value='{hh.roth_balance}' />
      Taxable <input name='taxable' value='{hh.taxable_balance}' /><br/>
      Spending <input name='spending' value='{hh.annual_spending_need}' />
      Return <input name='annual_return' value='{cfg.annual_return}' />
      Inflation <input name='inflation' value='{cfg.inflation}' />
      Bracket inflation <input name='bracket_inflation' value='{cfg.bracket_inflation}' /><br/>
      Legacy objective weight (%) <input name='legacy_weight' value='{legacy_weight_pct}' />
      Conversion min age <input name='conv_min_age' value='{cfg.conversion_min_age}' />
      Conversion max age <input name='conv_max_age' value='{cfg.conversion_max_age}' />
      Conversion cap <input name='conv_cap' value='{cfg.annual_conversion_cap}' />
      Conversion step <input name='conv_step' value='{cfg.conversion_step}' /><br/>
      Horizon <input name='horizon' value='{cfg.horizon_years}' />
      <button type='submit'>Optimize</button>
    </form>

    <h3>Recommendation & Rationale</h3>
    <p>Annual Roth conversions are optimized across your configured age range and annual cap to maximize weighted objective score: after-tax legacy (weight={cfg.weight_legacy:.2f}) and tax minimization (weight={cfg.weight_tax:.2f}).</p>

    <h3>Metrics</h3>
    <ul>
      <li>Projected lifetime taxes: ${result['lifetime_taxes']:,.0f}</li>
      <li>Projected after-tax legacy: ${result['after_tax_legacy']:,.0f}</li>
      <li>Objective score: {result['objective_score']:.4f}</li>
    </ul>

    <h3>Year-by-Year Projection</h3>
    {render_table(rows)}
    </body></html>
    """

    body = html.encode("utf-8")
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body)))])
    return [body]


if __name__ == "__main__":
    server = make_server("0.0.0.0", 8000, app)
    print("Serving on http://0.0.0.0:8000")
    server.serve_forever()
