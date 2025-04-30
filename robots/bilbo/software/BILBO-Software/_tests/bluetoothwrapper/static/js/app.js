async function fetchPaired() {
  const res = await fetch('/api/paired');
  const devices = await res.json();
  const tbody = document.querySelector('#paired-table tbody');
  tbody.innerHTML = '';
  devices.forEach(dev => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${dev.name}</td>
      <td>${dev.mac}</td>
      <td>${dev.connected ? 'Yes' : 'No'}</td>
      <td><button class="btn btn-danger btn-sm remove-btn" data-mac="${dev.mac}">Remove</button></td>
    `;
    tbody.appendChild(tr);
  });
  document.querySelectorAll('.remove-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const mac = btn.dataset.mac;
      await fetch('/api/remove', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mac})
      });
      fetchPaired();
    });
  });
}

async function fetchScan() {
  const res = await fetch('/api/scan');
  const devices = await res.json();
  const tbody = document.querySelector('#scan-table tbody');
  tbody.innerHTML = '';
  devices.forEach(dev => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${dev.name}</td>
      <td>${dev.mac}</td>
      <td><button class="btn btn-primary btn-sm connect-btn" data-mac="${dev.mac}">Connect</button></td>
    `;
    tbody.appendChild(tr);
  });
  document.querySelectorAll('.connect-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const mac = btn.dataset.mac;
      btn.disabled = true;
      btn.innerText = 'Connecting...';
      const res = await fetch('/api/pair', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mac})
      });
      const result = await res.json();
      console.log(result.output);
      btn.innerText = 'Connect';
      btn.disabled = false;
      fetchPaired();
    });
  });
}

// Initial load and intervals
fetchPaired();
fetchScan();
setInterval(fetchPaired, 5000);
setInterval(fetchScan, 10000);