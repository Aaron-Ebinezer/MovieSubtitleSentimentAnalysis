document.getElementById('uploadForm').addEventListener('submit', async function (e) {
  e.preventDefault();

  const fileInput = document.getElementById('subtitleFile');
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);

  document.getElementById('loader').style.display = 'block';

  try {
    const response = await fetch('http://127.0.0.1:5000/upload', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Upload failed: ${errorText}`);
    }

    const result = await response.json();
    document.getElementById('loader').style.display = 'none';

    displayJson(result);
    displayPreview(result.preview);
    document.getElementById('totalLines').textContent = `Total lines processed: ${result.total_lines}`;

    drawCharts(result.emotion_counts);
    drawLineChart(result.timeline);
    drawRadarChart(result.emotion_counts);

  } catch (error) {
    document.getElementById('loader').style.display = 'none';
    alert('Failed to analyze. Please try again.\nError: ' + error.message);
    console.error('Error:', error);
  }
});

let barChart, pieChart, lineChart, radarChart;

function drawCharts(emotionCounts) {
  const ctxBar = document.getElementById('barChart').getContext('2d');
  const ctxPie = document.getElementById('pieChart').getContext('2d');

  const labels = Object.keys(emotionCounts);
  const data = Object.values(emotionCounts);

  if (barChart) barChart.destroy();
  if (pieChart) pieChart.destroy();

  barChart = new Chart(ctxBar, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Emotion Counts',
        data: data,
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 }
        }
      },
      plugins: {
        title: {
          display: true,
          text: 'Emotion Counts (Bar Chart)'
        }
      }
    }
  });

  pieChart = new Chart(ctxPie, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        label: 'Emotion Distribution',
        data: data,
        backgroundColor: labels.map(() => getRandomColor()),
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Emotion Distribution (Pie Chart)'
        },
        legend: {
          position: 'right',
          labels: { boxWidth: 15 }
        }
      }
    }
  });
}

function drawLineChart(timeline) {
  const ctxLine = document.getElementById('lineChart').getContext('2d');

  const labels = timeline.map(t => t.chunk);
  const emotions = [...new Set(timeline.flatMap(t => Object.keys(t)).filter(e => e !== 'chunk'))];

  const datasets = emotions.map(emotion => ({
    label: emotion,
    data: timeline.map(t => t[emotion] || 0),
    borderColor: getRandomColor(),
    fill: false,
    tension: 0.3
  }));

  if (lineChart) lineChart.destroy();

  lineChart = new Chart(ctxLine, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Emotion Flow Over Subtitle Timeline'
        }
      },
      scales: {
        y: { beginAtZero: true },
        x: { title: { display: true, text: 'Line Chunks' } }
      }
    }
  });
}

function drawRadarChart(emotionCounts) {
  const ctx = document.getElementById('radarChart').getContext('2d');

  if (radarChart) radarChart.destroy();

  radarChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: Object.keys(emotionCounts),
      datasets: [{
        label: 'Emotion Spread',
        data: Object.values(emotionCounts),
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Radar Chart: Emotion Spread'
        }
      },
      scales: {
        r: { beginAtZero: true }
      }
    }
  });
}

function getRandomColor() {
  const r = Math.floor(Math.random() * 200 + 30);
  const g = Math.floor(Math.random() * 200 + 30);
  const b = Math.floor(Math.random() * 200 + 30);
  return `rgb(${r},${g},${b})`;
}

function displayJson(obj) {
  document.getElementById('jsonOutput').textContent = JSON.stringify(obj, null, 2);
}

function displayPreview(previewData) {
  const tbody = document.getElementById('previewTable').querySelector('tbody');
  tbody.innerHTML = '';
  previewData.forEach(row => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${row.cleaned_text}</td><td>${row.emotion}</td>`;
    tbody.appendChild(tr);
  });
}
