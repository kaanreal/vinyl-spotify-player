
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
        if(data.isPlaying  || data.is_playing) {
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
                console.log("No music playing");
                return;
            }

            const coverUrl = data.item.album.images[0].url;
            const screen = document.getElementById("round-screen");

            const currentBg = screen.style.backgroundImage.replaceAll('"', "");

            // If the cover is already the same → do nothing
            if (currentBg.includes(coverUrl)) return;

            // Start fade-out
            screen.classList.remove("FadeIn");
            screen.classList.add("FadeOut");

            // After fade-out is done, change the image and fade in
            setTimeout(() => {

                // Swap image
                screen.style.backgroundImage = `url("${coverUrl}")`;

                // Switch to fade-in
                screen.classList.remove("FadeOut");
                screen.classList.add("FadeIn");

                // Update title
                document.getElementById("song-title").textContent = data.item.name;

            }, 500); // same as fadeOut duration
        })
        .catch(err => console.error(err));
}

function updateMotor() {

    if (isPlaying) {
        fetch("http://localhost:5000/motor/start");
        
    } else {
        fetch("http://localhost:5000/motor/stop");
    }   
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