// Fetch the live banner state from status.json and update the page.
//
// status.json is the source of truth for the up/down banner. Edit it on
// GitHub (web UI or commit) to flip the banner; the page picks up the
// new state on next load. The query-string cache-buster prevents CDN
// caching of the fetched JSON.
//
// On any fetch failure we leave the safe defaults ("up!" with no
// message) in place rather than show stale or broken UI.
(async function () {
  try {
    const response = await fetch('status.json?t=' + Date.now(), {
      cache: 'no-store',
    });
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const data = await response.json();
    const statusEl = document.getElementById('status');
    const messageEl = document.getElementById('message');
    if (statusEl) statusEl.textContent = data.up || 'up!';
    if (messageEl) messageEl.textContent = data.message || '';
  } catch (e) {
    console.error('banner fetch failed:', e);
  }
})();
