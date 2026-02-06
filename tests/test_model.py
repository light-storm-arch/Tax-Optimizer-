from tax_optimizer.model import HouseholdConfig, ProjectionConfig, optimize_plan, project_plan


def test_baseline_projection_runs():
    hh = HouseholdConfig()
    cfg = ProjectionConfig(horizon_years=20)
    schedule = {hh.start_year + i: 0.0 for i in range(cfg.horizon_years)}
    result = project_plan(hh, cfg, schedule)

    assert len(result["projection"]) > 0
    assert result["lifetime_taxes"] >= 0
    assert result["after_tax_legacy"] >= 0


def test_optimizer_respects_conversion_cap():
    hh = HouseholdConfig()
    cfg = ProjectionConfig(horizon_years=15, annual_conversion_cap=40000, conversion_step=10000)
    result = optimize_plan(hh, cfg, iterations=2)

    schedule = result["conversion_schedule"]
    assert all(v <= 40000 for v in schedule.values())


def test_weights_change_objective_score():
    hh = HouseholdConfig()
    cfg_legacy = ProjectionConfig(horizon_years=15, weight_legacy=1.0, weight_tax=0.0)
    cfg_tax = ProjectionConfig(horizon_years=15, weight_legacy=0.0, weight_tax=1.0)
    schedule = {hh.start_year + i: 0.0 for i in range(15)}

    legacy_result = project_plan(hh, cfg_legacy, schedule)
    tax_result = project_plan(hh, cfg_tax, schedule)

    assert legacy_result["objective_score"] != tax_result["objective_score"]
