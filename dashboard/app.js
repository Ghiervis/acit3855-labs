const processingURL = "http://34.218.112.68:8100/stats";
const analyzerURL = "http://34.218.112.68:8110/stats";
const ppEventBaseURL = "http://34.218.112.68:8110/events/player-performance";
const aiEventBaseURL = "http://34.218.112.68:8110/events/audience-interaction";
const checkURL = "http://34.218.112.68:8200/checks";

function updateDashboard() {
  // Update stats from processing
  fetch(processingURL)
    .then(res => res.json())
    .then(data => {
      document.getElementById("stats").textContent = JSON.stringify(data, null, 2);
      document.getElementById("updated-time").textContent = new Date().toLocaleString();
    })
    .catch(err => console.error("Processing fetch failed:", err));

  // Update stats from analyzer
  fetch(analyzerURL)
    .then(res => res.json())
    .then(data => {
      document.getElementById("analyzer").textContent = JSON.stringify(data, null, 2);

      // Get random indexes
      const ppIndex = Math.floor(Math.random() * data.num_player_performance);
      const aiIndex = Math.floor(Math.random() * data.num_audience_interaction);

      // Fetch random player-performance event
      fetch(`${ppEventBaseURL}?index=${ppIndex}`)
        .then(res => res.ok ? res.json() : Promise.reject("PP fetch error"))
        .then(pp => {
          document.getElementById("pp-event").textContent = JSON.stringify(pp, null, 2);
        })
        .catch(err => {
          console.error("Random player-performance event error:", err);
          document.getElementById("pp-event").textContent = "Error loading player-performance event.";
        });

      // Fetch random audience-interaction event
      fetch(`${aiEventBaseURL}?index=${aiIndex}`)
        .then(res => res.ok ? res.json() : Promise.reject("AI fetch error"))
        .then(ai => {
          document.getElementById("ai-event").textContent = JSON.stringify(ai, null, 2);
        })
        .catch(err => {
          console.error("Random audience-interaction event error:", err);
          document.getElementById("ai-event").textContent = "Error loading audience-interaction event.";
        });

    })
    .catch(err => {
      console.error("Analyzer fetch failed:", err);
      document.getElementById("analyzer").textContent = "Error loading analyzer stats.";
    });

  fetch(checkURL)
    .then(res => res.json())
    .then(data => {
      document.getElementById("consistency-check").textContent = JSON.stringify(data, null, 2);
    })
    .catch(err => {
      document.getElementById("consistency-check").textContent = "Failed to fetch consistency check.";
    });
}

// Auto refresh every 3 seconds
setInterval(updateDashboard, 3000);
updateDashboard();
