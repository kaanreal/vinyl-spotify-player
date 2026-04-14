async function spotifyRequest(endpoint, method = "GET", body = null) {
    const SPOTIFY_ACCESS_TOKEN = await getAccessToken();
    return fetch("https://api.spotify.com/v1/" + endpoint, {
        method: method,
        headers: {
            "Authorization": "Bearer " + SPOTIFY_ACCESS_TOKEN,
            "Content-Type": "application/json"
        },
        body: body ? JSON.stringify(body) : null
    });
}

async function parseJsonSafe(response) {
    if (response.status === 204) {
        return null;
    }

    const text = await response.text();
    if (!text) {
        return null;
    }

    try {
        return JSON.parse(text);
    } catch (error) {
        console.error("Spotify response was not valid JSON:", error);
        return null;
    }
}

function getCurrentSong() {
    return spotifyRequest("me/player/currently-playing");
}
function checkisPlaying() {
   // console.log("Überprüfe Wiedergabestatus...");
    getCurrentSong()
    .then(response => parseJsonSafe(response))
    .then(data => {
        if (data && (data.isPlaying || data.is_playing)) { // Je nach Spotify API Version könnte es isPlaying oder is_playing sein
            isPlaying = true;
            return;
        } else {
            isPlaying = false;
            return; 
        }

    })
    .catch(err => console.error("checkisPlaying failed:", err));

}
function updateCover() {
    getCurrentSong()
        .then(response => parseJsonSafe(response))
        .then(data => {
            if (!data || !data.item) {
                console.log("Keine Musik läuft");
                console.log("Daten:", data);
                return;
            }

            const coverUrl = data.item.album.images[0].url;
            
          //  document.querySelector("#Cover img").src = coverUrl;
            document.getElementsByClassName("vinyl-label")[0].style.transition = "background-image 2s ease";
            document.getElementsByClassName("vinyl-label")[0].style.backgroundImage = `url(${coverUrl})`;
            document.getElementsByClassName("vinyl-label")[0].style.backgroundSize = "cover";
            document.getElementsByClassName("vinyl-label")[0].style.backgroundPosition = "center";

            const title = data.item.name;
            document.getElementById("song-title").textContent = title;
        })
        .catch(err => console.error("updateCover failed:", err));
}
function switch_playPause() {
   document.getElementById("play-pause").textContent = isPlaying ? "Pause" : "Play";
        
}
switch_playPause(); // Initialer Aufruf, um den Button-Text zu setzen
function nextTrack() {
    return spotifyRequest("me/player/next", "POST");
}

function previousTrack() {
    return spotifyRequest("me/player/previous", "POST");
}

function pauseTrack() {
    return spotifyRequest("me/player/pause", "PUT");
}

function playTrack() {
    return spotifyRequest("me/player/play", "PUT");
}
updateCover();