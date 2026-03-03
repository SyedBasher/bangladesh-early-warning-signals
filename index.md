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

Contact: syed.basher@gmail.com

---

## Latest Signals

<div id="signals"></div>

<script>
fetch('/bangladesh-early-warning-signals/data/signals.json')
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById('signals');

    data.slice().reverse().forEach(signal => {
      const block = document.createElement('div');
      block.style.marginBottom = "20px";

      const eventLabel = signal.event.replace(/_/g, " ");

      block.innerHTML = `
        <hr>
        <strong>${signal.date}</strong> — ${eventLabel}<br>
        ${signal.summary}<br>
        Channel: ${signal.channel}<br>
        Confidence: ${signal.confidence}<br>
        Importance: ${signal.importance}<br>
        <a href="${signal.sources[0]}" target="_blank">Source</a>
      `;

      container.appendChild(block);
    });
  })
  .catch(err => {
    document.getElementById('signals').innerText = "Could not load signals.";
    console.error(err);
  });
</script>
