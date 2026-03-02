SIGNALS = {

# ---------------- EXTERNAL SECTOR ----------------

"external_liquidity_stress": {
    "keywords": [
        "dollar shortage","forex shortage","forex crisis","reserve fall",
        "reserves drop","lc margin","lc opening","import payment backlog",
        "import payments delayed","kerb market","open market dollar",
        "bank unable to open lc","letter of credit problem"
    ],
    "channel": "external_sector",
    "transmission": [
        "import compression","industrial slowdown","employment pressure"
    ],
    "effect": "growth slowdown"
},

"exchange_rate_adjustment_pressure": {
    "keywords": [
        "taka depreciates","taka falls","currency weakens","devaluation",
        "exchange rate pressure","multiple exchange rate","crawling peg",
        "dollar rate rises","interbank rate rises"
    ],
    "channel": "expectations",
    "transmission": [
        "price expectations","hoarding","inflation acceleration"
    ],
    "effect": "inflation risk"
},

"export_demand_shock": {
    "keywords": [
        "exports fall","export decline","shipment fall","orders fall",
        "orders drop","buyers cut orders","rmg orders drop",
        "garment demand weak","export earnings drop"
    ],
    "channel": "external_demand",
    "transmission": [
        "factory utilization","labor income","urban consumption"
    ],
    "effect": "income slowdown"
},

"remittance_flow_shift": {
    "keywords": [
        "remittance falls","remittance drops","hundi","informal remittance",
        "remittance incentive","migrant inflow declines"
    ],
    "channel": "external_sector",
    "transmission": [
        "fx liquidity","bank liquidity","imports"
    ],
    "effect": "fx pressure"
},

# ---------------- ENERGY ----------------

"energy_supply_constraint": {
    "keywords": [
        "load shedding","loadshed","power outage","gas crisis",
        "gas rationing","captive power shutdown","power cut"
    ],
    "channel": "production",
    "transmission": [
        "industrial hours","output","wages"
    ],
    "effect": "output loss"
},

"energy_price_shock": {
    "keywords": [
        "gas price","gas prices","fuel price","fuel prices",
        "diesel price","petrol price","octane price",
        "electricity tariff","power tariff","energy price",
        "global oil price","lng price"
    ],
    "channel": "cost_push",
    "transmission": [
        "transport cost","food prices","inflation"
    ],
    "effect": "regressive inflation"
},

# ---------------- SUPPLY CHAIN ----------------

"logistics_disruption": {
    "keywords": [
        "port congestion","container backlog","shipment delay",
        "truck strike","transport strike","customs delay",
        "cargo stuck","clearance delay"
    ],
    "channel": "supply_chain",
    "transmission": [
        "delivery delay","inventory shortage","price volatility"
    ],
    "effect": "temporary inflation"
},

# ---------------- FINANCIAL SYSTEM ----------------

"banking_liquidity_stress": {
    "keywords": [
        "liquidity shortage","cash shortage","interbank rate spike",
        "repo support","central bank support","banks face liquidity pressure"
    ],
    "channel": "financial",
    "transmission": [
        "credit contraction","working capital shortage","output"
    ],
    "effect": "growth slowdown"
},

"credit_allocation_tightening": {
    "keywords": [
        "loan cap","credit ceiling","lending restriction",
        "sector lending limit","bank stops lending"
    ],
    "channel": "financial",
    "transmission": [
        "investment slowdown"
    ],
    "effect": "lower investment"
},

"deposit_confidence_event": {
    "keywords": [
        "withdrawal panic","bank run","depositors worried",
        "bank merger pressure","deposit safety concern"
    ],
    "channel": "financial",
    "transmission": [
        "deposit flight","lending contraction"
    ],
    "effect": "bank stress"
},

# ---------------- POLICY ----------------

"import_compression_policy": {
    "keywords": [
        "import ban","import restriction","luxury import restriction",
        "lc restriction","import control"
    ],
    "channel": "administrative",
    "transmission": [
        "shortages","price rise"
    ],
    "effect": "inflation volatility"
},

"price_control_intervention": {
    "keywords": [
        "price cap","price ceiling","fixed price","government price",
        "admin price"
    ],
    "channel": "administrative",
    "transmission": [
        "supply distortion","market shortage"
    ],
    "effect": "volatility"
},

"subsidy_adjustment": {
    "keywords": [
        "subsidy cut","fuel subsidy reduction","fertilizer subsidy",
        "subsidy reduced","subsidy withdrawn"
    ],
    "channel": "fiscal",
    "transmission": [
        "cost push inflation"
    ],
    "effect": "inflation"
},

# ---------------- LABOR & PRODUCTION ----------------

"labor_income_shock": {
    "keywords": [
        "layoffs","workers laid off","overtime cut",
        "factory closure","wage delay","salary delay"
    ],
    "channel": "labor",
    "transmission": [
        "household consumption"
    ],
    "effect": "demand slowdown"
},

"industrial_capacity_shift": {
    "keywords": [
        "factory relocation","capacity shutdown","production halt",
        "factory shuts down","plant closure"
    ],
    "channel": "production",
    "transmission": [
        "exports","employment"
    ],
    "effect": "medium-term slowdown"
}

}
