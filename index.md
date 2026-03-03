# Bangladesh Economic Early Warning Signals

High-frequency indicators extracted from real-economy developments before official statistics.

---

## Purpose
This site publishes structured economic signals identifying constraint changes in the Bangladesh economy — foreign exchange, credit, energy, production, and prices.

The objective is early situational awareness for analysts, investors, and policy institutions.

---

## Dataset
Machine-readable feed:
/data/signals.json

Individual observations:
/signals/

---

## Method
Each signal records:
- economic channel
- direction of change
- transmission mechanism
- time horizon
- confidence level

Signals are derived from contemporaneous information flows, not retrospective macro data.

---

## Access
Public feed: delayed  
Institutional feed: real-time structured dataset

Contact: [syed.basher@gmail.com](mailto:syed.basher@gmail.com)

---

## Latest Signals

<div id="signals"></div>

<script>
fetch('/bangladesh-early-warning-signals/data/signals.json')
  .then(res => res.json())
  .then(data => {

    const container = document.getElementById('signals');
    container.innerHTML = "";

    data
      .slice()
      .reverse()
      .slice(0, 10)   // show latest 10 only
      .forEach(signal => {

        const block = document.createElement('div');
        block.style.marginBottom = "24px";

        const eventLabel = signal.event.replace(/_/g, " ");

        const color = {
          high: "#b30000",
          medium: "#cc8400",
          low: "#006600"
        }[signal.importance] || "#000";

        const source = (signal.sources && signal.sources.length)
          ? signal.sources[0]
          : "#";

        block.innerHTML = `
          <hr>
          <strong style="color:${color}; font-size:1.05em;">
            ${signal.date} — ${eventLabel}
          </strong><br>
          <div style="margin-top:4px;">
            ${signal.summary}
          </div>
          <div style="font-size:0.9em; margin-top:6px;">
            Channel: ${signal.channel} |
            Confidence: ${signal.confidence} |
            Importance: ${signal.importance}
          </div>
          <div style="margin-top:6px;">
            <a href="${source}" target="_blank">Source</a>
          </div>
        `;

        container.appendChild(block);
      });

  })
  .catch(err => {
    document.getElementById('signals').innerText =
      "Could not load signals.";
    console.error(err);
  });
</script>
