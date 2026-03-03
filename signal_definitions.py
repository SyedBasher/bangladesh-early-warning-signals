SIGNALS = {

# ---------------- EXTERNAL SECTOR ----------------

"external_liquidity_stress": {
    "title": "External Liquidity Stress Signal",
    "signal_type": "balance_of_payments",
    "lead_indicator": "fx_reserves_pressure",
    "time_horizon": "1-3 months",
    "direction": "tightening",
    "economic_mechanism":
        "Foreign exchange shortages constrain import financing and working capital.",
    "who_should_care": [
        "trade finance banks",
        "importers",
        "currency desks"
    ],
    "expected_effects": [
        "import compression",
        "industrial slowdown",
        "informal FX premium widening"
    ],
    "keywords": [
        "dollar shortage","forex shortage","forex crisis","reserve fall",
        "reserves drop","lc margin","lc opening","import payment backlog",
        "import payments delayed","kerb market","open market dollar"
    ]
},

"export_demand_shock": {
    "title": "Export Demand Contraction Signal",
    "signal_type": "balance_of_payments",
    "lead_indicator": "export_orders_decline",
    "time_horizon": "1-3 months",
    "direction": "tightening",
    "economic_mechanism":
        "Weak external demand reduces factory utilization and labor income.",
    "who_should_care": [
        "exporters",
        "garment sector",
        "currency desks"
    ],
    "expected_effects": [
        "lower manufacturing output",
        "urban income slowdown",
        "FX earnings pressure"
    ],
    "keywords": [
        "exports fall","export decline","shipment fall","orders fall",
        "orders drop","buyers cut orders","rmg orders drop",
        "garment demand weak","export earnings drop"
    ]
},

"energy_supply_constraint": {
    "title": "Energy Supply Constraint Signal",
    "signal_type": "production_constraint",
    "lead_indicator": "load_shedding_intensity",
    "time_horizon": "immediate",
    "direction": "tightening",
    "economic_mechanism":
        "Energy shortages restrict industrial operating hours.",
    "who_should_care": [
        "industrial producers",
        "manufacturers",
        "energy traders"
    ],
    "expected_effects": [
        "output loss",
        "wage pressure",
        "cost push inflation"
    ],
    "keywords": [
        "load shedding","power outage","gas crisis",
        "gas rationing","power cut"
    ]
},

"credit_allocation_tightening": {
    "title": "Credit Allocation Tightening Signal",
    "signal_type": "financial_conditions",
    "lead_indicator": "credit_growth_slowdown",
    "time_horizon": "3-6 months",
    "direction": "tightening",
    "economic_mechanism":
        "Bank lending constraints reduce investment and working capital.",
    "who_should_care": [
        "commercial banks",
        "corporate borrowers",
        "investment desks"
    ],
    "expected_effects": [
        "investment slowdown",
        "working capital shortages",
        "lower GDP growth"
    ],
    "keywords": [
        "loan cap","credit ceiling","lending restriction",
        "sector lending limit","bank stops lending",
        "bad loans"
    ]
}

}
