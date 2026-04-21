let touchStartX = 0; // start point on x axis
let touchEndX = 0;  // end point on x axis

const swipeArea = document.body;   // Entire body as swipe area
swipeArea.addEventListener("touchstart", (e) => {   // when touch event = touchstart
    touchStartX = e.changedTouches[0].screenX;      // start point = point where finger touched screen
});

swipeArea.addEventListener("touchend", (e) => {     // when touch event = touchend
    touchEndX = e.changedTouches[0].screenX;        // end point = point where finger is lifted from screen
    handleSwipe();                                  // evaluate swipe    
}); 

function handleSwipe() {
    const distance = touchEndX - touchStartX; // last point - first point 

    // Minimum swipe length (so small movements are ignored)
    if (Math.abs(distance) < 50) pauseTrack(); // if movement is too small, pause the music

    if (distance < 0) { // if distance is negative, the movement was to the left
        console.log("Swipe Left → Next Song");
        previousTrack();   
    } else {
        console.log("Swipe Right → Previous Song"); // if distance is positive, the movement was to the right
        nextTrack(); 
    }
}
