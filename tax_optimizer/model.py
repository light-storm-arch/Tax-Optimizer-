from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

FEDERAL_BRACKETS_2026 = {
    "joint": [
        (0, 0.10), (24000, 0.12), (96000, 0.22), (205000, 0.24), (390000, 0.32), (490000, 0.35), (735000, 0.37)
    ],
    "single": [
        (0, 0.10), (12000, 0.12), (48000, 0.22), (102500, 0.24), (195000, 0.32), (245000, 0.35), (367500, 0.37)
    ],
}
STANDARD_DEDUCTION_2026 = {"joint": 30000.0, "single": 15000.0}
IRMAA_THRESHOLDS_2026 = {
    "single": [106000, 133000, 167000, 200000, 500000],
    "joint": [212000, 266000, 334000, 400000, 750000],
}
IRMAA_MONTHLY_SURCHARGE = [0, 70, 175, 280, 385, 420]
UNIFORM_LIFETIME_DIVISOR = {73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2}


@dataclass
class HouseholdConfig:
    start_year: int = 2026
    current_age_1: int = 62
    current_age_2: int = 60
    death_age_1: int = 90
    death_age_2: int = 92
    social_security_age_1: int = 67
    social_security_age_2: int = 67
    social_security_benefit_1: float = 32000.0
    social_security_benefit_2: float = 25000.0
    pension_income: float = 0.0
    other_ordinary_income: float = 0.0
    annual_spending_need: float = 120000.0
    trad_balance: float = 1500000.0
    roth_balance: float = 300000.0
    taxable_balance: float = 500000.0


@dataclass
class ProjectionConfig:
    annual_return: float = 0.05
    inflation: float = 0.025
    bracket_inflation: float = 0.025
    horizon_years: int = 35
    rmd_start_age: int = 73
    weight_legacy: float = 0.6
    weight_tax: float = 0.4
    conversion_min_age: int = 60
    conversion_max_age: int = 75
    annual_conversion_cap: float = 150000.0
    conversion_step: float = 5000.0
    conversion_bracket_target_rate: Optional[float] = None


def inflate(value: float, rate: float, year_offset: int) -> float:
    return value * ((1 + rate) ** year_offset)


def tax_from_brackets(taxable_income: float, brackets: List[Tuple[float, float]]) -> float:
    tax = 0.0
    for i, (start, rate) in enumerate(brackets):
        nxt = brackets[i + 1][0] if i + 1 < len(brackets) else float("inf")
        if taxable_income > start:
            tax += max(0.0, min(taxable_income, nxt) - start) * rate
    return tax


def marginal_rate(taxable_income: float, brackets: List[Tuple[float, float]]) -> float:
    rate = brackets[0][1]
    for start, r in brackets:
        if taxable_income >= start:
            rate = r
        else:
            break
    return rate


def bracket_top_for_rate(brackets: List[Tuple[float, float]], target_rate: float) -> float:
    for i, (_, rate) in enumerate(brackets):
        if rate == target_rate:
            if i + 1 < len(brackets):
                return brackets[i + 1][0]
            return float("inf")
    return float("inf")


def taxable_social_security(total_benefit: float, provisional_income: float, filing_status: str) -> float:
    if total_benefit <= 0:
        return 0.0
    base1, base2 = (32000, 44000) if filing_status == "joint" else (25000, 34000)
    if provisional_income <= base1:
        return 0.0
    if provisional_income <= base2:
        return min(0.5 * total_benefit, 0.5 * (provisional_income - base1))
    tier1 = min(0.5 * total_benefit, 0.5 * (base2 - base1))
    tier2 = min(0.85 * total_benefit - tier1, 0.85 * (provisional_income - base2))
    return max(0.0, min(0.85 * total_benefit, tier1 + tier2))


def irmaa_surcharge(magi: float, filing_status: str, covered_people: int) -> float:
    tier = 0
    for idx, th in enumerate(IRMAA_THRESHOLDS_2026[filing_status], start=1):
        if magi > th:
            tier = idx
    return IRMAA_MONTHLY_SURCHARGE[tier] * 12 * covered_people


def get_divisor(age: int) -> float:
    if age in UNIFORM_LIFETIME_DIVISOR:
        return UNIFORM_LIFETIME_DIVISOR[age]
    if age > 90:
        return max(2.0, UNIFORM_LIFETIME_DIVISOR[90] - 0.6 * (age - 90))
    return UNIFORM_LIFETIME_DIVISOR[73]


def _simulate(h: HouseholdConfig, cfg: ProjectionConfig, schedule: Dict[int, float]):
    trad, roth, taxable = h.trad_balance, h.roth_balance, h.taxable_balance
    spending = h.annual_spending_need
    lifetime_taxes = 0.0
    rows: List[Dict[str, float]] = []

    for i in range(cfg.horizon_years):
        year = h.start_year + i
        age1, age2 = h.current_age_1 + i, h.current_age_2 + i
        alive1, alive2 = age1 <= h.death_age_1, age2 <= h.death_age_2
        if not alive1 and not alive2:
            break

        filing = "joint" if alive1 and alive2 else "single"
        covered = int(alive1) + int(alive2)

        trad *= 1 + cfg.annual_return
        roth *= 1 + cfg.annual_return
        taxable *= 1 + cfg.annual_return
        if i > 0:
            spending *= 1 + cfg.inflation

        ss1 = h.social_security_benefit_1 * ((1 + cfg.inflation) ** i) if alive1 and age1 >= h.social_security_age_1 else 0.0
        ss2 = h.social_security_benefit_2 * ((1 + cfg.inflation) ** i) if alive2 and age2 >= h.social_security_age_2 else 0.0
        total_ss = ss1 + ss2
        pension = h.pension_income * ((1 + cfg.inflation) ** i)
        other = h.other_ordinary_income * ((1 + cfg.inflation) ** i)

        oldest = max(age1 if alive1 else 0, age2 if alive2 else 0)
        rmd = trad / get_divisor(oldest) if oldest >= cfg.rmd_start_age and trad > 0 else 0.0

        brackets = [(inflate(start, cfg.bracket_inflation, i), rate) for start, rate in FEDERAL_BRACKETS_2026[filing]]
        std_ded = inflate(STANDARD_DEDUCTION_2026[filing], cfg.bracket_inflation, i)

        in_window = cfg.conversion_min_age <= oldest <= cfg.conversion_max_age
        conversion_limit = cfg.annual_conversion_cap

        provisional_base = pension + other + rmd + 0.5 * total_ss
        taxable_ss_base = taxable_social_security(total_ss, provisional_base, filing)
        taxable_income_base = max(0.0, pension + other + rmd + taxable_ss_base - std_ded)

        if cfg.conversion_bracket_target_rate is not None:
            bracket_top = bracket_top_for_rate(brackets, cfg.conversion_bracket_target_rate)
            if bracket_top != float("inf"):
                conversion_limit = min(conversion_limit, max(0.0, bracket_top - taxable_income_base))

        conversion = min(schedule.get(year, 0.0), conversion_limit, max(0.0, trad - rmd)) if in_window else 0.0

        provisional = pension + other + rmd + conversion + 0.5 * total_ss
        taxable_ss = taxable_social_security(total_ss, provisional, filing)

        gross_ordinary = pension + other + rmd + conversion + taxable_ss
        taxable_income = max(0.0, gross_ordinary - std_ded)
        income_tax = tax_from_brackets(taxable_income, brackets)
        current_marginal_rate = marginal_rate(taxable_income, brackets)

        magi = pension + other + rmd + conversion + total_ss
        surcharge = irmaa_surcharge(magi, filing, covered)
        total_tax = income_tax + surcharge
        lifetime_taxes += total_tax

        trad -= rmd + conversion
        roth += conversion

        cash_needed = spending + total_tax - (total_ss + pension + other + rmd)
        wd_taxable = min(taxable, max(0.0, cash_needed))
        taxable -= wd_taxable
        cash_needed -= wd_taxable

        wd_trad = min(trad, max(0.0, cash_needed))
        trad -= wd_trad
        cash_needed -= wd_trad

        wd_roth = min(roth, max(0.0, cash_needed))
        roth -= wd_roth

        rows.append({
            "year": year,
            "age_1": age1,
            "age_2": age2,
            "filing_status": filing,
            "social_security": total_ss,
            "pension_income": pension,
            "other_income": other,
            "provisional_income": provisional,
            "taxable_social_security": taxable_ss,
            "standard_deduction": std_ded,
            "gross_ordinary_income": gross_ordinary,
            "rmd": rmd,
            "roth_conversion": conversion,
            "taxable_income": taxable_income,
            "marginal_tax_rate": current_marginal_rate,
            "federal_tax": income_tax,
            "irmaa_proxy": surcharge,
            "total_tax": total_tax,
            "spending_need": spending,
            "taxable_withdrawal": wd_taxable,
            "trad_withdrawal": wd_trad,
            "roth_withdrawal": wd_roth,
            "trad_end": trad,
            "roth_end": roth,
            "taxable_end": taxable,
            "net_worth_end": trad + roth + taxable,
        })

    if not rows:
        return rows, 0.0, 0.0, 0.0

    last = rows[-1]
    final_i = len(rows) - 1
    final_brackets = [(inflate(start, cfg.bracket_inflation, final_i), rate) for start, rate in FEDERAL_BRACKETS_2026[last["filing_status"]]]
    terminal_rate = marginal_rate(last["taxable_income"], final_brackets)
    legacy = last["taxable_end"] + last["roth_end"] + last["trad_end"] * (1 - terminal_rate)

    initial = h.trad_balance + h.roth_balance + h.taxable_balance
    score = cfg.weight_legacy * (legacy / max(1.0, initial)) - cfg.weight_tax * (lifetime_taxes / max(1.0, initial))
    return rows, lifetime_taxes, legacy, score


def project_plan(household: HouseholdConfig, cfg: ProjectionConfig, conversion_schedule: Dict[int, float]):
    rows, taxes, legacy, score = _simulate(household, cfg, conversion_schedule)
    return {
        "projection": rows,
        "lifetime_taxes": taxes,
        "after_tax_legacy": legacy,
        "objective_score": score,
        "conversion_schedule": conversion_schedule,
    }


def optimize_plan(household: HouseholdConfig, cfg: ProjectionConfig, iterations: int = 5):
    years = [household.start_year + i for i in range(cfg.horizon_years)]
    grid = []
    val = 0.0
    while val <= cfg.annual_conversion_cap + 1e-9:
        grid.append(round(val, 2))
        val += cfg.conversion_step

    schedule = {y: 0.0 for y in years}
    for y in years:
        i = y - household.start_year
        oldest = max(household.current_age_1 + i, household.current_age_2 + i)
        if cfg.conversion_min_age <= oldest <= cfg.conversion_max_age:
            schedule[y] = min(cfg.annual_conversion_cap, 0.35 * cfg.annual_conversion_cap)

    best = project_plan(household, cfg, schedule)

    for _ in range(iterations):
        improved = False
        for year in years:
            best_local = best["objective_score"]
            best_value = schedule[year]
            for amt in grid:
                trial = dict(schedule)
                trial[year] = amt
                result = project_plan(household, cfg, trial)
                if result["objective_score"] > best_local:
                    best_local = result["objective_score"]
                    best_value = amt
                    best = result
                    improved = True
            schedule[year] = best_value
        if not improved:
            break

    best["conversion_schedule"] = schedule
    return best
