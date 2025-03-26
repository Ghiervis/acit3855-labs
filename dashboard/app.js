const processingURL = "http://34.218.112.68:8100/stats";
const analyzerURL = "http://34.218.112.68:8110/stats";
const eventURL = "http://34.218.112.68:8110/events/player-performance"; // or audience-interaction

function updateDashboard() {
  fetch(processingURL)
    .then(res => res.json())
    .then(data => {
      document.getElementById("stats").textContent = JSON.stringify(data, null, 2);
      document.getElementById("updated-time").textContent = new Date().toLocaleString();
    });

  fetch(analyzerURL)
    .then(res => res.json())
    .then(data => {
      document.getElementById("analyzer").textContent = JSON.stringify(data, null, 2);
    });

  fetch(eventURL)
    .then(res => res.json())
    .then(data => {
      const random = data[Math.floor(Math.random() * data.length)];
      document.getElementById("event").textContent = JSON.stringify(random, null, 2);
    });
}

setInterval(updateDashboard, 3000);
updateDashboard();
