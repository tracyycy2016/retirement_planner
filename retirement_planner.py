"""
Canadian Retirement Planner - Comprehensive Multi-Destination Tool
For Ontario residents 30+ planning early retirement
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import math

st.set_page_config(
    page_title="Canadian Retirement Planner",
    page_icon="🍁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# DESTINATION DATA  (real costs & tax rules as of 2024/2025)
# ─────────────────────────────────────────────────────────────────────────────

DESTINATIONS = {
    "Toronto, Canada": {
        "flag": "🇨🇦",
        "currency": "CAD",
        "fx_to_cad": 1.0,
        "monthly_costs": {
            "Housing (rent/mortgage equivalent)": 2800,
            "Groceries": 700,
            "Dining Out": 500,
            "Transportation": 200,
            "Utilities (hydro, gas, internet)": 350,
            "Healthcare (supplemental)": 250,
            "Entertainment & leisure": 400,
            "Clothing & personal care": 200,
            "Travel & vacations": 400,
            "Miscellaneous": 300,
        },
        "healthcare_note": "Provincial OHIP covers basics; supplemental ~$250/mo",
        "tax_info": {
            "type": "domestic",
            "provincial": "Ontario",
            "note": "Full Canadian tax system applies. OAS/CPP fully taxable. No withholding.",
        },
        "inflation": 0.025,
        "investment_return": 0.065,
        "property_ownership": True,
        "visa_difficulty": "None (citizen/PR)",
        "quality_of_life": 8,
        "healthcare_quality": 9,
        "safety": 8,
    },
    "Calgary, Canada": {
        "flag": "🇨🇦",
        "currency": "CAD",
        "fx_to_cad": 1.0,
        "monthly_costs": {
            "Housing (rent/mortgage equivalent)": 2000,
            "Groceries": 650,
            "Dining Out": 420,
            "Transportation": 180,
            "Utilities (hydro, gas, internet)": 280,
            "Healthcare (supplemental)": 200,
            "Entertainment & leisure": 350,
            "Clothing & personal care": 180,
            "Travel & vacations": 400,
            "Miscellaneous": 250,
        },
        "healthcare_note": "Alberta AHCIP; no provincial income tax",
        "tax_info": {
            "type": "domestic",
            "provincial": "Alberta",
            "note": "No Alberta provincial income tax. Full Canadian federal tax applies. OAS/CPP fully taxable.",
        },
        "inflation": 0.025,
        "investment_return": 0.065,
        "property_ownership": True,
        "visa_difficulty": "None (citizen/PR)",
        "quality_of_life": 8,
        "healthcare_quality": 8,
        "safety": 8,
    },
    "Chiang Mai, Thailand": {
        "flag": "🇹🇭",
        "currency": "THB",
        "fx_to_cad": 0.038,  # 1 THB ≈ 0.038 CAD
        "monthly_costs": {
            "Housing (rent/condo)": 500,
            "Groceries": 200,
            "Dining Out": 250,
            "Transportation": 80,
            "Utilities (electric, internet)": 100,
            "Healthcare (private insurance)": 200,
            "Entertainment & leisure": 200,
            "Clothing & personal care": 100,
            "Travel & vacations": 300,
            "Miscellaneous": 150,
        },
        "healthcare_note": "Private international insurance required ~$150-250/mo. Excellent private hospitals.",
        "tax_info": {
            "type": "foreign",
            "canada_treaty": True,
            "treaty_country": "Thailand",
            "oas_withholding": 0.25,
            "cpp_withholding": 0.25,
            "rrsp_withholding": 0.25,
            "local_tax_on_foreign_income": False,
            "local_tax_rate": 0.0,
            "note": "Canada-Thailand tax treaty: 25% withholding on OAS/CPP/RRSP. Thailand taxes income remitted in same year earned (from 2024 rule); careful planning can minimize. No tax on foreign income remitted from prior years.",
            "deemed_resident_risk": False,
            "departure_tax": True,
        },
        "inflation": 0.02,
        "investment_return": 0.065,
        "property_ownership": False,
        "visa_difficulty": "Thailand LTR Visa (Long-Term Resident) - requires $80k USD income or assets",
        "quality_of_life": 8,
        "healthcare_quality": 7,
        "safety": 7,
    },
    "Penang, Malaysia": {
        "flag": "🇲🇾",
        "currency": "MYR",
        "fx_to_cad": 0.30,  # 1 MYR ≈ 0.30 CAD
        "monthly_costs": {
            "Housing (rent/condo)": 600,
            "Groceries": 250,
            "Dining Out": 200,
            "Transportation": 80,
            "Utilities (electric, internet)": 90,
            "Healthcare (private insurance)": 180,
            "Entertainment & leisure": 200,
            "Clothing & personal care": 100,
            "Travel & vacations": 300,
            "Miscellaneous": 150,
        },
        "healthcare_note": "MM2H visa holders use private hospitals. International insurance ~$150-200/mo.",
        "tax_info": {
            "type": "foreign",
            "canada_treaty": False,
            "treaty_country": None,
            "oas_withholding": 0.25,
            "cpp_withholding": 0.25,
            "rrsp_withholding": 0.25,
            "local_tax_on_foreign_income": False,
            "local_tax_rate": 0.0,
            "note": "No Canada-Malaysia tax treaty. Default 25% NR withholding on Canadian registered income. Malaysia does NOT tax foreign-sourced income remitted to Malaysia (territorial tax system). TFSA withdrawals tax-free.",
            "deemed_resident_risk": False,
            "departure_tax": True,
        },
        "inflation": 0.025,
        "investment_return": 0.065,
        "property_ownership": True,
        "visa_difficulty": "MM2H (Malaysia My Second Home): RM1.5M liquid assets or RM40k/mo income",
        "quality_of_life": 8,
        "healthcare_quality": 7,
        "safety": 7,
    },
    "Puerto Vallarta, Mexico": {
        "flag": "🇲🇽",
        "currency": "MXN",
        "fx_to_cad": 0.073,  # 1 MXN ≈ 0.073 CAD
        "monthly_costs": {
            "Housing (rent/condo)": 900,
            "Groceries": 350,
            "Dining Out": 300,
            "Transportation": 100,
            "Utilities (electric, internet)": 120,
            "Healthcare (private insurance)": 220,
            "Entertainment & leisure": 300,
            "Clothing & personal care": 120,
            "Travel & vacations": 350,
            "Miscellaneous": 200,
        },
        "healthcare_note": "IMSS voluntary enrollment ~$500/yr or private insurance. Excellent private hospitals in PV.",
        "tax_info": {
            "type": "foreign",
            "canada_treaty": True,
            "treaty_country": "Mexico",
            "oas_withholding": 0.15,
            "cpp_withholding": 0.15,
            "rrsp_withholding": 0.15,
            "local_tax_on_foreign_income": True,
            "local_tax_rate": 0.0,
            "note": "Canada-Mexico tax treaty: reduced 15% withholding on pensions. Mexico taxes residents on worldwide income but Canadian pensions/OAS/CPP qualify for treaty relief. Mexican income tax rates 1.92%-35%; foreign pension income may have treaty exemptions. TFSA withdrawals not subject to Mexican tax.",
            "deemed_resident_risk": False,
            "departure_tax": True,
        },
        "inflation": 0.038,
        "investment_return": 0.065,
        "property_ownership": True,
        "visa_difficulty": "Temporary Resident Visa → Permanent Resident (4 yrs). Income requirement ~$2,700 CAD/mo",
        "quality_of_life": 8,
        "healthcare_quality": 7,
        "safety": 6,
    },
    "Barcelona, Spain": {
        "flag": "🇪🇸",
        "currency": "EUR",
        "fx_to_cad": 1.47,  # 1 EUR ≈ 1.47 CAD
        "monthly_costs": {
            "Housing (rent/apartment)": 1500,
            "Groceries": 450,
            "Dining Out": 500,
            "Transportation": 80,
            "Utilities (electric, internet)": 130,
            "Healthcare (private insurance)": 250,
            "Entertainment & leisure": 400,
            "Clothing & personal care": 200,
            "Travel & vacations": 400,
            "Miscellaneous": 300,
        },
        "healthcare_note": "Spain requires private health insurance for non-EU residents. ~€200-300/mo.",
        "tax_info": {
            "type": "foreign",
            "canada_treaty": True,
            "treaty_country": "Spain",
            "oas_withholding": 0.15,
            "cpp_withholding": 0.15,
            "rrsp_withholding": 0.15,
            "local_tax_on_foreign_income": True,
            "local_tax_rate": 0.24,
            "note": "Canada-Spain tax treaty: 15% withholding on Canadian pensions. Spain taxes residents on worldwide income. Spanish income tax 19%-47%. Non-Lucrative Visa residents cannot work but may live on passive income. Beckham Law (special expat regime) may apply for first 6 years: flat 24% on Spanish-source income. Foreign pensions taxed in Spain at progressive rates but treaty credits offset double taxation.",
            "deemed_resident_risk": True,
            "beckham_law": True,
            "departure_tax": True,
        },
        "inflation": 0.025,
        "investment_return": 0.065,
        "property_ownership": True,
        "visa_difficulty": "Non-Lucrative Visa: €28,800/yr income. Renewal annually → Permanent after 5 yrs",
        "quality_of_life": 9,
        "healthcare_quality": 9,
        "safety": 8,
    },
    "Lisbon/Algarve, Portugal": {
        "flag": "🇵🇹",
        "currency": "EUR",
        "fx_to_cad": 1.47,
        "monthly_costs": {
            "Housing (rent/apartment)": 1200,
            "Groceries": 380,
            "Dining Out": 380,
            "Transportation": 60,
            "Utilities (electric, internet)": 120,
            "Healthcare (private insurance)": 200,
            "Entertainment & leisure": 300,
            "Clothing & personal care": 150,
            "Travel & vacations": 400,
            "Miscellaneous": 250,
        },
        "healthcare_note": "SNS (national health) accessible to legal residents. Private insurance adds ~€100-200/mo.",
        "tax_info": {
            "type": "foreign",
            "canada_treaty": True,
            "treaty_country": "Portugal",
            "oas_withholding": 0.10,
            "cpp_withholding": 0.10,
            "rrsp_withholding": 0.25,
            "local_tax_on_foreign_income": True,
            "local_tax_rate": 0.10,
            "note": "Canada-Portugal tax treaty: 10% withholding on OAS/CPP pensions. RRSP/RRIF withdrawals 25% NR withholding. Portugal NHR (Non-Habitual Resident) regime: 10% flat tax on foreign pension income for 10 years (NHR 2.0 as of 2024). After NHR period, standard Portuguese rates 14.5%-48% apply. Excellent tax efficiency during NHR period.",
            "nhr_regime": True,
            "nhr_rate": 0.10,
            "nhr_years": 10,
            "deemed_resident_risk": False,
            "departure_tax": True,
        },
        "inflation": 0.023,
        "investment_return": 0.065,
        "property_ownership": True,
        "visa_difficulty": "D7 Passive Income Visa: ~€1,020/mo income. Very accessible.",
        "quality_of_life": 9,
        "healthcare_quality": 8,
        "safety": 9,
    },
    "Athens/Crete, Greece": {
        "flag": "🇬🇷",
        "currency": "EUR",
        "fx_to_cad": 1.47,
        "monthly_costs": {
            "Housing (rent/apartment)": 900,
            "Groceries": 380,
            "Dining Out": 380,
            "Transportation": 60,
            "Utilities (electric, internet)": 130,
            "Healthcare (private insurance)": 180,
            "Entertainment & leisure": 300,
            "Clothing & personal care": 130,
            "Travel & vacations": 400,
            "Miscellaneous": 200,
        },
        "healthcare_note": "Public healthcare accessible to legal residents. Private insurance strongly recommended ~€150-200/mo.",
        "tax_info": {
            "type": "foreign",
            "canada_treaty": False,
            "treaty_country": None,
            "oas_withholding": 0.25,
            "cpp_withholding": 0.25,
            "rrsp_withholding": 0.25,
            "local_tax_on_foreign_income": True,
            "local_tax_rate": 0.07,
            "note": "No Canada-Greece tax treaty. Default 25% NR withholding on Canadian registered accounts. Greece offers a 7% flat tax regime for foreign retirees (Alternative Tax Regime for Pensioners) for 15 years: pay only 7% on all foreign-source income. This is extremely advantageous. Must transfer tax residency to Greece and apply within 3 years.",
            "pensioner_flat_tax": True,
            "pensioner_flat_rate": 0.07,
            "pensioner_flat_years": 15,
            "deemed_resident_risk": False,
            "departure_tax": True,
        },
        "inflation": 0.025,
        "investment_return": 0.065,
        "property_ownership": True,
        "visa_difficulty": "Digital Nomad Visa / Retirement Visa: €3,500/mo income. Golden Visa: €250k property.",
        "quality_of_life": 8,
        "healthcare_quality": 7,
        "safety": 8,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# CANADIAN TAX FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def canadian_federal_tax(income: float, year: int = 2024) -> float:
    """Calculate federal income tax (2024 brackets, indexed ~2% annually)"""
    idx = (1 + 0.02) ** (year - 2024)
    brackets = [
        (57375 * idx, 0.15),
        (114750 * idx, 0.205),
        (177882 * idx, 0.26),
        (253414 * idx, 0.29),
        (float('inf'), 0.33),
    ]
    tax = 0.0
    prev = 0.0
    for limit, rate in brackets:
        if income <= prev:
            break
        taxable = min(income, limit) - prev
        tax += taxable * rate
        prev = limit
    return max(0, tax)

def ontario_provincial_tax(income: float, year: int = 2024) -> float:
    """Ontario provincial income tax"""
    idx = (1 + 0.02) ** (year - 2024)
    brackets = [
        (51446 * idx, 0.0505),
        (102894 * idx, 0.0915),
        (150000 * idx, 0.1116),
        (220000 * idx, 0.1216),
        (float('inf'), 0.1316),
    ]
    tax = 0.0
    prev = 0.0
    for limit, rate in brackets:
        if income <= prev:
            break
        taxable = min(income, limit) - prev
        tax += taxable * rate
        prev = limit
    # Ontario surtax
    if tax > 5315 * idx:
        tax += (tax - 5315 * idx) * 0.20
    if tax > 6802 * idx:
        tax += (tax - 6802 * idx) * 0.36
    return max(0, tax)

def alberta_provincial_tax(income: float, year: int = 2024) -> float:
    """Alberta provincial income tax"""
    idx = (1 + 0.02) ** (year - 2024)
    brackets = [
        (148269 * idx, 0.10),
        (177922 * idx, 0.12),
        (237230 * idx, 0.13),
        (355845 * idx, 0.14),
        (float('inf'), 0.15),
    ]
    tax = 0.0
    prev = 0.0
    for limit, rate in brackets:
        if income <= prev:
            break
        taxable = min(income, limit) - prev
        tax += taxable * rate
        prev = limit
    return max(0, tax)

def canadian_total_tax(income: float, province: str = "Ontario", year: int = 2024) -> float:
    """Total Canadian tax (federal + provincial)"""
    federal = canadian_federal_tax(income, year)
    if province == "Alberta":
        provincial = alberta_provincial_tax(income, year)
    else:
        provincial = ontario_provincial_tax(income, year)
    
    # Basic personal amount credit
    bpa = 15705 * (1.02 ** (year - 2024))
    federal_credit = bpa * 0.15
    if province == "Ontario":
        prov_credit = bpa * 0.0505
    else:
        prov_credit = bpa * 0.10
    
    total = max(0, federal - federal_credit) + max(0, provincial - prov_credit)
    return total

def oas_clawback(total_income: float, year: int = 2024) -> float:
    """OAS recovery tax (clawback) - 15% on income above threshold"""
    idx = (1.02) ** (year - 2024)
    threshold = 90997 * idx
    if total_income <= threshold:
        return 0.0
    return min((total_income - threshold) * 0.15, 8732 * idx)

# ─────────────────────────────────────────────────────────────────────────────
# GOVERNMENT BENEFITS
# ─────────────────────────────────────────────────────────────────────────────

def get_oas_annual(start_age: int, current_age: int, years_in_canada: int = 40) -> float:
    """
    OAS benefit calculation (2024 rates, indexed to CPI).
    Max at 65: $8,732/yr. Deferral: +0.6%/month up to 70.
    Partial: years_in_canada/40 * max.
    """
    max_oas_2024 = 8732.0  # annual
    proration = min(years_in_canada / 40, 1.0)
    base = max_oas_2024 * proration
    
    if start_age < 65:
        return 0.0  # Cannot start before 65
    if start_age > 70:
        start_age = 70
    
    deferral_months = (start_age - 65) * 12
    enhancement = 1 + (deferral_months * 0.006)
    return base * enhancement

def get_cpp_annual(
    start_age: int,
    avg_income: float,
    contributory_years: int = 35,
    current_age: int = 35
) -> float:
    """
    CPP benefit. Max at 65 (2024): $16,375/yr.
    Early (60-64): -0.6%/month. Defer (66-70): +0.7%/month.
    Estimate based on earnings history.
    """
    max_cpp_2024 = 16375.0
    ympe_2024 = 68500.0
    
    # Earnings ratio
    avg_ympe_ratio = min(avg_income / ympe_2024, 1.0)
    years_ratio = min(contributory_years / 39, 1.0)
    
    base_at_65 = max_cpp_2024 * avg_ympe_ratio * years_ratio
    
    if start_age < 60:
        return 0.0
    elif start_age < 65:
        reduction_months = (65 - start_age) * 12
        factor = 1 - (reduction_months * 0.006)
        return base_at_65 * factor
    elif start_age > 65:
        deferral_months = min((start_age - 65) * 12, 60)
        enhancement = 1 + (deferral_months * 0.007)
        return base_at_65 * enhancement
    else:
        return base_at_65

def get_gis_annual(oas: float, other_income: float) -> float:
    """Guaranteed Income Supplement (for low-income OAS recipients)"""
    # Max GIS 2024 single: ~$13,522/yr, reduced by $0.50 per $1 other income
    max_gis = 13522.0
    if other_income > 21624:
        return 0.0
    gis = max(0, max_gis - (other_income * 0.5))
    return gis

# ─────────────────────────────────────────────────────────────────────────────
# ACCOUNT WITHDRAWAL STRATEGY
# ─────────────────────────────────────────────────────────────────────────────

def rrsp_rrif_min_withdrawal_rate(age: int) -> float:
    """RRIF minimum withdrawal rates by age"""
    rates = {
        71: 0.0528, 72: 0.0540, 73: 0.0553, 74: 0.0567, 75: 0.0582,
        76: 0.0598, 77: 0.0617, 78: 0.0636, 79: 0.0658, 80: 0.0682,
        81: 0.0708, 82: 0.0738, 83: 0.0771, 84: 0.0808, 85: 0.0851,
        86: 0.0899, 87: 0.0955, 88: 0.1021, 89: 0.1099, 90: 0.1192,
        91: 0.1306, 92: 0.1449, 93: 0.1634, 94: 0.1879,
    }
    if age < 71:
        return 0.0
    if age >= 95:
        return 0.20
    return rates.get(age, 0.20)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN PROJECTION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def run_projection(params: dict, dest_name: str, dest_data: dict) -> pd.DataFrame:
    """
    Run year-by-year retirement projection.
    Returns DataFrame with annual financial details.
    Supports per-account investment returns, per-destination inflation override,
    and a company group pension plan (DB or DC).
    """
    current_age = params["current_age"]
    retire_age  = params["retire_age"]
    lifespan    = params["lifespan"]
    current_year = 2024

    # ── Accounts ──────────────────────────────────────────────────────────
    rrsp   = params["rrsp_balance"]
    tfsa   = params["tfsa_balance"]
    nonreg = params["nonreg_balance"]
    # DC pension account balance (grows like RRSP but separate)
    dc_pension = params.get("dc_pension_balance", 0.0)

    # ── Income during accumulation ─────────────────────────────────────────
    salary                   = params["current_salary"]
    annual_rrsp_contribution = params["annual_rrsp_contribution"]
    annual_tfsa_contribution = params["annual_tfsa_contribution"]
    annual_nonreg_contribution = params["annual_nonreg_contribution"]
    salary_growth            = params["salary_growth"]
    # DC: employer + employee contribution per year
    annual_dc_contribution   = params.get("annual_dc_contribution", 0.0)

    # ── Per-account investment returns ────────────────────────────────────
    # Fall back to dest default if not overridden
    dest_default_return = dest_data["investment_return"]
    inv_rrsp   = params.get("inv_return_rrsp",   dest_default_return)
    inv_tfsa   = params.get("inv_return_tfsa",   dest_default_return)
    inv_nonreg = params.get("inv_return_nonreg", dest_default_return)
    inv_dc     = params.get("inv_return_dc",     dest_default_return)

    # ── Inflation (destination-specific override wins) ────────────────────
    inflation = dest_data["inflation"]
    dest_inf_override = params.get(f"inflation_override_{dest_name}", None)
    if dest_inf_override is not None:
        inflation = dest_inf_override
    elif params.get("inflation_override") is not None:
        inflation = params["inflation_override"]

    # ── Monthly expenses ──────────────────────────────────────────────────
    monthly_expenses_cad  = params["monthly_expenses_cad"]
    annual_expenses_today = monthly_expenses_cad * 12

    # ── Government benefits ───────────────────────────────────────────────
    oas_start             = params["oas_start_age"]
    cpp_start             = params["cpp_start_age"]
    years_canada          = params["years_in_canada"]
    avg_cpp_income        = params["cpp_avg_income"]
    cpp_contributory_years = params["cpp_contributory_years"]

    # ── Group Pension Plan ────────────────────────────────────────────────
    pension_type         = params.get("pension_type", "none")       # "none" | "db" | "dc"
    # DB: fixed annual benefit starting at retire_age (in today's CAD, indexed to CPI)
    db_annual_benefit    = params.get("db_annual_benefit", 0.0)
    db_indexed           = params.get("db_indexed", True)           # CPI-indexed
    db_survivor_pct      = params.get("db_survivor_pct", 0.60)      # survivor benefit %
    # DC: treated as additional registered account (like RRSP for tax, separate balance)

    # ── Tax info ──────────────────────────────────────────────────────────
    tax_info         = dest_data["tax_info"]
    is_domestic      = tax_info["type"] == "domestic"
    province         = tax_info.get("provincial", "Ontario")
    oas_wh           = tax_info.get("oas_withholding",  0.25)
    cpp_wh           = tax_info.get("cpp_withholding",  0.25)
    rrsp_wh          = tax_info.get("rrsp_withholding", 0.25)
    nhr              = tax_info.get("nhr_regime",        False)
    nhr_rate         = tax_info.get("nhr_rate",          0.10)
    nhr_years        = tax_info.get("nhr_years",         10)
    pensioner_flat   = tax_info.get("pensioner_flat_tax", False)
    pensioner_flat_rate  = tax_info.get("pensioner_flat_rate",  0.07)
    pensioner_flat_years = tax_info.get("pensioner_flat_years", 15)
    local_tax_on_foreign = tax_info.get("local_tax_on_foreign_income", False)
    local_tax_rate       = tax_info.get("local_tax_rate", 0.0)

    records = []

    for age in range(current_age, lifespan + 1):
        year          = current_year + (age - current_age)
        years_retired = max(0, age - retire_age)
        is_retired    = age >= retire_age
        inflation_factor = (1 + inflation) ** years_retired if is_retired else 1.0

        # ── Accumulation Phase ────────────────────────────────────────────
        if not is_retired:
            sal_now = salary * (1 + salary_growth) ** (age - current_age)
            rrsp    = rrsp    * (1 + inv_rrsp)   + annual_rrsp_contribution
            tfsa    = tfsa    * (1 + inv_tfsa)   + annual_tfsa_contribution
            nonreg  = nonreg  * (1 + inv_nonreg) + annual_nonreg_contribution
            if pension_type == "dc":
                dc_pension = dc_pension * (1 + inv_dc) + annual_dc_contribution
            tax_paid   = canadian_total_tax(sal_now, province, year)
            net_salary = (sal_now - tax_paid
                          - annual_rrsp_contribution
                          - annual_tfsa_contribution
                          - annual_nonreg_contribution
                          - (annual_dc_contribution if pension_type == "dc" else 0))

            total_port = rrsp + tfsa + nonreg + (dc_pension if pension_type == "dc" else 0)
            records.append({
                "Age": age, "Year": year, "Phase": "Accumulation",
                "RRSP Balance": rrsp, "TFSA Balance": tfsa,
                "Non-Reg Balance": nonreg, "DC Pension Balance": dc_pension,
                "Total Portfolio": total_port,
                "Gross Income": sal_now,
                "CPP Benefit": 0, "OAS Benefit": 0, "DB Pension": 0,
                "RRSP Withdrawal": 0, "TFSA Withdrawal": 0,
                "NonReg Withdrawal": 0, "DC Withdrawal": 0,
                "Annual Expenses (CAD)": 0,
                "Tax Paid (Canada)": tax_paid, "Tax Paid (Local)": 0,
                "Withholding Tax": 0, "Net Surplus/Deficit": net_salary,
                "OAS Clawback": 0,
            })
            continue

        # ── Retirement Phase ──────────────────────────────────────────────
        annual_expenses = annual_expenses_today * inflation_factor

        # Government benefits (gross, CPI-indexed at 2%/yr)
        cpi_idx   = (1 + 0.02) ** (year - 2024)
        cpp_gross = (get_cpp_annual(cpp_start, avg_cpp_income, cpp_contributory_years)
                     * cpi_idx) if age >= cpp_start else 0.0
        oas_gross = (get_oas_annual(oas_start, age, years_canada)
                     * cpi_idx) if age >= oas_start else 0.0

        # DB Pension income
        db_income = 0.0
        if pension_type == "db" and age >= retire_age:
            db_income = db_annual_benefit * (cpi_idx if db_indexed else 1.0)

        expenses_cad = annual_expenses

        # Withholding on government benefits (NR)
        if is_domestic:
            cpp_net  = cpp_gross
            oas_net  = oas_gross
            wh_paid  = 0.0
        else:
            cpp_net  = cpp_gross * (1 - cpp_wh)
            oas_net  = oas_gross * (1 - oas_wh)
            wh_paid  = (cpp_gross * cpp_wh) + (oas_gross * oas_wh)
            # DB pension treated same as CPP for withholding purposes (registered pension)
            db_net   = db_income * (1 - rrsp_wh)
            wh_paid += db_income * rrsp_wh
        if is_domestic:
            db_net = db_income

        guaranteed_income = cpp_net + oas_net + db_net
        income_gap        = max(0, expenses_cad - guaranteed_income)

        # ── Withdrawal Strategy ────────────────────────────────────────────
        # Order: TFSA (tax-free) → DC Pension → RRSP/RRIF → Non-Reg
        rrsp_withdrawal   = 0.0
        tfsa_withdrawal   = 0.0
        nonreg_withdrawal = 0.0
        dc_withdrawal     = 0.0
        rrsp_tax_wh       = 0.0
        dc_tax_wh         = 0.0

        # RRIF minimum
        rrif_min = rrsp * rrsp_rrif_min_withdrawal_rate(age)
        # DC pension min (treated same as RRIF once converted)
        dc_rrif_min = dc_pension * rrsp_rrif_min_withdrawal_rate(age)

        remaining_gap = income_gap

        # 1. TFSA
        tfsa_draw       = min(tfsa, remaining_gap * params.get("tfsa_priority", 0.5))
        tfsa_withdrawal = max(tfsa_draw, 0)
        remaining_gap  -= tfsa_withdrawal

        # 2. DC Pension (if DC type)
        if pension_type == "dc":
            dc_draw = max(dc_rrif_min, min(dc_pension,
                          remaining_gap / (1 - rrsp_wh if not is_domestic else 0.3)))
            dc_draw      = min(dc_pension, dc_draw)
            dc_withdrawal = dc_draw
            if not is_domestic:
                dc_tax_wh   = dc_draw * rrsp_wh
                wh_paid    += dc_tax_wh
            remaining_gap -= (dc_draw - dc_tax_wh)

        # 3. RRSP/RRIF
        rrsp_draw = max(rrif_min, min(rrsp,
                        remaining_gap / (1 - rrsp_wh if not is_domestic else 0.3)))
        rrsp_draw       = min(rrsp, rrsp_draw)
        rrsp_withdrawal = rrsp_draw
        if not is_domestic:
            rrsp_tax_wh  = rrsp_draw * rrsp_wh
            wh_paid     += rrsp_tax_wh
        remaining_gap -= (rrsp_draw - rrsp_tax_wh)

        # 4. Non-Reg
        nonreg_draw       = max(0, min(nonreg, remaining_gap))
        nonreg_withdrawal = nonreg_draw
        remaining_gap    -= nonreg_draw

        # Grow accounts
        rrsp      = max(0, rrsp      - rrsp_withdrawal)   * (1 + inv_rrsp)
        tfsa      = max(0, tfsa      - tfsa_withdrawal)   * (1 + inv_tfsa)
        nonreg    = max(0, nonreg    - nonreg_withdrawal) * (1 + inv_nonreg)
        dc_pension = max(0, dc_pension - dc_withdrawal)   * (1 + inv_dc)

        total_withdrawal  = rrsp_withdrawal + tfsa_withdrawal + nonreg_withdrawal + dc_withdrawal
        total_gross_income = cpp_gross + oas_gross + db_income + total_withdrawal

        # ── Tax Calculation ────────────────────────────────────────────────
        if is_domestic:
            taxable_income   = (cpp_gross + oas_gross + db_income
                                + rrsp_withdrawal + dc_withdrawal
                                + (nonreg_withdrawal * 0.5))
            oas_clawback_amt = oas_clawback(taxable_income, year)
            canada_tax       = canadian_total_tax(taxable_income, province, year)
            local_tax        = 0.0
            wh_paid          = oas_clawback_amt
            total_tax        = canada_tax
        else:
            oas_clawback_amt = 0.0
            foreign_registered_net = (cpp_net + oas_net + db_net
                                      + rrsp_withdrawal * (1 - rrsp_wh)
                                      + dc_withdrawal   * (1 - rrsp_wh))
            if nhr and years_retired <= nhr_years:
                local_tax = foreign_registered_net * nhr_rate
            elif pensioner_flat and years_retired <= pensioner_flat_years:
                local_tax = foreign_registered_net * pensioner_flat_rate
            elif local_tax_on_foreign:
                local_tax = foreign_registered_net * local_tax_rate
            else:
                local_tax = 0.0
            canada_tax = 0.0
            total_tax  = wh_paid + local_tax

        net_income  = total_gross_income - total_tax
        net_surplus = net_income - expenses_cad

        total_port  = rrsp + tfsa + nonreg + (dc_pension if pension_type == "dc" else 0)

        records.append({
            "Age": age, "Year": year, "Phase": "Retirement",
            "RRSP Balance": rrsp, "TFSA Balance": tfsa,
            "Non-Reg Balance": nonreg, "DC Pension Balance": dc_pension,
            "Total Portfolio": total_port,
            "Gross Income": total_gross_income,
            "CPP Benefit": cpp_gross, "OAS Benefit": oas_gross, "DB Pension": db_income,
            "RRSP Withdrawal": rrsp_withdrawal,
            "TFSA Withdrawal": tfsa_withdrawal,
            "NonReg Withdrawal": nonreg_withdrawal,
            "DC Withdrawal": dc_withdrawal,
            "Annual Expenses (CAD)": expenses_cad,
            "Tax Paid (Canada)": canada_tax + wh_paid,
            "Tax Paid (Local)": local_tax,
            "Withholding Tax": wh_paid,
            "Net Surplus/Deficit": net_surplus,
            "OAS Clawback": oas_clawback_amt if is_domestic else 0.0,
        })

    return pd.DataFrame(records)

# ─────────────────────────────────────────────────────────────────────────────
# RETIREMENT AGE FINDER
# ─────────────────────────────────────────────────────────────────────────────

def find_earliest_retirement(params: dict, dest_name: str, dest_data: dict) -> Optional[int]:
    """Find earliest retirement age where portfolio doesn't run out by lifespan."""
    for try_age in range(params["current_age"] + 5, 71):
        p = params.copy()
        p["retire_age"] = try_age
        df = run_projection(p, dest_name, dest_data)
        if df["Total Portfolio"].min() > 0:
            return try_age
    return None

# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def fmt_cad(val: float) -> str:
    if abs(val) >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    if abs(val) >= 1_000:
        return f"${val/1_000:.0f}K"
    return f"${val:.0f}"

def sustainability_score(df: pd.DataFrame) -> str:
    retired = df[df["Phase"] == "Retirement"]
    if retired.empty:
        return "N/A"
    min_port = retired["Total Portfolio"].min()
    last_port = retired.iloc[-1]["Total Portfolio"]
    if last_port > 500_000:
        return "🟢 Excellent"
    elif last_port > 100_000:
        return "🟡 Good"
    elif last_port > 0:
        return "🟠 Marginal"
    elif min_port > 0:
        return "🟡 Depleted Late"
    else:
        deficit_age = retired[retired["Total Portfolio"] <= 0]["Age"].iloc[0]
        return f"🔴 Depleted at {deficit_age}"

# ─────────────────────────────────────────────────────────────────────────────
# STREAMLIT APP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
         padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;'>
        <h1 style='color: #e94560; margin:0; font-size:2.2rem;'>🍁 Canadian Retirement Planner</h1>
        <p style='color: #a8b2d8; margin-top:0.5rem; font-size:1.05rem;'>
            Multi-destination early retirement analysis · RRSP · TFSA · Non-Reg · Tax-optimized
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Top-level page tabs ───────────────────────────────────────────────────
    page_tabs = st.tabs([
        "⚙️ My Profile & Settings",
        "🏠 Living Expenses",
        "📋 Summary",
        "📈 Portfolio Growth",
        "💸 Income & Withdrawals",
        "🧾 Tax Analysis",
        "📊 Data Tables",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 0 — PROFILE & SETTINGS
    # ════════════════════════════════════════════════════════════════════════
    with page_tabs[0]:
        st.markdown("## 👤 Personal Profile & Financial Settings")
        st.caption("Set your personal details, account balances, and retirement preferences here.")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("### 🧑 Profile")
            current_age = st.number_input("Current Age", 25, 60, 35, 1, key="current_age")
            lifespan    = st.number_input("Planning Horizon (age)", 80, 100, 90, 1, key="lifespan")
            years_in_canada = st.number_input("Years in Canada (for OAS proration)", 0, 40, 35, 1, key="yic")

            st.markdown("### 🎯 Retirement Target")
            retire_age     = st.number_input("Target Retirement Age", current_age + 1, 70, 55, 1, key="retire_age")
            tfsa_priority  = st.slider("TFSA draw priority (fraction of income gap)", 0.1, 1.0, 0.5, 0.05, key="tfsa_pri")

        with col_b:
            st.markdown("### 💰 Income & Salary")
            current_salary = st.number_input("Current Annual Salary (CAD)", 40000, 500000, 120000, 5000, key="salary")
            salary_growth  = st.slider("Annual Salary Growth", 0.0, 0.10, 0.02, 0.005, format="%.1f%%", key="sal_growth")

            st.markdown("### 📊 CPP Estimate")
            cpp_avg_income       = st.number_input("Avg Career Income for CPP (CAD)", 40000, 200000, 95000, 5000, key="cpp_inc")
            cpp_contributory_years = st.number_input("CPP Contributory Years (career total)", 5, 39, 30, 1, key="cpp_yrs")
            cpp_start = st.selectbox("CPP Start Age", [60,61,62,63,64,65,66,67,68,69,70], index=5, key="cpp_start")
            oas_start = st.selectbox("OAS Start Age", [65,66,67,68,69,70], index=0, key="oas_start")

        with col_c:
            st.markdown("### 🏦 Account Balances (CAD today)")
            rrsp_balance   = st.number_input("RRSP Balance",              0, 2000000, 80000,  5000, key="rrsp_bal")
            tfsa_balance   = st.number_input("TFSA Balance",              0,  500000, 40000,  5000, key="tfsa_bal")
            nonreg_balance = st.number_input("Non-Registered Balance",    0, 2000000, 20000,  5000, key="nr_bal")

            st.markdown("### 💳 Annual Contributions (CAD)")
            annual_rrsp   = st.number_input("Annual RRSP Contribution",   0,  31560, 18000,   500, key="rrsp_con")
            annual_tfsa   = st.number_input("Annual TFSA Contribution",   0,   7000,  7000,   500, key="tfsa_con")
            annual_nonreg = st.number_input("Annual Non-Reg Contribution",0, 200000, 10000,  1000, key="nr_con")

        st.divider()
        st.markdown("### 🔧 Rate Overrides  *(optional — leave unchecked to use destination defaults)*")
        oc1, oc2 = st.columns(2)
        with oc1:
            use_inv_override = st.checkbox("Override Investment Return", key="use_inv")
            inv_override = st.slider("Investment Return", 0.01, 0.12, 0.065, 0.005,
                                     format="%.1f%%", key="inv_ov") if use_inv_override else None
        with oc2:
            use_inf_override = st.checkbox("Override Inflation Rate", key="use_inf")
            inf_override = st.slider("Inflation Rate", 0.005, 0.08, 0.025, 0.005,
                                     format="%.1f%%", key="inf_ov") if use_inf_override else None

        st.divider()
        st.markdown("### 🗺️ Retirement Destinations to Compare")
        selected_dests = st.multiselect(
            "Select up to 8 destinations",
            list(DESTINATIONS.keys()),
            default=["Toronto, Canada", "Lisbon/Algarve, Portugal", "Athens/Crete, Greece"],
            key="sel_dests"
        )
        if not selected_dests:
            st.warning("Please select at least one destination.")

        # Estimated CPP / OAS preview
        if current_age and retire_age:
            st.divider()
            st.markdown("### 📐 Estimated Government Benefits Preview")
            bc1, bc2, bc3 = st.columns(3)
            est_cpp = get_cpp_annual(cpp_start, cpp_avg_income, cpp_contributory_years)
            est_oas = get_oas_annual(oas_start, oas_start, years_in_canada)
            with bc1:
                st.metric("Estimated CPP (at 65 base)", f"${est_cpp:,.0f}/yr",
                          help="Adjusted for start age selected above")
            with bc2:
                st.metric("Estimated OAS (at 65 base)", f"${est_oas:,.0f}/yr",
                          help="Pro-rated by years in Canada")
            with bc3:
                st.metric("Combined Annual", f"${est_cpp + est_oas:,.0f}/yr",
                          f"${(est_cpp + est_oas)/12:,.0f}/mo")

    # Retrieve all widget values (stored in session_state by key)
    # Provide safe defaults so other tabs work even before tab 0 is visited
    current_age    = st.session_state.get("current_age",    35)
    lifespan       = st.session_state.get("lifespan",       90)
    years_in_canada= st.session_state.get("yic",            35)
    retire_age     = st.session_state.get("retire_age",     55)
    tfsa_priority  = st.session_state.get("tfsa_pri",      0.5)
    current_salary = st.session_state.get("salary",     120000)
    salary_growth  = st.session_state.get("sal_growth",  0.02)
    cpp_avg_income = st.session_state.get("cpp_inc",     95000)
    cpp_contributory_years = st.session_state.get("cpp_yrs", 30)
    cpp_start      = st.session_state.get("cpp_start",      65)
    oas_start      = st.session_state.get("oas_start",      65)
    rrsp_balance   = st.session_state.get("rrsp_bal",    80000)
    tfsa_balance   = st.session_state.get("tfsa_bal",    40000)
    nonreg_balance = st.session_state.get("nr_bal",      20000)
    annual_rrsp    = st.session_state.get("rrsp_con",    18000)
    annual_tfsa    = st.session_state.get("tfsa_con",     7000)
    annual_nonreg  = st.session_state.get("nr_con",      10000)
    inv_rrsp       = st.session_state.get("inv_rrsp",   0.065)
    inv_tfsa       = st.session_state.get("inv_tfsa",   0.07)
    inv_nonreg     = st.session_state.get("inv_nonreg", 0.055)
    inv_dc         = st.session_state.get("inv_dc",     0.065)
    _pension_radio     = st.session_state.get("pension_type_radio", "None")
    pension_type_key   = {"None": "none", "Defined Benefit (DB)": "db",
                          "Defined Contribution (DC)": "dc"}.get(_pension_radio, "none")
    db_annual_benefit  = st.session_state.get("db_benefit",  0.0)
    db_indexed         = st.session_state.get("db_indexed",  True)
    dc_pension_balance = st.session_state.get("dc_bal",      0.0)
    annual_dc_contribution = st.session_state.get("dc_con",  0.0)
    dest_inflation_overrides = st.session_state.get("dest_inflation_overrides", {})
    selected_dests = st.session_state.get("sel_dests",
                        ["Toronto, Canada", "Lisbon/Algarve, Portugal", "Athens/Crete, Greece"])

    if not selected_dests:
        for t in page_tabs[1:]:
            pass  # tabs exist but content below will be skipped
        st.stop()

    base_params = {
        "current_age": current_age,
        "lifespan": lifespan,
        "years_in_canada": years_in_canada,
        "current_salary": current_salary,
        "salary_growth": salary_growth,
        "rrsp_balance": rrsp_balance,
        "tfsa_balance": tfsa_balance,
        "nonreg_balance": nonreg_balance,
        "annual_rrsp_contribution": annual_rrsp,
        "annual_tfsa_contribution": annual_tfsa,
        "annual_nonreg_contribution": annual_nonreg,
        "cpp_avg_income": cpp_avg_income,
        "cpp_contributory_years": cpp_contributory_years,
        "cpp_start_age": cpp_start,
        "oas_start_age": oas_start,
        "retire_age": retire_age,
        "tfsa_priority": tfsa_priority,
        "inv_return_rrsp":   inv_rrsp,
        "inv_return_tfsa":   inv_tfsa,
        "inv_return_nonreg": inv_nonreg,
        "inv_return_dc":     inv_dc,
        "pension_type":           pension_type_key,
        "db_annual_benefit":      db_annual_benefit,
        "db_indexed":             db_indexed,
        "dc_pension_balance":     dc_pension_balance,
        "annual_dc_contribution": annual_dc_contribution,
    }
    for d, inf_val in dest_inflation_overrides.items():
        base_params[f"inflation_override_{d}"] = inf_val

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — LIVING EXPENSES
    # ════════════════════════════════════════════════════════════════════════
    with page_tabs[1]:
        st.markdown("## 🏠 Monthly Expense Customization by Destination")
        st.caption("All values in CAD. Defaults are based on real 2024 cost-of-living data. Adjust to match your lifestyle.")

        dest_expenses_local = {}
        n_cols = min(len(selected_dests), 3)
        exp_cols = st.columns(n_cols)

        for i, dest_name in enumerate(selected_dests):
            col = exp_cols[i % n_cols]
            dest = DESTINATIONS[dest_name]
            with col:
                st.markdown(f"### {dest['flag']} {dest_name.split(',')[0]}")
                monthly_total = 0
                for category, default_val in dest["monthly_costs"].items():
                    val = st.number_input(
                        f"{category}",
                        min_value=0, max_value=20000,
                        value=default_val, step=50,
                        key=f"exp_{dest_name}_{category}",
                    )
                    monthly_total += val
                years_to_retire = max(0, retire_age - current_age)
                inf_at_retire = (1 + dest["inflation"]) ** years_to_retire
                st.metric("Monthly Total (today)", f"${monthly_total:,.0f}",
                          f"~${monthly_total * inf_at_retire:,.0f} at retirement (inflation)")
                st.caption(f"🏥 {dest['healthcare_note']}")
                dest_expenses_local[dest_name] = monthly_total

        # Store for use in other tabs via session state
        st.session_state["dest_expenses"] = dest_expenses_local

        st.divider()
        st.markdown("### 📊 Cost of Living Comparison")
        colors = px.colors.qualitative.Bold
        cost_rows = [(d, dest_expenses_local[d]) for d in selected_dests]
        cost_rows.sort(key=lambda x: x[1])
        fig_bar = go.Figure(go.Bar(
            x=[f"{DESTINATIONS[d]['flag']} {d.split(',')[0]}" for d, _ in cost_rows],
            y=[v for _, v in cost_rows],
            marker_color=colors[:len(cost_rows)],
            text=[f"${v:,.0f}" for _, v in cost_rows],
            textposition="outside"
        ))
        fig_bar.update_layout(template="plotly_dark", height=400,
            yaxis_title="Monthly CAD", title="Monthly Cost of Living — Cheapest to Most Expensive")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Pie charts row
        st.markdown("### 🥧 Expense Breakdown by Category")
        pie_cols = st.columns(min(len(selected_dests), 3))
        for i, dest_name in enumerate(selected_dests):
            dest = DESTINATIONS[dest_name]
            expense_data = {
                cat: st.session_state.get(f"exp_{dest_name}_{cat}", default_val)
                for cat, default_val in dest["monthly_costs"].items()
            }
            with pie_cols[i % len(pie_cols)]:
                fig_pie = go.Figure(go.Pie(
                    labels=list(expense_data.keys()),
                    values=list(expense_data.values()),
                    hole=0.38,
                    textinfo="percent",
                ))
                fig_pie.update_layout(
                    template="plotly_dark", height=320,
                    title=f"{dest['flag']} {dest_name.split(',')[0]}",
                    showlegend=False,
                    margin=dict(t=40, b=10, l=10, r=10)
                )
                st.plotly_chart(fig_pie, use_container_width=True)

    # Resolve dest_expenses (may come from session state if tab 1 not re-rendered)
    dest_expenses = st.session_state.get("dest_expenses", {
        d: sum(DESTINATIONS[d]["monthly_costs"].values()) for d in selected_dests
    })
    # Fill any missing destinations
    for d in selected_dests:
        if d not in dest_expenses:
            dest_expenses[d] = sum(DESTINATIONS[d]["monthly_costs"].values())

    # ── Run projections ───────────────────────────────────────────────────────
    projections = {}
    for dest_name in selected_dests:
        params = base_params.copy()
        params["monthly_expenses_cad"] = dest_expenses[dest_name]
        projections[dest_name] = run_projection(params, dest_name, DESTINATIONS[dest_name])

    colors = px.colors.qualitative.Bold

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — SUMMARY CARDS
    # ════════════════════════════════════════════════════════════════════════
    with page_tabs[2]:
        st.markdown("## 📋 Retirement Plan Summary")

        n = len(selected_dests)
        summary_cols = st.columns(min(n, 3))
        for i, dest_name in enumerate(selected_dests):
            dest       = DESTINATIONS[dest_name]
            df         = projections[dest_name]
            retired_df = df[df["Phase"] == "Retirement"]

            score     = sustainability_score(df)
            retire_val = retired_df.iloc[0]["Total Portfolio"] if not retired_df.empty else 0
            last_val   = df.iloc[-1]["Total Portfolio"]
            avg_tax    = (retired_df["Tax Paid (Canada)"].mean() + retired_df["Tax Paid (Local)"].mean()
                          ) if not retired_df.empty else 0
            monthly_exp = dest_expenses[dest_name]
            earliest   = find_earliest_retirement(
                {**base_params, "monthly_expenses_cad": monthly_exp}, dest_name, dest)

            with summary_cols[i % 3]:
                st.markdown(f"""
                <div style='background:#1e2a3a;border:1px solid #2d4a6e;border-radius:10px;padding:1rem;margin-bottom:0.8rem;'>
                    <h3 style='color:#e94560;margin:0 0 0.2rem 0;'>{dest['flag']} {dest_name.split(',')[0]}</h3>
                    <div style='color:#a8b2d8;font-size:0.78rem;margin-bottom:0.7rem;'>{dest_name}</div>
                    <div style='display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;'>
                        <div style='background:#0d1b2a;padding:0.5rem;border-radius:6px;'>
                            <div style='color:#64ffda;font-size:0.65rem;'>SUSTAINABILITY</div>
                            <div style='color:white;font-size:0.85rem;font-weight:bold;'>{score}</div>
                        </div>
                        <div style='background:#0d1b2a;padding:0.5rem;border-radius:6px;'>
                            <div style='color:#64ffda;font-size:0.65rem;'>EARLIEST RETIRE AGE</div>
                            <div style='color:white;font-size:0.85rem;font-weight:bold;'>{earliest if earliest else "70+"}</div>
                        </div>
                        <div style='background:#0d1b2a;padding:0.5rem;border-radius:6px;'>
                            <div style='color:#64ffda;font-size:0.65rem;'>PORTFOLIO @ RETIRE</div>
                            <div style='color:white;font-size:0.85rem;'>{fmt_cad(retire_val)}</div>
                        </div>
                        <div style='background:#0d1b2a;padding:0.5rem;border-radius:6px;'>
                            <div style='color:#64ffda;font-size:0.65rem;'>PORTFOLIO @ {lifespan}</div>
                            <div style='color:white;font-size:0.85rem;'>{fmt_cad(last_val)}</div>
                        </div>
                        <div style='background:#0d1b2a;padding:0.5rem;border-radius:6px;'>
                            <div style='color:#64ffda;font-size:0.65rem;'>MONTHLY EXPENSES</div>
                            <div style='color:white;font-size:0.85rem;'>{fmt_cad(monthly_exp)}/mo</div>
                        </div>
                        <div style='background:#0d1b2a;padding:0.5rem;border-radius:6px;'>
                            <div style='color:#64ffda;font-size:0.65rem;'>AVG ANNUAL TAX</div>
                            <div style='color:white;font-size:0.85rem;'>{fmt_cad(avg_tax)}</div>
                        </div>
                    </div>
                    <div style='margin-top:0.7rem;font-size:0.7rem;color:#8892b0;border-top:1px solid #2d4a6e;padding-top:0.5rem;'>
                        💼 {dest["visa_difficulty"][:70]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Side-by-side comparison table
        st.divider()
        st.markdown("### 🔢 Key Metrics Comparison Table")
        rows = []
        for dest_name in selected_dests:
            dest = DESTINATIONS[dest_name]
            df   = projections[dest_name]
            ret  = df[df["Phase"] == "Retirement"]
            rows.append({
                "Destination": f"{dest['flag']} {dest_name.split(',')[0]}",
                "Monthly Cost (CAD)": f"${dest_expenses[dest_name]:,.0f}",
                "Annual Cost (CAD)":  f"${dest_expenses[dest_name]*12:,.0f}",
                "Portfolio @ Retire": fmt_cad(ret.iloc[0]["Total Portfolio"]) if not ret.empty else "—",
                "Portfolio @ End":    fmt_cad(df.iloc[-1]["Total Portfolio"]),
                "Avg Annual Tax":     fmt_cad(ret["Tax Paid (Canada)"].mean() + ret["Tax Paid (Local)"].mean()) if not ret.empty else "—",
                "Sustainability":     sustainability_score(df),
                "Inflation Rate":     f"{dest['inflation']*100:.1f}%",
                "Inv. Return":        f"{dest['investment_return']*100:.1f}%" if inv_override is None else f"{inv_override*100:.1f}%",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — PORTFOLIO GROWTH
    # ════════════════════════════════════════════════════════════════════════
    with page_tabs[3]:
        st.markdown("## 📈 Portfolio Value Over Time")

        fig = go.Figure()
        for i, dest_name in enumerate(selected_dests):
            df   = projections[dest_name]
            dest = DESTINATIONS[dest_name]
            fig.add_trace(go.Scatter(
                x=df["Age"], y=df["Total Portfolio"],
                name=f"{dest['flag']} {dest_name.split(',')[0]}",
                line=dict(color=colors[i % len(colors)], width=2.5),
                hovertemplate="Age %{x}: $%{y:,.0f} CAD<extra></extra>"
            ))
        fig.add_vline(x=retire_age, line_dash="dash", line_color="orange",
                      annotation_text=f"Retire {retire_age}", annotation_font_color="orange")
        fig.add_vline(x=cpp_start, line_dash="dot", line_color="#64ffda",
                      annotation_text=f"CPP {cpp_start}", annotation_font_color="#64ffda")
        fig.add_vline(x=oas_start, line_dash="dot", line_color="#bb86fc",
                      annotation_text=f"OAS {oas_start}", annotation_font_color="#bb86fc")
        fig.add_hline(y=0, line_color="red", line_dash="dash", opacity=0.5,
                      annotation_text="$0", annotation_font_color="red")
        fig.update_layout(template="plotly_dark", hovermode="x unified",
            yaxis_title="Portfolio Value (CAD)", xaxis_title="Age",
            legend=dict(orientation="h", yanchor="bottom", y=1.02), height=520)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown("### 🏦 Account-by-Account Breakdown")
        dest_acct = st.selectbox("Select destination for account breakdown", selected_dests, key="acct_dest")
        df0  = projections[dest_acct]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df0["Age"], y=df0["RRSP Balance"],
            name="RRSP/RRIF", fill="tozeroy", line=dict(color="#e94560"), stackgroup="one"))
        fig2.add_trace(go.Scatter(x=df0["Age"], y=df0["TFSA Balance"],
            name="TFSA", fill="tonexty", line=dict(color="#64ffda"), stackgroup="one"))
        fig2.add_trace(go.Scatter(x=df0["Age"], y=df0["Non-Reg Balance"],
            name="Non-Reg", fill="tonexty", line=dict(color="#bb86fc"), stackgroup="one"))
        fig2.add_vline(x=retire_age, line_dash="dash", line_color="orange")
        fig2.update_layout(template="plotly_dark", height=400,
            yaxis_title="Balance (CAD)", xaxis_title="Age",
            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig2, use_container_width=True)

        # Balance at key ages table
        st.markdown("### 📐 Portfolio Balance at Key Ages")
        key_ages = sorted(set([retire_age, cpp_start, oas_start, 71, 80, 90, lifespan]))
        key_ages = [a for a in key_ages if current_age <= a <= lifespan]
        rows_age = []
        for dest_name in selected_dests:
            dest = DESTINATIONS[dest_name]
            df   = projections[dest_name]
            row  = {"Destination": f"{dest['flag']} {dest_name.split(',')[0]}"}
            for a in key_ages:
                match = df[df["Age"] == a]
                row[f"Age {a}"] = fmt_cad(match.iloc[0]["Total Portfolio"]) if not match.empty else "—"
            rows_age.append(row)
        st.dataframe(pd.DataFrame(rows_age), use_container_width=True, hide_index=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — INCOME & WITHDRAWALS
    # ════════════════════════════════════════════════════════════════════════
    with page_tabs[4]:
        st.markdown("## 💸 Retirement Income & Withdrawal Strategy")

        dest_inc = st.selectbox("Select destination", selected_dests, key="income_dest")
        df_inc   = projections[dest_inc][projections[dest_inc]["Phase"] == "Retirement"]

        if not df_inc.empty:
            st.markdown("### Annual Income Stack vs Expenses")
            fig_inc = go.Figure()
            fig_inc.add_trace(go.Bar(x=df_inc["Age"], y=df_inc["CPP Benefit"],
                name="CPP", marker_color="#64ffda"))
            fig_inc.add_trace(go.Bar(x=df_inc["Age"], y=df_inc["OAS Benefit"],
                name="OAS", marker_color="#bb86fc"))
            if df_inc["DB Pension"].sum() > 0:
                fig_inc.add_trace(go.Bar(x=df_inc["Age"], y=df_inc["DB Pension"],
                    name="DB Pension", marker_color="#f4a261"))
            fig_inc.add_trace(go.Bar(x=df_inc["Age"], y=df_inc["RRSP Withdrawal"],
                name="RRSP/RRIF Withdrawal", marker_color="#e94560"))
            fig_inc.add_trace(go.Bar(x=df_inc["Age"], y=df_inc["TFSA Withdrawal"],
                name="TFSA Withdrawal", marker_color="#ffd166"))
            if df_inc["DC Withdrawal"].sum() > 0:
                fig_inc.add_trace(go.Bar(x=df_inc["Age"], y=df_inc["DC Withdrawal"],
                    name="DC Pension Withdrawal", marker_color="#e76f51"))
            fig_inc.add_trace(go.Bar(x=df_inc["Age"], y=df_inc["NonReg Withdrawal"],
                name="Non-Reg Withdrawal", marker_color="#06d6a0"))
            fig_inc.add_trace(go.Scatter(x=df_inc["Age"], y=df_inc["Annual Expenses (CAD)"],
                name="Total Expenses", line=dict(color="white", width=2.5, dash="dash")))
            fig_inc.update_layout(barmode="stack", template="plotly_dark", height=460,
                yaxis_title="CAD / year", xaxis_title="Age",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                hovermode="x unified")
            st.plotly_chart(fig_inc, use_container_width=True)

            st.markdown("### Annual Net Surplus / Deficit")
            sd_colors = ["#06d6a0" if v >= 0 else "#e94560" for v in df_inc["Net Surplus/Deficit"]]
            fig_sd = go.Figure(go.Bar(
                x=df_inc["Age"], y=df_inc["Net Surplus/Deficit"],
                marker_color=sd_colors
            ))
            fig_sd.add_hline(y=0, line_color="white", line_dash="dash")
            fig_sd.update_layout(template="plotly_dark", height=300,
                yaxis_title="CAD", xaxis_title="Age")
            st.plotly_chart(fig_sd, use_container_width=True)

            st.markdown("### Income Source Mix (%)")
            total_w = (df_inc["RRSP Withdrawal"] + df_inc["TFSA Withdrawal"] +
                       df_inc["NonReg Withdrawal"] + df_inc["DC Withdrawal"] +
                       df_inc["CPP Benefit"] + df_inc["OAS Benefit"] + df_inc["DB Pension"])
            total_w = total_w.replace(0, np.nan)
            fig_mix = go.Figure()
            mix_sources = [
                ("CPP Benefit",      "#64ffda", "CPP"),
                ("OAS Benefit",      "#bb86fc", "OAS"),
                ("DB Pension",       "#f4a261", "DB Pension"),
                ("RRSP Withdrawal",  "#e94560", "RRSP/RRIF"),
                ("TFSA Withdrawal",  "#ffd166", "TFSA"),
                ("DC Withdrawal",    "#e76f51", "DC Pension"),
                ("NonReg Withdrawal","#06d6a0", "Non-Reg"),
            ]
            for col_name, color_val, label in mix_sources:
                if df_inc[col_name].sum() > 0:
                    pct = (df_inc[col_name] / total_w * 100).fillna(0)
                    fig_mix.add_trace(go.Scatter(x=df_inc["Age"], y=pct,
                        name=label, stackgroup="one", line=dict(color=color_val)))
            fig_mix.update_layout(template="plotly_dark", height=320,
                yaxis_title="% of total income", xaxis_title="Age",
                legend=dict(orientation="h", yanchor="bottom", y=1.02))
            st.plotly_chart(fig_mix, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 5 — TAX ANALYSIS
    # ════════════════════════════════════════════════════════════════════════
    with page_tabs[5]:
        st.markdown("## 🧾 Tax Analysis")

        # Lifetime tax comparison
        tax_summary = []
        for dest_name in selected_dests:
            dest = DESTINATIONS[dest_name]
            df   = projections[dest_name][projections[dest_name]["Phase"] == "Retirement"]
            if df.empty:
                continue
            total_tax     = df["Tax Paid (Canada)"].sum() + df["Tax Paid (Local)"].sum()
            total_income  = df["RRSP Withdrawal"].sum() + df["CPP Benefit"].sum() + df["OAS Benefit"].sum()
            eff_rate      = total_tax / total_income if total_income > 0 else 0
            tax_summary.append({
                "Destination": f"{dest['flag']} {dest_name.split(',')[0]}",
                "Lifetime Tax": total_tax,
                "Avg Annual Tax": df["Tax Paid (Canada)"].mean() + df["Tax Paid (Local)"].mean(),
                "Avg Withholding/yr": df["Withholding Tax"].mean(),
                "Effective Rate": f"{eff_rate:.1%}",
            })

        if tax_summary:
            ts_df = pd.DataFrame(tax_summary)

            tc1, tc2 = st.columns(2)
            with tc1:
                fig_lt = go.Figure(go.Bar(
                    x=ts_df["Destination"], y=ts_df["Lifetime Tax"],
                    marker_color=colors[:len(ts_df)],
                    text=[fmt_cad(v) for v in ts_df["Lifetime Tax"]],
                    textposition="outside"
                ))
                fig_lt.update_layout(template="plotly_dark", height=380,
                    yaxis_title="CAD", title="Lifetime Tax Burden")
                st.plotly_chart(fig_lt, use_container_width=True)
            with tc2:
                fig_avg = go.Figure(go.Bar(
                    x=ts_df["Destination"], y=ts_df["Avg Annual Tax"],
                    marker_color=colors[:len(ts_df)],
                    text=[fmt_cad(v) for v in ts_df["Avg Annual Tax"]],
                    textposition="outside"
                ))
                fig_avg.update_layout(template="plotly_dark", height=380,
                    yaxis_title="CAD/yr", title="Average Annual Tax")
                st.plotly_chart(fig_avg, use_container_width=True)

            # Comparison table
            st.dataframe(ts_df, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### 📜 Tax Rules per Destination")
        for dest_name in selected_dests:
            dest     = DESTINATIONS[dest_name]
            tax_info = dest["tax_info"]
            with st.expander(f"{dest['flag']}  {dest_name} — Full Tax Details"):
                st.info(tax_info["note"])
                m1, m2, m3 = st.columns(3)
                m1.metric("OAS NR Withholding",  f"{tax_info.get('oas_withholding',  0)*100:.0f}%")
                m2.metric("CPP NR Withholding",  f"{tax_info.get('cpp_withholding',  0)*100:.0f}%")
                m3.metric("RRSP NR Withholding", f"{tax_info.get('rrsp_withholding', 0)*100:.0f}%")

                if tax_info.get("nhr_regime"):
                    st.success(f"✅ Portugal NHR 2.0: {tax_info['nhr_rate']*100:.0f}% flat on foreign pensions for {tax_info['nhr_years']} years")
                if tax_info.get("pensioner_flat_tax"):
                    st.success(f"✅ Greece pensioner flat tax: {tax_info['pensioner_flat_rate']*100:.0f}% on all foreign income for {tax_info['pensioner_flat_years']} years")
                if tax_info.get("beckham_law"):
                    st.success("✅ Spain Beckham Law: 24% flat on Spanish-source income for first 6 years")
                if tax_info.get("departure_tax"):
                    st.warning("⚠️ Departure tax applies when leaving Canada — deemed disposition of non-registered assets")

                df_ret = projections[dest_name][projections[dest_name]["Phase"] == "Retirement"]
                if not df_ret.empty:
                    fig_tx = go.Figure()
                    fig_tx.add_trace(go.Bar(x=df_ret["Age"], y=df_ret["Tax Paid (Canada)"],
                        name="Canadian Tax + Withholding", marker_color="#e94560"))
                    fig_tx.add_trace(go.Bar(x=df_ret["Age"], y=df_ret["Tax Paid (Local)"],
                        name="Local Country Tax", marker_color="#ffd166"))
                    if df_ret["OAS Clawback"].sum() > 0:
                        fig_tx.add_trace(go.Bar(x=df_ret["Age"], y=df_ret["OAS Clawback"],
                            name="OAS Clawback", marker_color="#bb86fc"))
                    fig_tx.update_layout(barmode="stack", template="plotly_dark", height=280,
                        yaxis_title="CAD", xaxis_title="Age",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02))
                    st.plotly_chart(fig_tx, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 6 — DATA TABLES
    # ════════════════════════════════════════════════════════════════════════
    with page_tabs[6]:
        st.markdown("## 📊 Detailed Year-by-Year Data")

        dest_tbl = st.selectbox("Select destination", selected_dests, key="table_dest")
        df_raw   = projections[dest_tbl]

        # Milestones
        st.markdown("### 🏁 Key Financial Milestones")
        milestones = []
        ret_rows = df_raw[df_raw["Phase"] == "Retirement"]
        if not ret_rows.empty:
            milestones.append({"Event": "🎯 Retirement begins", "Age": retire_age,
                "Portfolio": fmt_cad(ret_rows.iloc[0]["Total Portfolio"])})
        cpp_r = df_raw[df_raw["CPP Benefit"] > 0]
        if not cpp_r.empty:
            milestones.append({"Event": "💰 CPP begins", "Age": int(cpp_r.iloc[0]["Age"]),
                "Portfolio": fmt_cad(cpp_r.iloc[0]["Total Portfolio"])})
        oas_r = df_raw[df_raw["OAS Benefit"] > 0]
        if not oas_r.empty:
            milestones.append({"Event": "👴 OAS begins", "Age": int(oas_r.iloc[0]["Age"]),
                "Portfolio": fmt_cad(oas_r.iloc[0]["Total Portfolio"])})
        peak  = df_raw.loc[df_raw["Total Portfolio"].idxmax()]
        milestones.append({"Event": "📈 Peak portfolio", "Age": int(peak["Age"]),
            "Portfolio": fmt_cad(peak["Total Portfolio"])})
        depl = df_raw[df_raw["Total Portfolio"] <= 0]
        if not depl.empty:
            milestones.append({"Event": "⚠️ Portfolio depleted", "Age": int(depl.iloc[0]["Age"]),
                "Portfolio": "$0"})
        else:
            final = df_raw.iloc[-1]
            milestones.append({"Event": f"✅ Final balance (age {lifespan})", "Age": lifespan,
                "Portfolio": fmt_cad(final["Total Portfolio"])})
        st.dataframe(pd.DataFrame(milestones), use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### 📋 Full Annual Projection")

        money_cols = [
            "RRSP Balance", "TFSA Balance", "Non-Reg Balance", "DC Pension Balance", "Total Portfolio",
            "Gross Income", "CPP Benefit", "OAS Benefit", "DB Pension",
            "RRSP Withdrawal", "TFSA Withdrawal", "DC Withdrawal", "NonReg Withdrawal",
            "Annual Expenses (CAD)", "Tax Paid (Canada)", "Tax Paid (Local)",
            "Withholding Tax", "Net Surplus/Deficit", "OAS Clawback",
        ]
        disp = df_raw[["Age", "Year", "Phase"] + money_cols].copy()
        for c in money_cols:
            disp[c] = disp[c].apply(lambda x: f"${x:,.0f}")

        st.dataframe(disp, use_container_width=True, hide_index=True, height=520)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("""
    <div style='background:#1e2a3a;padding:1rem;border-radius:8px;font-size:0.8rem;color:#8892b0;'>
    ⚠️ <strong>Disclaimer:</strong> For educational planning purposes only. Tax rules, benefit amounts,
    and costs change frequently. Consult a CFP, CPA, and immigration lawyer before decisions.
    CPP/OAS are estimates. Foreign tax rules (NHR, Greek pensioner regime, etc.) should be verified
    with local advisors. Exchange rates as of 2024/2025.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
