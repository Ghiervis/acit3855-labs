const processingURL = "http://34.218.112.68:8100/stats";
const analyzerURL = "http://34.218.112.68:8110/stats";
const ppEventURL = "http://34.218.112.68:8110/events/player-performance?index=0";
const aiEventURL = "http://34.218.112.68:8110/events/audience-interaction/index=0";

function updateDashboard() {
  // Stats from processing
  fetch(processingURL)
    .then(res => res.json())
    .then(data => {
      document.getElementById("stats").textContent = JSON.stringify(data, null, 2);
      document.getElementById("updated-time").textContent = new Date().toLocaleString();
    })
    .catch(err => console.error("Processing fetch failed:", err));

  // Stats from analyzer
  fetch(analyzerURL)
    .then(res => res.json())
    .then(data => {
      document.getElementById("analyzer").textContent = JSON.stringify(data, null, 2);
    })
    .catch(err => console.error("Analyzer fetch failed:", err));

  // One event of each type
  Promise.all([
    fetch(ppEventURL).then(res => res.ok ? res.json() : Promise.reject("PP fetch error")),
    fetch(aiEventURL).then(res => res.ok ? res.json() : Promise.reject("AI fetch error"))
  ])
  .then(([pp, ai]) => {
    const display = {
      "Player Performance": pp,
      "Audience Interaction": ai
    };
    document.getElementById("event").textContent = JSON.stringify(display, null, 2);
  })
  .catch(err => {
    console.error("Event fetch error:", err);
    document.getElementById("event").textContent = "Error fetching event data.";
  });
}

setInterval(updateDashboard, 3000);
updateDashboard();
