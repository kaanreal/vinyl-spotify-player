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
function getCurrentSong() {
    return spotifyRequest("me/player/currently-playing");
}
function checkisPlaying() {
   // console.log("Überprüfe Wiedergabestatus...");
    getCurrentSong()
    .then(response => response.json())  
    .then(data => {
        if(data.isPlaying  || data.is_playing) { // Je nach Spotify API Version könnte es isPlaying oder is_playing sein
            isPlaying = true;
            return;
        } else {
            isPlaying = false;
            return; 
        }

    })

}
function updateCover() {
    getCurrentSong()
        .then(response => response.json())
        .then(data => {
            if (!data || !data.item) {
                console.log("Keine Musik läuft");
                console.log("Daten:", data);
                return;
            }

            const coverUrl = data.item.album.images[0].url;
            
          //  document.querySelector("#Cover img").src = coverUrl;
            document.getElementById("round-screen").style.backgroundImage = `url(${coverUrl})`;
            document.getElementById("round-screen").style.backgroundSize = "cover";
            document.getElementById("round-screen").style.backgroundPosition = "center";

            const title = data.item.name;
            document.getElementById("song-title").textContent = title;
        })
        .catch(err => console.error(err));
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