# Bangladesh Economic Early Warning Signals

High-frequency constraint signals extracted from real-economy developments before official statistics.

**Live site:** [syedbasher.github.io/bangladesh-early-warning-signals](https://syedbasher.github.io/bangladesh-early-warning-signals/)

## How It Works

1. **Collect** — `scripts/collector.py` pulls headlines from Bangladesh newspaper RSS feeds twice daily
2. **Classify** — `interpret_events.py` matches headlines against 14 economic signal channels using keyword-based classification
3. **Publish** — structured signals are written to `data/signals.json` and daily snapshots to `signals/`
4. **Display** — `index.html` renders a real-time heatmap dashboard from the JSON feed

## Signal Channels (14)

| Channel | Type | Lead Indicator |
|---------|------|----------------|
| Foreign Exchange | Balance of Payments | FX reserves pressure |
| Exports | Balance of Payments | Export orders decline |
| Remittances | Balance of Payments | Remittance growth change |
| Energy | Production Constraint | Load shedding intensity |
| Logistics | Production Constraint | Transport bottleneck |
| Credit | Financial Conditions | Credit growth slowdown |
| Banking | Financial Conditions | NPL ratio change |
| Monetary Policy | Financial Conditions | Policy rate change |
| Food Prices | Price Signal | Staple price acceleration |
| Agriculture | Supply Shock | Crop damage report |
| Fiscal | Fiscal | Revenue collection shortfall |
| Political Risk | Institutional | Governance disruption |
| Trade Policy | Policy Shock | Trade regime change |
| Labor Market | Real Economy | Employment disruption |

## Data Access

- **Public feed (delayed):** `data/signals.json`
- **CSV export:** `data/signals.csv`
- **Institutional feed (real-time):** Contact [syed.basher@gmail.com](mailto:syed.basher@gmail.com)

## Setup

The pipeline runs automatically via GitHub Actions. To run manually:

```bash
python scripts/collector.py      # fetch headlines
python interpret_events.py       # classify and generate signals
python scripts/export_csv.py     # generate CSV export
```

## License

Signal methodology and definitions © Syed Basher. Data feed available under institutional license.
