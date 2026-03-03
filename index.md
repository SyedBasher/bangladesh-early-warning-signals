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
fetch('data/signals.json')
  .then(res => res.json())
  .then(data => {

    const container = document.getElementById('signals');
    container.innerHTML = "";

    data
      .slice()
      .reverse()
      .slice(0, 10)
      .forEach(signal => {

        const block = document.createElement('div');
        block.style.marginBottom = "28px";

        const color = {
          tightening: "#b30000",
          easing: "#006600"
        }[signal.direction] || "#000";

        block.innerHTML = `
          <hr>
          <strong style="color:${color}; font-size:1.1em;">
            ${signal.title}
          </strong><br>
          <em>${signal.date}</em><br><br>

          <strong>Mechanism:</strong>
          ${signal.economic_mechanism}<br><br>

          <strong>Expected Effects:</strong>
          <ul>
            ${signal.expected_effects.map(e => `<li>${e}</li>`).join("")}
          </ul>

          <strong>Who Should Care:</strong>
          ${signal.who_should_care.join(", ")}<br><br>

          <strong>Lead Indicator:</strong>
          ${signal.lead_indicator}<br>
          <strong>Time Horizon:</strong>
          ${signal.time_horizon}<br>
          <strong>Confidence:</strong>
          ${signal.confidence}<br><br>

          <a href="${signal.sources[0]}" target="_blank">
            Source Headline
          </a>
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
