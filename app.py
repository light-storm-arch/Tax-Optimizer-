<<<<<<< codex/design-long-term-tax-planning-tool-83pl5j
import io
import re
from typing import Dict

=======
>>>>>>> main
import pandas as pd
import plotly.express as px
import streamlit as st

<<<<<<< codex/design-long-term-tax-planning-tool-83pl5j
from tax_optimizer.model import FEDERAL_BRACKETS_2026, HouseholdConfig, ProjectionConfig, optimize_plan, project_plan

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except Exception:  # runtime fallback if dependency missing
    letter = None
    canvas = None


def parse_currency(value: str, default: float) -> float:
    if not value:
        return default
    cleaned = re.sub(r"[^0-9.\-]", "", value)
    try:
        return float(cleaned)
    except ValueError:
        return default


def currency_input(label: str, key: str, default: float) -> float:
    txt = st.text_input(label, value=f"{default:,.0f}", key=key)
    return parse_currency(txt, default)


def percent_input(label: str, value: float, minv: float = 0.0, maxv: float = 100.0, step: float = 0.1) -> float:
    return st.number_input(label, min_value=minv, max_value=maxv, value=value, step=step, format="%.2f")


def build_pdf(summary: Dict[str, float], table: pd.DataFrame) -> bytes:
    if canvas is None:
        return b""
    output = io.BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    y = 760
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Tax Optimizer Analysis Export")
    y -= 24
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Projected lifetime taxes: ${summary['lifetime_taxes']:,.0f}")
    y -= 14
    c.drawString(40, y, f"Projected after-tax legacy: ${summary['after_tax_legacy']:,.0f}")
    y -= 14
    c.drawString(40, y, f"Objective score: {summary['objective_score']:.4f}")
    y -= 24
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Year-by-year highlights")
    y -= 14
    c.setFont("Helvetica", 8)

    cols = ["year", "roth_conversion", "taxable_income", "marginal_tax_rate", "total_tax", "net_worth_end"]
    preview = table[cols].head(20)
    for _, row in preview.iterrows():
        line = (
            f"{int(row['year'])} | Conv ${row['roth_conversion']:,.0f} | Taxable ${row['taxable_income']:,.0f} | "
            f"Marg {row['marginal_tax_rate']*100:.0f}% | Tax ${row['total_tax']:,.0f} | NW ${row['net_worth_end']:,.0f}"
        )
        c.drawString(40, y, line)
        y -= 12
        if y < 40:
            c.showPage()
            y = 760
            c.setFont("Helvetica", 8)

    c.save()
    return output.getvalue()
=======
from tax_optimizer.model import HouseholdConfig, ProjectionConfig, optimize_plan, project_plan
>>>>>>> main


def render_app() -> None:
    st.set_page_config(page_title="Tax Optimizer", layout="wide")
<<<<<<< codex/design-long-term-tax-planning-tool-83pl5j
    st.markdown("""
        <style>
        .stApp {background: #f7f9fc;}
        .block-container {padding-top: 1rem;}
        </style>
    """, unsafe_allow_html=True)

    st.title("Advisor Tax Optimizer")
    st.caption("Educational planning tool. Results depend on assumptions and simplified tax modeling.")

    bracket_options = [f"Top of {int(rate*100)}% bracket" for _, rate in FEDERAL_BRACKETS_2026["joint"]]
    bracket_rate_map = {label: FEDERAL_BRACKETS_2026["joint"][idx][1] for idx, label in enumerate(bracket_options)}

    with st.sidebar.form("inputs"):
        st.subheader("Household")
=======
    st.title("Advisor Tax Optimizer (Deterministic V1)")
    st.caption("Educational planning tool. Results depend on assumptions and simplified tax modeling.")

    with st.sidebar:
        st.header("Household Inputs")
>>>>>>> main
        current_age_1 = st.number_input("Current age (spouse 1)", value=62, min_value=40, max_value=95)
        current_age_2 = st.number_input("Current age (spouse 2)", value=60, min_value=40, max_value=95)
        death_age_1 = st.number_input("Assumed death age (spouse 1)", value=90, min_value=50, max_value=110)
        death_age_2 = st.number_input("Assumed death age (spouse 2)", value=92, min_value=50, max_value=110)
<<<<<<< codex/design-long-term-tax-planning-tool-83pl5j
        ss_age_1 = st.slider("Social Security claim age (spouse 1)", 62, 70, 67)
        ss_age_2 = st.slider("Social Security claim age (spouse 2)", 62, 70, 67)
        ss_benefit_1 = currency_input("Annual SS benefit at claim (spouse 1)", "ss1", 32000.0)
        ss_benefit_2 = currency_input("Annual SS benefit at claim (spouse 2)", "ss2", 25000.0)

        st.subheader("Cash Flow & Balances")
        pension_income = currency_input("Annual pension income", "pension", 0.0)
        other_income = currency_input("Other annual ordinary income", "other", 0.0)
        spending_need = currency_input("Annual after-tax spending need", "spending", 120000.0)
        trad_balance = currency_input("Tax-deferred (IRA/401k)", "trad", 1500000.0)
        roth_balance = currency_input("Roth", "roth", 300000.0)
        taxable_balance = currency_input("Taxable", "taxable", 500000.0)

        st.subheader("Projection & Objective")
        annual_return_pct = percent_input("Annual portfolio return (%)", 5.0, 0.0, 12.0)
        inflation_pct = percent_input("Inflation (%)", 2.5, 0.0, 6.0)
        bracket_inflation_pct = percent_input("Tax bracket inflation (%)", 2.5, 0.0, 6.0)
        horizon_years = st.slider("Projection horizon (years)", 10, 45, 35)
        legacy_weight_pct = st.slider("Weight: maximize after-tax legacy (%)", 0, 100, 60)

        st.subheader("Roth Conversion Policy")
        conversion_min_age = st.number_input("Min conversion age", value=60, min_value=40, max_value=90)
        conversion_max_age = st.number_input("Max conversion age", value=75, min_value=40, max_value=95)
        bracket_target = st.selectbox("Roth conversion upper bound", options=bracket_options, index=2)
        conversion_step = currency_input("Optimization conversion step ($)", "conv_step", 5000.0)
        run_mode = st.radio("Run type", options=["Optimized Strategy", "Baseline (No Conversions)"])
        submitted = st.form_submit_button("Run Analysis", type="primary")

    if submitted:
        household = HouseholdConfig(
            current_age_1=int(current_age_1),
            current_age_2=int(current_age_2),
            death_age_1=int(death_age_1),
            death_age_2=int(death_age_2),
            social_security_age_1=int(ss_age_1),
            social_security_age_2=int(ss_age_2),
            social_security_benefit_1=float(ss_benefit_1),
            social_security_benefit_2=float(ss_benefit_2),
            pension_income=float(pension_income),
            other_ordinary_income=float(other_income),
            annual_spending_need=float(spending_need),
            trad_balance=float(trad_balance),
            roth_balance=float(roth_balance),
            taxable_balance=float(taxable_balance),
        )

        cfg = ProjectionConfig(
            annual_return=float(annual_return_pct / 100),
            inflation=float(inflation_pct / 100),
            bracket_inflation=float(bracket_inflation_pct / 100),
            horizon_years=int(horizon_years),
            weight_legacy=legacy_weight_pct / 100,
            weight_tax=(100 - legacy_weight_pct) / 100,
            conversion_min_age=int(conversion_min_age),
            conversion_max_age=int(conversion_max_age),
            annual_conversion_cap=household.trad_balance,
            conversion_step=float(max(1000.0, conversion_step)),
            conversion_bracket_target_rate=bracket_rate_map[bracket_target],
        )

        if run_mode == "Baseline (No Conversions)":
            zero_schedule = {household.start_year + i: 0.0 for i in range(cfg.horizon_years)}
            result = project_plan(household, cfg, zero_schedule)
        else:
            result = optimize_plan(household, cfg)

        st.session_state["result"] = result
        st.session_state["cfg"] = cfg
        st.session_state["run_mode"] = run_mode

    result = st.session_state.get("result")
    if not result:
        st.info("Set inputs in the left panel and click **Run Analysis**.")
        return

    projection = pd.DataFrame(result["projection"])

    k1, k2, k3 = st.columns(3)
    k1.metric("Projected lifetime taxes", f"${result['lifetime_taxes']:,.0f}")
    k2.metric("Projected after-tax legacy", f"${result['after_tax_legacy']:,.0f}")
    k3.metric("Objective score", f"{result['objective_score']:.4f}")

    st.markdown(
        "**Recommendation rationale:** Strategy maximizes weighted objective and constrains Roth conversions to your selected bracket cap."
    )

    scenario_enabled = st.checkbox("Add comparison scenario")
    comparison_df = None
    if scenario_enabled:
        c1, c2, c3 = st.columns(3)
        with c1:
            alt_ss_age_1 = st.slider("Alt SS age (spouse 1)", 62, 70, 67, key="alt_a1")
            alt_ss_age_2 = st.slider("Alt SS age (spouse 2)", 62, 70, 67, key="alt_a2")
        with c2:
            alt_death_age_1 = st.number_input("Alt death age (spouse 1)", value=90, key="alt_d1")
            alt_death_age_2 = st.number_input("Alt death age (spouse 2)", value=92, key="alt_d2")
        with c3:
            alt_return = percent_input("Alt annual return (%)", 5.0, 0.0, 12.0)
            alt_infl = percent_input("Alt inflation (%)", 2.5, 0.0, 6.0)

        if st.button("Run comparison scenario"):
            base_cfg = st.session_state["cfg"]
            base_hh = HouseholdConfig()
            # use latest input values directly from sidebar session fields
            base_hh.current_age_1 = int(current_age_1)
            base_hh.current_age_2 = int(current_age_2)
            base_hh.death_age_1 = int(death_age_1)
            base_hh.death_age_2 = int(death_age_2)
            base_hh.social_security_age_1 = int(ss_age_1)
            base_hh.social_security_age_2 = int(ss_age_2)
            base_hh.social_security_benefit_1 = float(ss_benefit_1)
            base_hh.social_security_benefit_2 = float(ss_benefit_2)
            base_hh.pension_income = float(pension_income)
            base_hh.other_ordinary_income = float(other_income)
            base_hh.annual_spending_need = float(spending_need)
            base_hh.trad_balance = float(trad_balance)
            base_hh.roth_balance = float(roth_balance)
            base_hh.taxable_balance = float(taxable_balance)

            alt_hh = HouseholdConfig(**{**base_hh.__dict__, "social_security_age_1": int(alt_ss_age_1), "social_security_age_2": int(alt_ss_age_2), "death_age_1": int(alt_death_age_1), "death_age_2": int(alt_death_age_2)})
            alt_cfg = ProjectionConfig(**{**base_cfg.__dict__, "annual_return": alt_return / 100, "inflation": alt_infl / 100})
            if st.session_state["run_mode"] == "Baseline (No Conversions)":
                alt_result = project_plan(alt_hh, alt_cfg, {alt_hh.start_year + i: 0.0 for i in range(alt_cfg.horizon_years)})
            else:
                alt_result = optimize_plan(alt_hh, alt_cfg)
            st.session_state["alt_result"] = alt_result

        alt_result = st.session_state.get("alt_result")
        if alt_result:
            st.dataframe(pd.DataFrame([
                {"Scenario": "Base", "Lifetime Taxes": result["lifetime_taxes"], "After-Tax Legacy": result["after_tax_legacy"], "Objective Score": result["objective_score"]},
                {"Scenario": "Alternative", "Lifetime Taxes": alt_result["lifetime_taxes"], "After-Tax Legacy": alt_result["after_tax_legacy"], "Objective Score": alt_result["objective_score"]},
            ]), hide_index=True)
            comparison_df = pd.DataFrame(alt_result["projection"])
            comparison_df["scenario"] = "Alternative"

    display_df = projection.copy()
    display_df["marginal_tax_rate"] = display_df["marginal_tax_rate"].map(lambda x: f"{x*100:.0f}%")
    money_cols = [c for c in display_df.columns if c not in {"year", "age_1", "age_2", "filing_status", "marginal_tax_rate"}]
    for col in money_cols:
        display_df[col] = display_df[col].map(lambda x: f"${x:,.0f}")

    tab1, tab2, tab3 = st.tabs(["Projection Table", "Charts", "Year Detail"])
    with tab1:
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    chart_df = projection.copy()
    chart_df["scenario"] = "Base"
    if comparison_df is not None:
        chart_df = pd.concat([chart_df, comparison_df], ignore_index=True)

    with tab2:
        st.plotly_chart(px.line(chart_df, x="year", y="total_tax", color="scenario", title="Projected Total Tax by Year"), use_container_width=True)
        st.plotly_chart(px.bar(chart_df, x="year", y="roth_conversion", color="scenario", title="Roth Conversions by Year"), use_container_width=True)
        balances = chart_df.melt(id_vars=["year", "scenario"], value_vars=["trad_end", "roth_end", "taxable_end"], var_name="account", value_name="balance")
        st.plotly_chart(px.line(balances, x="year", y="balance", color="scenario", facet_col="account", title="Account Balances by Year"), use_container_width=True)

    with tab3:
        years = projection["year"].tolist()
        selected_year = st.selectbox("Select a year for detailed calculations", years)
        detail = projection[projection["year"] == selected_year].iloc[0]
        detail_df = pd.DataFrame({"Metric": detail.index, "Value": detail.values})
        detail_df["Value"] = detail_df.apply(
            lambda r: f"{r['Value']*100:.0f}%" if r["Metric"] == "marginal_tax_rate" else (f"${r['Value']:,.2f}" if isinstance(r["Value"], float) else r["Value"]),
            axis=1,
        )
        st.dataframe(detail_df, hide_index=True, use_container_width=True)

    pdf_bytes = build_pdf(result, projection)
    if pdf_bytes:
        st.download_button(
            "Export analysis to PDF",
            data=pdf_bytes,
            file_name="tax_optimizer_analysis.pdf",
            mime="application/pdf",
        )
    else:
        st.warning("PDF export dependency unavailable. Install `reportlab` to enable PDF downloads.")

    st.markdown("---")
    st.caption("Disclaimer: This educational model uses assumptions and simplified tax mechanics. Validate with current law and professional judgment before acting.")
=======

        ss_age_1 = st.slider("Social Security claim age (spouse 1)", 62, 70, 67)
        ss_age_2 = st.slider("Social Security claim age (spouse 2)", 62, 70, 67)
        ss_benefit_1 = st.number_input("Annual SS benefit at claim (spouse 1)", value=32000.0, step=1000.0)
        ss_benefit_2 = st.number_input("Annual SS benefit at claim (spouse 2)", value=25000.0, step=1000.0)

        pension_income = st.number_input("Annual pension income", value=0.0, step=1000.0)
        other_income = st.number_input("Other annual ordinary income", value=0.0, step=1000.0)
        spending_need = st.number_input("Annual after-tax spending need", value=120000.0, step=5000.0)

        st.header("Account Balances")
        trad_balance = st.number_input("Tax-deferred (IRA/401k)", value=1500000.0, step=10000.0)
        roth_balance = st.number_input("Roth", value=300000.0, step=10000.0)
        taxable_balance = st.number_input("Taxable", value=500000.0, step=10000.0)

        st.header("Projection & Objective")
        annual_return = st.slider("Annual portfolio return", 0.0, 0.12, 0.05, 0.005)
        inflation = st.slider("Inflation", 0.0, 0.06, 0.025, 0.0025)
        bracket_inflation = st.slider("Tax bracket inflation", 0.0, 0.06, 0.025, 0.0025)
        horizon_years = st.slider("Projection horizon (years)", 10, 45, 35)

        st.subheader("Objective Weighting")
        legacy_weight_pct = st.slider("Weight: maximize after-tax legacy (%)", 0, 100, 60)
        tax_weight_pct = 100 - legacy_weight_pct
        st.write(f"Weight: minimize lifetime taxes (%) = {tax_weight_pct}")

        st.header("Roth Conversion Policy")
        conversion_min_age = st.number_input("Min conversion age", value=60, min_value=40, max_value=90)
        conversion_max_age = st.number_input("Max conversion age", value=75, min_value=40, max_value=95)
        annual_conversion_cap = st.number_input("Annual conversion upper bound", value=150000.0, step=5000.0)
        conversion_step = st.number_input("Conversion search step", value=5000.0, step=1000.0)

    household = HouseholdConfig(
        current_age_1=int(current_age_1),
        current_age_2=int(current_age_2),
        death_age_1=int(death_age_1),
        death_age_2=int(death_age_2),
        social_security_age_1=int(ss_age_1),
        social_security_age_2=int(ss_age_2),
        social_security_benefit_1=float(ss_benefit_1),
        social_security_benefit_2=float(ss_benefit_2),
        pension_income=float(pension_income),
        other_ordinary_income=float(other_income),
        annual_spending_need=float(spending_need),
        trad_balance=float(trad_balance),
        roth_balance=float(roth_balance),
        taxable_balance=float(taxable_balance),
    )

    cfg = ProjectionConfig(
        annual_return=float(annual_return),
        inflation=float(inflation),
        bracket_inflation=float(bracket_inflation),
        horizon_years=int(horizon_years),
        weight_legacy=legacy_weight_pct / 100,
        weight_tax=tax_weight_pct / 100,
        conversion_min_age=int(conversion_min_age),
        conversion_max_age=int(conversion_max_age),
        annual_conversion_cap=float(annual_conversion_cap),
        conversion_step=float(conversion_step),
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        run_opt = st.button("Optimize conversion strategy", type="primary")
    with col2:
        run_zero = st.button("Run baseline (no conversions)")

    if run_opt or run_zero:
        if run_zero:
            zero_schedule = {household.start_year + i: 0.0 for i in range(cfg.horizon_years)}
            result = project_plan(household, cfg, zero_schedule)
            strategy_name = "Baseline (No Conversions)"
        else:
            result = optimize_plan(household, cfg)
            strategy_name = "Optimized Strategy"

        projection = pd.DataFrame(result["projection"])
        st.subheader(strategy_name)

        m1, m2, m3 = st.columns(3)
        m1.metric("Projected lifetime taxes", f"${result['lifetime_taxes']:,.0f}")
        m2.metric("Projected after-tax legacy", f"${result['after_tax_legacy']:,.0f}")
        m3.metric("Objective score", f"{result['objective_score']:.4f}")

        st.markdown(
            "**Recommendation rationale:** The optimizer searches annual Roth conversion levels within your age window and cap, "
            "then selects the schedule that best balances lifetime taxes vs after-tax legacy using your selected weights."
        )

        st.subheader("Scenario Analysis")
        scenario_enabled = st.checkbox("Add comparison scenario")

        comparison_df = None
        if scenario_enabled:
            c1, c2, c3 = st.columns(3)
            with c1:
                alt_ss_age_1 = st.slider("Alt SS age (spouse 1)", 62, 70, int(ss_age_1), key="a1")
                alt_ss_age_2 = st.slider("Alt SS age (spouse 2)", 62, 70, int(ss_age_2), key="a2")
            with c2:
                alt_death_age_1 = st.number_input("Alt death age (spouse 1)", value=int(death_age_1), key="d1")
                alt_death_age_2 = st.number_input("Alt death age (spouse 2)", value=int(death_age_2), key="d2")
            with c3:
                alt_return = st.slider("Alt annual return", 0.0, 0.12, float(annual_return), 0.005, key="r1")
                alt_infl = st.slider("Alt inflation", 0.0, 0.06, float(inflation), 0.0025, key="i1")

            alt_household = HouseholdConfig(
                **{
                    **household.__dict__,
                    "social_security_age_1": int(alt_ss_age_1),
                    "social_security_age_2": int(alt_ss_age_2),
                    "death_age_1": int(alt_death_age_1),
                    "death_age_2": int(alt_death_age_2),
                }
            )
            alt_cfg = ProjectionConfig(**{**cfg.__dict__, "annual_return": float(alt_return), "inflation": float(alt_infl)})

            if run_zero:
                alt_result = project_plan(
                    alt_household,
                    alt_cfg,
                    {alt_household.start_year + i: 0.0 for i in range(alt_cfg.horizon_years)},
                )
            else:
                alt_result = optimize_plan(alt_household, alt_cfg)

            st.write(
                pd.DataFrame(
                    [
                        {
                            "Scenario": "Base",
                            "Lifetime Taxes": result["lifetime_taxes"],
                            "After-Tax Legacy": result["after_tax_legacy"],
                            "Objective Score": result["objective_score"],
                        },
                        {
                            "Scenario": "Alternative",
                            "Lifetime Taxes": alt_result["lifetime_taxes"],
                            "After-Tax Legacy": alt_result["after_tax_legacy"],
                            "Objective Score": alt_result["objective_score"],
                        },
                    ]
                )
            )
            comparison_df = pd.DataFrame(alt_result["projection"])
            comparison_df["scenario"] = "Alternative"

        st.subheader("Year-by-Year Output Table")
        st.dataframe(projection, use_container_width=True, hide_index=True)

        chart_df = projection.copy()
        chart_df["scenario"] = "Base"
        if comparison_df is not None:
            chart_df = pd.concat([chart_df, comparison_df], ignore_index=True)

        st.subheader("Charts")
        if not chart_df.empty:
            line2 = px.line(chart_df, x="year", y="total_tax", color="scenario", title="Projected Total Tax by Year")
            st.plotly_chart(line2, use_container_width=True)

            line3 = px.bar(chart_df, x="year", y="roth_conversion", color="scenario", title="Roth Conversions by Year")
            st.plotly_chart(line3, use_container_width=True)

            balances = chart_df.melt(
                id_vars=["year", "scenario"],
                value_vars=["trad_end", "roth_end", "taxable_end"],
                var_name="account",
                value_name="balance",
            )
            line1 = px.line(
                balances,
                x="year",
                y="balance",
                color="scenario",
                facet_col="account",
                title="Account Balances by Year",
            )
            st.plotly_chart(line1, use_container_width=True)

    st.markdown("---")
    st.caption(
        "Disclaimer: This educational model uses assumptions and simplified tax mechanics. "
        "Validate with current law and professional judgment before acting."
    )
>>>>>>> main


if __name__ == "__main__":
    render_app()
