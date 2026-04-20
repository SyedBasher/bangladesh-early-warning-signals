"""
signal_definitions.py
---------------------
Channel metadata for Bangladesh macroeconomic early warning signals.

Each of the 16 monitored channels has two direction variants:
  - tightening: deteriorating conditions (constraint binding harder)
  - easing:     improving conditions (constraint relaxing)

The classifier (interpret_events.py) picks the channel AND direction
independently for each headline via LLM classification. Lookups against
this dict pull the appropriate metadata block for display.
"""

CHANNELS = {

    # ================================================================
    # EXTERNAL SECTOR
    # ================================================================

    "Foreign Exchange": {
        "tightening": {
            "title": "External Liquidity Stress",
            "signal_type": "balance_of_payments",
            "lead_indicator": "fx_reserves_pressure",
            "time_horizon": "1–3 months",
            "economic_mechanism":
                "Foreign exchange shortages constrain import financing, widen the informal premium, and force rationing of dollar-denominated obligations.",
            "who_should_care": ["trade finance banks", "importers", "currency desks"],
            "expected_effects": ["import compression", "industrial input shortage", "informal FX premium widening"],
        },
        "easing": {
            "title": "External Liquidity Improvement",
            "signal_type": "balance_of_payments",
            "lead_indicator": "fx_reserves_recovery",
            "time_horizon": "1–3 months",
            "economic_mechanism":
                "Rising reserves and improved BoP position ease import financing constraints, narrow the informal FX premium, and restore normal trade settlement.",
            "who_should_care": ["trade finance banks", "importers", "currency desks"],
            "expected_effects": ["import normalization", "informal FX premium narrowing", "reserve buffer strengthening"],
        },
    },

    "Exports": {
        "tightening": {
            "title": "Export Demand Contraction",
            "signal_type": "balance_of_payments",
            "lead_indicator": "export_orders_decline",
            "time_horizon": "1–3 months",
            "economic_mechanism":
                "Weak external demand reduces factory utilization, compresses labor income, and lowers FX earnings.",
            "who_should_care": ["exporters", "garment sector", "currency desks"],
            "expected_effects": ["lower manufacturing output", "urban income slowdown", "FX earnings pressure"],
        },
        "easing": {
            "title": "Export Demand Expansion",
            "signal_type": "balance_of_payments",
            "lead_indicator": "export_orders_increase",
            "time_horizon": "1–3 months",
            "economic_mechanism":
                "Rising external demand lifts factory utilization, expands labor income, and strengthens FX earnings.",
            "who_should_care": ["exporters", "garment sector", "currency desks"],
            "expected_effects": ["higher manufacturing output", "urban employment gains", "FX earnings boost"],
        },
    },

    "Remittances": {
        "tightening": {
            "title": "Remittance Flow Disruption",
            "signal_type": "balance_of_payments",
            "lead_indicator": "remittance_growth_decline",
            "time_horizon": "1–3 months",
            "economic_mechanism":
                "Remittance slowdown reduces rural household income, weakens consumption demand, and tightens FX supply.",
            "who_should_care": ["rural economy analysts", "consumer sector", "central bank"],
            "expected_effects": ["rural consumption slowdown", "FX supply reduction", "hundi channel widening"],
        },
        "easing": {
            "title": "Remittance Flow Strengthening",
            "signal_type": "balance_of_payments",
            "lead_indicator": "remittance_growth_acceleration",
            "time_horizon": "1–3 months",
            "economic_mechanism":
                "Rising remittances lift rural household income, strengthen consumption demand, and expand formal FX supply.",
            "who_should_care": ["rural economy analysts", "consumer sector", "central bank"],
            "expected_effects": ["rural consumption boost", "FX supply expansion", "formal channel share rising"],
        },
    },

    # ================================================================
    # ENERGY & PRODUCTION
    # ================================================================

    "Energy": {
        "tightening": {
            "title": "Energy Supply Constraint",
            "signal_type": "production_constraint",
            "lead_indicator": "load_shedding_intensity",
            "time_horizon": "immediate",
            "economic_mechanism":
                "Energy shortages restrict industrial operating hours, raise unit costs, and force firms to rely on expensive captive generation.",
            "who_should_care": ["industrial producers", "manufacturers", "energy traders"],
            "expected_effects": ["output loss", "production cost increase", "cost-push inflation"],
        },
        "easing": {
            "title": "Energy Supply Improvement",
            "signal_type": "production_constraint",
            "lead_indicator": "load_shedding_reduction",
            "time_horizon": "immediate",
            "economic_mechanism":
                "Improved power and gas supply expands industrial operating hours, lowers unit costs, and reduces reliance on captive generation.",
            "who_should_care": ["industrial producers", "manufacturers", "energy traders"],
            "expected_effects": ["output normalization", "production cost relief", "inflation pressure easing"],
        },
    },

    "Logistics": {
        "tightening": {
            "title": "Logistics Disruption",
            "signal_type": "production_constraint",
            "lead_indicator": "transport_bottleneck",
            "time_horizon": "immediate–1 month",
            "economic_mechanism":
                "Port congestion, transport disruption, or infrastructure failure raises delivery times and costs across supply chains.",
            "who_should_care": ["exporters", "importers", "logistics firms"],
            "expected_effects": ["supply chain delays", "higher transport costs", "export shipment bottleneck"],
        },
        "easing": {
            "title": "Logistics Improvement",
            "signal_type": "production_constraint",
            "lead_indicator": "transport_capacity_expansion",
            "time_horizon": "immediate–1 month",
            "economic_mechanism":
                "Port throughput gains, transport improvements, or new infrastructure cut delivery times and lower costs across supply chains.",
            "who_should_care": ["exporters", "importers", "logistics firms"],
            "expected_effects": ["supply chain acceleration", "lower transport costs", "export throughput gains"],
        },
    },

    # ================================================================
    # FINANCIAL CONDITIONS
    # ================================================================

    "Credit": {
        "tightening": {
            "title": "Credit Allocation Tightening",
            "signal_type": "financial_conditions",
            "lead_indicator": "credit_growth_slowdown",
            "time_horizon": "3–6 months",
            "economic_mechanism":
                "Bank lending constraints reduce investment and working capital availability across the real economy.",
            "who_should_care": ["commercial banks", "corporate borrowers", "investment desks"],
            "expected_effects": ["investment slowdown", "working capital shortages", "lower GDP growth"],
        },
        "easing": {
            "title": "Credit Allocation Loosening",
            "signal_type": "financial_conditions",
            "lead_indicator": "credit_growth_acceleration",
            "time_horizon": "3–6 months",
            "economic_mechanism":
                "Expanded bank lending improves investment and working capital availability across the real economy.",
            "who_should_care": ["commercial banks", "corporate borrowers", "investment desks"],
            "expected_effects": ["investment pickup", "working capital expansion", "GDP growth support"],
        },
    },

    "Banking": {
        "tightening": {
            "title": "Banking Sector Fragility",
            "signal_type": "financial_conditions",
            "lead_indicator": "npl_ratio_deterioration",
            "time_horizon": "3–12 months",
            "economic_mechanism":
                "Rising non-performing loans, governance failures, or liquidity stress in banks constrain credit intermediation and erode depositor confidence.",
            "who_should_care": ["depositors", "bank regulators", "financial analysts"],
            "expected_effects": ["credit rationing", "deposit flight risk", "fiscal contingent liability"],
        },
        "easing": {
            "title": "Banking Sector Strengthening",
            "signal_type": "financial_conditions",
            "lead_indicator": "npl_ratio_improvement",
            "time_horizon": "3–12 months",
            "economic_mechanism":
                "Declining NPLs, stronger governance, or improved liquidity conditions restore credit intermediation capacity and depositor confidence.",
            "who_should_care": ["depositors", "bank regulators", "financial analysts"],
            "expected_effects": ["credit expansion capacity", "deposit confidence", "contingent liability easing"],
        },
    },

    "Monetary Policy": {
        "tightening": {
            "title": "Monetary Policy Tightening",
            "signal_type": "financial_conditions",
            "lead_indicator": "policy_rate_hike",
            "time_horizon": "1–6 months",
            "economic_mechanism":
                "Central bank tightening raises borrowing costs, slows credit expansion, and signals concern about inflation or external balance.",
            "who_should_care": ["banks", "bond market", "corporate treasurers"],
            "expected_effects": ["higher borrowing costs", "bond yield rise", "investment dampening"],
        },
        "easing": {
            "title": "Monetary Policy Easing",
            "signal_type": "financial_conditions",
            "lead_indicator": "policy_rate_cut",
            "time_horizon": "1–6 months",
            "economic_mechanism":
                "Central bank easing lowers borrowing costs, supports credit expansion, and signals confidence that inflation and external balances permit stimulus.",
            "who_should_care": ["banks", "bond market", "corporate treasurers"],
            "expected_effects": ["lower borrowing costs", "bond yield decline", "investment support"],
        },
    },

    # ================================================================
    # PRICES & FOOD SECURITY
    # ================================================================

    "Food Prices": {
        "tightening": {
            "title": "Food Price Pressure",
            "signal_type": "price_signal",
            "lead_indicator": "staple_price_acceleration",
            "time_horizon": "immediate–3 months",
            "economic_mechanism":
                "Rising staple prices compress real incomes of the poor, raise wage demands, and feed into broader inflation expectations.",
            "who_should_care": ["consumer sector", "food importers", "social protection agencies"],
            "expected_effects": ["real income erosion for the poor", "wage pressure", "headline inflation rise"],
        },
        "easing": {
            "title": "Food Price Relief",
            "signal_type": "price_signal",
            "lead_indicator": "staple_price_deceleration",
            "time_horizon": "immediate–3 months",
            "economic_mechanism":
                "Stabilizing or falling staple prices restore real incomes of the poor, ease wage pressure, and moderate inflation expectations.",
            "who_should_care": ["consumer sector", "food importers", "social protection agencies"],
            "expected_effects": ["real income recovery for the poor", "wage pressure easing", "headline inflation moderation"],
        },
    },

    "Agriculture": {
        "tightening": {
            "title": "Climate & Agricultural Shock",
            "signal_type": "supply_shock",
            "lead_indicator": "crop_damage_report",
            "time_horizon": "1–6 months",
            "economic_mechanism":
                "Floods, droughts, or cyclones destroy crops and infrastructure, reducing agricultural output and triggering food price spikes.",
            "who_should_care": ["agricultural sector", "food security analysts", "insurers"],
            "expected_effects": ["crop output loss", "food price spike", "rural income contraction"],
        },
        "easing": {
            "title": "Agricultural Output Gain",
            "signal_type": "supply_shock",
            "lead_indicator": "crop_yield_increase",
            "time_horizon": "1–6 months",
            "economic_mechanism":
                "Favorable weather, strong harvests, or input availability raise agricultural output, ease food prices, and lift rural incomes.",
            "who_should_care": ["agricultural sector", "food security analysts", "consumer sector"],
            "expected_effects": ["crop output gain", "food price moderation", "rural income support"],
        },
    },

    # ================================================================
    # FISCAL & SOVEREIGN
    # ================================================================

    "Fiscal": {
        "tightening": {
            "title": "Fiscal Revenue Stress",
            "signal_type": "fiscal",
            "lead_indicator": "revenue_collection_shortfall",
            "time_horizon": "3–6 months",
            "economic_mechanism":
                "Tax revenue shortfalls force expenditure compression or borrowing, crowding out development spending and raising domestic debt costs.",
            "who_should_care": ["bond market", "development agencies", "government contractors"],
            "expected_effects": ["development spending cut", "domestic borrowing increase", "treasury yield pressure"],
        },
        "easing": {
            "title": "Fiscal Revenue Improvement",
            "signal_type": "fiscal",
            "lead_indicator": "revenue_collection_growth",
            "time_horizon": "3–6 months",
            "economic_mechanism":
                "Revenue collection gains relieve expenditure compression, support development spending, and ease pressure on domestic borrowing.",
            "who_should_care": ["bond market", "development agencies", "government contractors"],
            "expected_effects": ["development spending room", "domestic borrowing relief", "treasury yield easing"],
        },
    },

    "Political Risk": {
        "tightening": {
            "title": "Political Risk Escalation",
            "signal_type": "institutional",
            "lead_indicator": "governance_disruption",
            "time_horizon": "1–12 months",
            "economic_mechanism":
                "Political instability, policy reversals, or governance failures undermine investor confidence and raise country risk premia.",
            "who_should_care": ["foreign investors", "rating agencies", "multilateral lenders"],
            "expected_effects": ["FDI slowdown", "sovereign spread widening", "policy uncertainty premium"],
        },
        "easing": {
            "title": "Political Risk Moderation",
            "signal_type": "institutional",
            "lead_indicator": "governance_stabilization",
            "time_horizon": "1–12 months",
            "economic_mechanism":
                "Restored political stability, credible policy commitments, or institutional strengthening improve investor confidence and narrow country risk premia.",
            "who_should_care": ["foreign investors", "rating agencies", "multilateral lenders"],
            "expected_effects": ["FDI re-engagement", "sovereign spread narrowing", "policy predictability"],
        },
    },

    "Trade Policy": {
        "tightening": {
            "title": "Trade Policy Restriction",
            "signal_type": "policy_shock",
            "lead_indicator": "trade_regime_tightening",
            "time_horizon": "1–6 months",
            "economic_mechanism":
                "Import bans, tariff hikes, or trade partner restrictions alter relative prices and disrupt established supply chains.",
            "who_should_care": ["importers", "exporters", "trade policy analysts"],
            "expected_effects": ["supply chain disruption", "input cost increase", "trade diversion"],
        },
        "easing": {
            "title": "Trade Policy Liberalization",
            "signal_type": "policy_shock",
            "lead_indicator": "trade_regime_opening",
            "time_horizon": "1–6 months",
            "economic_mechanism":
                "Tariff reductions, liberalization measures, or preferential access agreements lower input costs and open new market access.",
            "who_should_care": ["importers", "exporters", "trade policy analysts"],
            "expected_effects": ["supply chain diversification", "input cost reduction", "export market expansion"],
        },
    },

    "Labor Market": {
        "tightening": {
            "title": "Labor Market Stress",
            "signal_type": "real_economy",
            "lead_indicator": "employment_disruption",
            "time_horizon": "1–6 months",
            "economic_mechanism":
                "Factory closures, layoffs, or wage arrears signal real-economy deterioration and reduce aggregate demand through income channels.",
            "who_should_care": ["garment sector", "labor unions", "consumer sector analysts"],
            "expected_effects": ["consumption contraction", "social tension", "urban poverty increase"],
        },
        "easing": {
            "title": "Labor Market Improvement",
            "signal_type": "real_economy",
            "lead_indicator": "employment_expansion",
            "time_horizon": "1–6 months",
            "economic_mechanism":
                "New hiring, wage gains, or overseas employment growth lift household incomes and support aggregate demand.",
            "who_should_care": ["garment sector", "labor unions", "consumer sector analysts"],
            "expected_effects": ["consumption support", "social stability", "poverty reduction"],
        },
    },

    # ================================================================
    # GEOPOLITICAL & EXTERNAL SHOCKS
    # ================================================================

    "Geopolitical Risk": {
        "tightening": {
            "title": "Geopolitical Risk Escalation",
            "signal_type": "external_shock",
            "lead_indicator": "geopolitical_tension_rise",
            "time_horizon": "1–6 months",
            "economic_mechanism":
                "Regional conflicts, trade sanctions, or Gulf state policy shifts disrupt migrant labor markets, trade routes, and energy supply chains affecting Bangladesh.",
            "who_should_care": ["exporters", "remittance-dependent sectors", "energy importers"],
            "expected_effects": ["remittance channel disruption", "trade route uncertainty", "energy price volatility"],
        },
        "easing": {
            "title": "Geopolitical Risk Moderation",
            "signal_type": "external_shock",
            "lead_indicator": "geopolitical_tension_decline",
            "time_horizon": "1–6 months",
            "economic_mechanism":
                "De-escalation of regional conflicts, restoration of Gulf labor channels, or stable trade arrangements reduce external risk premia for Bangladesh.",
            "who_should_care": ["exporters", "remittance-dependent sectors", "energy importers"],
            "expected_effects": ["remittance channel normalization", "trade route stability", "energy price moderation"],
        },
    },

    # ================================================================
    # CAPITAL MARKETS
    # ================================================================

    "Capital Markets": {
        "tightening": {
            "title": "Capital Markets Stress",
            "signal_type": "financial_conditions",
            "lead_indicator": "equity_market_decline",
            "time_horizon": "immediate–3 months",
            "economic_mechanism":
                "Equity market declines, FDI withdrawals, or portfolio outflows signal deteriorating investor confidence and tighter financing conditions.",
            "who_should_care": ["equity investors", "portfolio managers", "foreign investors"],
            "expected_effects": ["equity valuation decline", "FDI slowdown", "market liquidity tightening"],
        },
        "easing": {
            "title": "Capital Markets Recovery",
            "signal_type": "financial_conditions",
            "lead_indicator": "equity_market_rally",
            "time_horizon": "immediate–3 months",
            "economic_mechanism":
                "Equity market gains, FDI inflows, or portfolio inflows signal improving investor confidence and easier financing conditions.",
            "who_should_care": ["equity investors", "portfolio managers", "foreign investors"],
            "expected_effects": ["equity valuation gain", "FDI recovery", "market liquidity expansion"],
        },
    },

}


def get_metadata(channel, direction):
    """Return the metadata block for a (channel, direction) pair, or None."""
    return CHANNELS.get(channel, {}).get(direction)


def all_channels():
    return list(CHANNELS.keys())
