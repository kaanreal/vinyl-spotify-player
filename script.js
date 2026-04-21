document.getElementById("next").addEventListener("click", () => {
    
    nextTrack().then(() => setTimeout(updateCover, 300));
    

});

document.getElementById("previous").addEventListener("click", () => {
    
    
    previousTrack().then(() => setTimeout(updateCover, 300));
    
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
        rotation += delta * 0.01; // Speed
    }

    document.getElementById("vinyl-version").style.transform =
        `rotate(${rotation}deg)`;

    requestAnimationFrame(animateCover);
}
function isplaying() {
    //console.log("Checking isplaying...");
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




