SIGNALS = {

# ================================================================
# EXTERNAL SECTOR
# ================================================================

"external_liquidity_stress": {
    "title": "External Liquidity Stress",
    "signal_type": "balance_of_payments",
    "lead_indicator": "fx_reserves_pressure",
    "time_horizon": "1–3 months",
    "direction": "tightening",
    "channel": "Foreign Exchange",
    "economic_mechanism":
        "Foreign exchange shortages constrain import financing, widen the informal premium, and force rationing of dollar-denominated obligations.",
    "who_should_care": [
        "trade finance banks",
        "importers",
        "currency desks"
    ],
    "expected_effects": [
        "import compression",
        "industrial input shortage",
        "informal FX premium widening"
    ],
    "keywords": [
        "dollar shortage", "forex shortage", "forex crisis",
        "reserve fall", "reserves drop", "reserves decline",
        "lc margin", "lc opening", "import payment backlog",
        "import payments delayed", "kerb market", "open market dollar",
        "dollar rate", "forex reserve", "bb reserve",
        "current account deficit", "balance of payment"
    ]
},

"export_demand_shock": {
    "title": "Export Demand Contraction",
    "signal_type": "balance_of_payments",
    "lead_indicator": "export_orders_decline",
    "time_horizon": "1–3 months",
    "direction": "tightening",
    "channel": "Exports",
    "economic_mechanism":
        "Weak external demand reduces factory utilization, compresses labor income, and lowers FX earnings.",
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
        "export fall", "export decline", "export drop",
        "shipment fall", "shipment decline",
        "order fall", "order drop", "order cancel",
        "buyer cut order", "rmg order drop", "rmg order cancel",
        "garment demand weak", "export earning drop",
        "export earning decline", "apparel export",
        "jute export", "leather export"
    ]
},

"remittance_flow_disruption": {
    "title": "Remittance Flow Disruption",
    "signal_type": "balance_of_payments",
    "lead_indicator": "remittance_growth_change",
    "time_horizon": "1–3 months",
    "direction": "tightening",
    "channel": "Remittances",
    "economic_mechanism":
        "Remittance slowdown reduces rural household income, weakens consumption demand, and tightens FX supply.",
    "who_should_care": [
        "rural economy analysts",
        "consumer sector",
        "central bank"
    ],
    "expected_effects": [
        "rural consumption slowdown",
        "FX supply reduction",
        "hundi channel widening"
    ],
    "keywords": [
        "remittance fall", "remittance decline", "remittance drop",
        "remittance slow", "expatriate income",
        "migrant worker", "manpower export",
        "hundi", "informal remittance",
        "wage earner remittance", "remittance inflow"
    ]
},

# ================================================================
# ENERGY & PRODUCTION
# ================================================================

"energy_supply_constraint": {
    "title": "Energy Supply Constraint",
    "signal_type": "production_constraint",
    "lead_indicator": "load_shedding_intensity",
    "time_horizon": "immediate",
    "direction": "tightening",
    "channel": "Energy",
    "economic_mechanism":
        "Energy shortages restrict industrial operating hours, raise unit costs, and force firms to rely on expensive captive generation.",
    "who_should_care": [
        "industrial producers",
        "manufacturers",
        "energy traders"
    ],
    "expected_effects": [
        "output loss",
        "production cost increase",
        "cost push inflation"
    ],
    "keywords": [
        "load shedding", "power outage", "gas crisis",
        "gas rationing", "power cut", "power shortage",
        "electricity shortage", "blackout", "gas supply cut",
        "fuel price hike", "diesel price", "lng import",
        "furnace oil", "power generation fall",
        "power plant shut", "energy crisis"
    ]
},

"infrastructure_logistics_disruption": {
    "title": "Infrastructure & Logistics Disruption",
    "signal_type": "production_constraint",
    "lead_indicator": "transport_bottleneck",
    "time_horizon": "immediate–1 month",
    "direction": "tightening",
    "channel": "Logistics",
    "economic_mechanism":
        "Port congestion, transport disruption, or infrastructure failure raises delivery times and costs across supply chains.",
    "who_should_care": [
        "exporters",
        "importers",
        "logistics firms"
    ],
    "expected_effects": [
        "supply chain delays",
        "higher transport costs",
        "export shipment bottleneck"
    ],
    "keywords": [
        "port congestion", "chittagong port", "chattogram port",
        "container jam", "container handling",
        "transport strike", "road block",
        "bridge collapse", "rail disruption", "shipping delay",
        "vessel delay", "freight rate", "port handling"
    ]
},

# ================================================================
# FINANCIAL CONDITIONS
# ================================================================

"credit_allocation_tightening": {
    "title": "Credit Allocation Tightening",
    "signal_type": "financial_conditions",
    "lead_indicator": "credit_growth_slowdown",
    "time_horizon": "3–6 months",
    "direction": "tightening",
    "channel": "Credit",
    "economic_mechanism":
        "Bank lending constraints reduce investment and working capital availability across the real economy.",
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
        "loan cap", "credit ceiling", "lending restriction",
        "sector lending limit", "bank stop lending",
        "credit growth slow", "private credit",
        "advance deposit ratio", "interest rate cap",
        "lending rate hike", "credit squeeze"
    ]
},

"banking_sector_fragility": {
    "title": "Banking Sector Fragility",
    "signal_type": "financial_conditions",
    "lead_indicator": "npl_ratio_change",
    "time_horizon": "3–12 months",
    "direction": "tightening",
    "channel": "Banking",
    "economic_mechanism":
        "Rising non-performing loans, governance failures, or liquidity stress in banks constrain credit intermediation and erode depositor confidence.",
    "who_should_care": [
        "depositors",
        "bank regulators",
        "financial analysts"
    ],
    "expected_effects": [
        "credit rationing",
        "deposit flight risk",
        "fiscal contingent liability"
    ],
    "keywords": [
        "bad loan", "non-performing loan", "npl rise",
        "default loan", "loan scam", "bank fraud",
        "bank liquidity crisis", "bank capital shortage",
        "deposit withdrawal", "bank run",
        "classified loan", "loan write-off",
        "loan reschedule", "bank merge"
    ]
},

"monetary_policy_shift": {
    "title": "Monetary Policy Shift",
    "signal_type": "financial_conditions",
    "lead_indicator": "policy_rate_change",
    "time_horizon": "1–6 months",
    "direction": "tightening",
    "channel": "Monetary Policy",
    "economic_mechanism":
        "Central bank tightening raises borrowing costs, slows credit expansion, and signals concern about inflation or external balance.",
    "who_should_care": [
        "banks",
        "bond market",
        "corporate treasurers"
    ],
    "expected_effects": [
        "higher borrowing costs",
        "bond yield rise",
        "investment dampening"
    ],
    "keywords": [
        "repo rate hike", "policy rate hike", "policy rate increase",
        "interest rate hike", "bangladesh bank tighten",
        "monetary tightening", "standing lending facility",
        "reverse repo", "treasury yield rise",
        "call money rate spike", "interbank rate",
        "repo rate", "policy rate", "bank rate"
    ]
},

# ================================================================
# PRICES & FOOD SECURITY
# ================================================================

"food_price_pressure": {
    "title": "Food Price Pressure",
    "signal_type": "price_signal",
    "lead_indicator": "staple_price_acceleration",
    "time_horizon": "immediate–3 months",
    "direction": "tightening",
    "channel": "Food Prices",
    "economic_mechanism":
        "Rising staple prices compress real incomes of the poor, raise wage demands, and feed into broader inflation expectations.",
    "who_should_care": [
        "consumer sector",
        "food importers",
        "social protection agencies"
    ],
    "expected_effects": [
        "real income erosion for the poor",
        "wage pressure",
        "headline inflation rise"
    ],
    "keywords": [
        "rice price rise", "rice price hike", "rice price surge",
        "onion price", "food price hike", "food inflation",
        "vegetable price", "edible oil price",
        "sugar price", "egg price", "chicken price",
        "essential commodity price", "tcb sale",
        "food price spike", "consumer price"
    ]
},

"climate_agricultural_shock": {
    "title": "Climate & Agricultural Shock",
    "signal_type": "supply_shock",
    "lead_indicator": "crop_damage_report",
    "time_horizon": "1–6 months",
    "direction": "tightening",
    "channel": "Agriculture",
    "economic_mechanism":
        "Floods, droughts, or cyclones destroy crops and infrastructure, reducing agricultural output and triggering food price spikes.",
    "who_should_care": [
        "agricultural sector",
        "food security analysts",
        "insurers"
    ],
    "expected_effects": [
        "crop output loss",
        "food price spike",
        "rural income contraction"
    ],
    "keywords": [
        "flood damage", "crop damage", "crop loss",
        "cyclone damage", "drought", "boro crop",
        "aman crop", "haor flood", "river erosion",
        "flash flood", "waterlogging", "salinity intrusion",
        "harvest loss", "paddy damage", "fishery loss"
    ]
},

# ================================================================
# FISCAL & SOVEREIGN
# ================================================================

"fiscal_revenue_stress": {
    "title": "Fiscal Revenue Stress",
    "signal_type": "fiscal",
    "lead_indicator": "revenue_collection_shortfall",
    "time_horizon": "3–6 months",
    "direction": "tightening",
    "channel": "Fiscal",
    "economic_mechanism":
        "Tax revenue shortfalls force expenditure compression or borrowing, crowding out development spending and raising domestic debt costs.",
    "who_should_care": [
        "bond market",
        "development agencies",
        "government contractors"
    ],
    "expected_effects": [
        "development spending cut",
        "domestic borrowing increase",
        "treasury yield pressure"
    ],
    "keywords": [
        "nbr revenue fall", "nbr revenue shortfall",
        "tax collection drop", "revenue target miss",
        "budget deficit widen", "government borrowing rise",
        "treasury bill yield", "national savings certificate",
        "austerity", "expenditure cut", "revenue mobilization",
        "nbr revenue", "revenue collection", "tax shortfall"
    ]
},

"sovereign_political_risk": {
    "title": "Sovereign & Political Risk",
    "signal_type": "institutional",
    "lead_indicator": "governance_disruption",
    "time_horizon": "1–12 months",
    "direction": "tightening",
    "channel": "Political Risk",
    "economic_mechanism":
        "Political instability, policy reversals, or governance failures undermine investor confidence and raise country risk premia.",
    "who_should_care": [
        "foreign investors",
        "rating agencies",
        "multilateral lenders"
    ],
    "expected_effects": [
        "FDI slowdown",
        "sovereign spread widening",
        "policy uncertainty premium"
    ],
    "keywords": [
        "hartal", "blockade", "strike shutdown",
        "political crisis", "protest violent",
        "credit rating downgrade", "imf condition", "imf reform",
        "world bank suspend", "governance failure",
        "policy reversal", "institutional crisis",
        "caretaker government", "election crisis"
    ]
},

"trade_policy_disruption": {
    "title": "Trade Policy Disruption",
    "signal_type": "policy_shock",
    "lead_indicator": "trade_regime_change",
    "time_horizon": "1–6 months",
    "direction": "tightening",
    "channel": "Trade Policy",
    "economic_mechanism":
        "Import bans, tariff changes, or trade partner restrictions alter relative prices and disrupt established supply chains.",
    "who_should_care": [
        "importers",
        "exporters",
        "trade policy analysts"
    ],
    "expected_effects": [
        "supply chain disruption",
        "input cost changes",
        "trade diversion"
    ],
    "keywords": [
        "import ban", "tariff hike", "tariff increase",
        "duty increase", "export restriction",
        "trade sanction", "anti-dumping",
        "safeguard duty", "regulatory duty",
        "import restriction", "customs duty hike",
        "gsp withdrawal", "trade preference"
    ]
},

"labor_market_stress": {
    "title": "Labor Market Stress",
    "signal_type": "real_economy",
    "lead_indicator": "employment_disruption",
    "time_horizon": "1–6 months",
    "direction": "tightening",
    "channel": "Labor Market",
    "economic_mechanism":
        "Factory closures, layoffs, or wage arrears signal real-economy deterioration and reduce aggregate demand through income channels.",
    "who_should_care": [
        "garment sector",
        "labor unions",
        "consumer sector analysts"
    ],
    "expected_effects": [
        "consumption contraction",
        "social tension",
        "urban poverty increase"
    ],
    "keywords": [
        "factory closure", "factory shut", "layoff",
        "worker retrench", "job loss", "job cut",
        "wage arrear", "wage protest", "minimum wage",
        "worker unrest", "unemployment rise",
        "worker lay off", "redundancy"
    ]
},

}
