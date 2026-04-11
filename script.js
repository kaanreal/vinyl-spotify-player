document.getElementById("next").addEventListener("click", () => {
     document.getElementsByClassName("vinyl-label")[0].style.transition = "background-image 0.2s ease";
    nextTrack().then(() => setTimeout(updateCover, 300));
    setTimeout(() => rotation = 0, 300); // Reset Rotation

});

document.getElementById("previous").addEventListener("click", () => {
     document.getElementsByClassName("vinyl-label")[0].style.transition = "background-image 0.2s ease";
    previousTrack().then(() => setTimeout(updateCover, 300));
    setTimeout(() => rotation = 0, 300); // Reset Rotation
});

let isPlaying = false;
let rotation = 0;
let lastTime = null;
let rotating = false;


function animateCover(timestamp) {
    if (!lastTime) lastTime = timestamp;

    const delta = timestamp - lastTime;
    lastTime = timestamp;
    

    if (rotating) {
        rotation += delta * 0.01; // Geschwindigkeit
    }

    document.getElementById("vinyl-version").style.transform =
        `rotate(${rotation}deg)`;

    requestAnimationFrame(animateCover);
}
function isplaying() {
    //console.log("Überprüfe isplaying...");
    if  (isPlaying) {
        rotating = true; // START
    }else {
        rotating = false; // STOP
    }
}

requestAnimationFrame(animateCover);

document.getElementById("play-pause").addEventListener("click", () => {
    if (isPlaying) {
       
        pauseTrack().then(() => {
            isPlaying = false;
            rotating = false; // STOP
            updateCover();
            switch_playPause();
        });
    } else {
        
        playTrack().then(() => {
            isPlaying = true;
            rotating = true; // START
            updateCover();
            switch_playPause();
        });
    }
});




