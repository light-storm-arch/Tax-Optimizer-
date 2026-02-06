import pandas as pd
import plotly.express as px
import streamlit as st

from tax_optimizer.model import HouseholdConfig, ProjectionConfig, optimize_plan, project_plan


def render_app() -> None:
    st.set_page_config(page_title="Tax Optimizer", layout="wide")
    st.title("Advisor Tax Optimizer (Deterministic V1)")
    st.caption("Educational planning tool. Results depend on assumptions and simplified tax modeling.")

    with st.sidebar:
        st.header("Household Inputs")
        current_age_1 = st.number_input("Current age (spouse 1)", value=62, min_value=40, max_value=95)
        current_age_2 = st.number_input("Current age (spouse 2)", value=60, min_value=40, max_value=95)
        death_age_1 = st.number_input("Assumed death age (spouse 1)", value=90, min_value=50, max_value=110)
        death_age_2 = st.number_input("Assumed death age (spouse 2)", value=92, min_value=50, max_value=110)

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


if __name__ == "__main__":
    render_app()
