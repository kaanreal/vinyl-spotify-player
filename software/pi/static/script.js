const POLL_MS = 2000;

let playing = false;
let titleEl = document.getElementById("title");
let artistEl = document.getElementById("artist");
let artworkEl = document.getElementById("artwork");
let ppBtn = document.getElementById("playpause");
let setupOverlay = document.getElementById("setup-overlay");
let prevCover = "";

async function api(path, opts = {}) {
  try {
    let r = await fetch(path, { ...opts, headers: { "Accept": "application/json" } });
    return await r.json();
  } catch { return null; }
}

async function poll() {
  let data = await api("/api/status");
  if (!data) return;

  if (!data.authenticated) {
    setupOverlay.classList.add("visible");
    return;
  }
  setupOverlay.classList.remove("visible");

  playing = data.playing;
  ppBtn.textContent = playing ? "⏸" : "▶";

  if (playing) {
    artworkEl.classList.add("spin");
  } else {
    artworkEl.classList.remove("spin");
  }

  let track = data.track;
  if (track && track.title) {
    titleEl.textContent = track.title;
    artistEl.textContent = (track.artists || []).join(", ");
    if (track.cover_url && track.cover_url !== prevCover) {
      prevCover = track.cover_url;
      let img = new Image();
      img.onload = () => { artworkEl.style.backgroundImage = `url("${track.cover_url}")`; };
      img.src = track.cover_url;
    }
  } else {
    if (!prevCover) {
      titleEl.textContent = "No track playing";
      artistEl.textContent = "";
    }
  }
}

document.getElementById("playpause").addEventListener("click", () => {
  api(playing ? "/api/pause" : "/api/play", { method: "POST" });
});
document.getElementById("next").addEventListener("click", () => {
  api("/api/next", { method: "POST" });
});
document.getElementById("prev").addEventListener("click", () => {
  api("/api/prev", { method: "POST" });
});

poll();
setInterval(poll, POLL_MS);
