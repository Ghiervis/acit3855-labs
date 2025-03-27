const processingURL = "http://34.218.112.68:8100/stats";
const analyzerURL = "http://34.218.112.68:8110/stats";
const ppEventURL = "http://34.218.112.68:8110/events/player-performance/0";
const aiEventURL = "http://34.218.112.68:8110/events/audience-interaction/0";

function updateDashboard() {
  fetch(processingURL)
    .then(res => res.json())
    .then(data => {
      document.getElementById("stats").textContent = JSON.stringify(data, null, 2);
      document.getElementById("updated-time").textContent = new Date().toLocaleString();
    })
    .catch(err => console.error("Processing error:", err));

  fetch(analyzerURL)
    .then(res => res.json())
    .then(data => {
      document.getElementById("analyzer").textContent = JSON.stringify(data, null, 2);
    })
    .catch(err => console.error("Analyzer error:", err));

  Promise.all([
    fetch(ppEventURL).then(res => res.json()),
    fetch(aiEventURL).then(res => res.json())
  ])
    .then(([ppData, aiData]) => {
      const display = {
        "Player Performance Event": ppData,
        "Audience Interaction Event": aiData
      };
      document.getElementById("event").textContent = JSON.stringify(display, null, 2);
    })
    .catch(err => console.error("Event fetch error:", err));
}

setInterval(updateDashboard, 3000);
updateDashboard();
