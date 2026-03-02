SIGNALS = {

"external_liquidity_stress": {
    "keywords": [
        "dollar shortage","reserve fall","lc margin","import restriction",
        "kerb market","forex shortage","payment backlog"
    ],
    "channel": "external_sector",
    "transmission": [
        "import compression","industrial slowdown","employment pressure"
    ],
    "effect": "growth slowdown"
},

"exchange_rate_adjustment_pressure": {
    "keywords": [
        "exchange rate pressure","devaluation expectation","multiple rate",
        "crawling peg change","currency pressure"
    ],
    "channel": "expectations",
    "transmission": [
        "price expectations","hoarding","inflation acceleration"
    ],
    "effect": "inflation risk"
},

"export_demand_shock": {
    "keywords": [
        "export fall","shipment decline","orders drop","rmg orders",
        "buyers cut","apparel demand"
    ],
    "channel": "external_demand",
    "transmission": [
        "factory utilization","labor income","urban consumption"
    ],
    "effect": "income slowdown"
},

"remittance_flow_shift": {
    "keywords": [
        "remittance decline","hundi","remittance incentive",
        "migrant inflow drop"
    ],
    "channel": "external_sector",
    "transmission": [
        "fx liquidity","bank liquidity","imports"
    ],
    "effect": "fx pressure"
},

"energy_supply_constraint": {
    "keywords": [
        "load shedding","gas rationing","power outage","captive shutdown"
    ],
    "channel": "production",
    "transmission": [
        "industrial hours","output","wages"
    ],
    "effect": "output loss"
},

"energy_price_shock": {
    "keywords": [
        "fuel price","gas price","diesel price","electricity tariff"
    ],
    "channel": "cost_push",
    "transmission": [
        "transport cost","food prices","inflation"
    ],
    "effect": "regressive inflation"
},

"logistics_disruption": {
    "keywords": [
        "port congestion","container backlog","truck strike","shipment delay"
    ],
    "channel": "supply_chain",
    "transmission": [
        "delivery delay","inventory shortage","price volatility"
    ],
    "effect": "temporary inflation"
},

"banking_liquidity_stress": {
    "keywords": [
        "liquidity shortage","cash shortage","interbank rate spike","repo support"
    ],
    "channel": "financial",
    "transmission": [
        "credit contraction","working capital shortage","output"
    ],
    "effect": "growth slowdown"
},

"credit_allocation_tightening": {
    "keywords": [
        "loan cap","credit ceiling","lending restriction","sector lending limit"
    ],
    "channel": "financial",
    "transmission": [
        "investment slowdown"
    ],
    "effect": "lower investment"
},

"deposit_confidence_event": {
    "keywords": [
        "withdrawal panic","bank run","merger pressure","deposit concern"
    ],
    "channel": "financial",
    "transmission": [
        "deposit flight","lending contraction"
    ],
    "effect": "bank stress"
},

"import_compression_policy": {
    "keywords": [
        "import ban","luxury import restriction","lc restriction"
    ],
    "channel": "administrative",
    "transmission": [
        "shortages","price rise"
    ],
    "effect": "inflation volatility"
},

"price_control_intervention": {
    "keywords": [
        "price cap","admin price","fixed price","price ceiling"
    ],
    "channel": "administrative",
    "transmission": [
        "supply distortion","market shortage"
    ],
    "effect": "volatility"
},

"subsidy_adjustment": {
    "keywords": [
        "subsidy cut","fertilizer subsidy","fuel subsidy reduction"
    ],
    "channel": "fiscal",
    "transmission": [
        "cost push inflation"
    ],
    "effect": "inflation"
},

"labor_income_shock": {
    "keywords": [
        "layoff","overtime cut","factory closure","wage delay"
    ],
    "channel": "labor",
    "transmission": [
        "household consumption"
    ],
    "effect": "demand slowdown"
},

"industrial_capacity_shift": {
    "keywords": [
        "factory relocation","capacity shutdown","production halt"
    ],
    "channel": "production",
    "transmission": [
        "exports","employment"
    ],
    "effect": "medium-term slowdown"
}

}
