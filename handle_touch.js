let touchStartX = 0; // start point auf x achse
let touchEndX = 0;  // end point auf x achse

const swipeArea = document.body;   // Ganzer Body als Swipe-Bereich
swipeArea.addEventListener("touchstart", (e) => {   // wenn touch Event = touchstart
    touchStartX = e.changedTouches[0].screenX;      // start point = pungt wo finder screen berührt hat
});

swipeArea.addEventListener("touchend", (e) => {     // wenn touch Event = touchend
    touchEndX = e.changedTouches[0].screenX;        // end point = punkt wo finger von screen weggenommen wird
    handleSwipe();                                  // swipe auswerten    
}); 

function handleSwipe() {
    const distance = touchEndX - touchStartX; // letzter punk - erster punkt 

    // Mindest-Swipe-Länge (damit kleine Bewegungen ignoriert werden)
    if (Math.abs(distance) < 50) return;

    if (distance < 0) { // wenn distance negativ ist, dann war die Bewegung nach links
        console.log("Swipe Left → Next Song");
        previousTrack();   
    } else {
        console.log("Swipe Right → Previous Song"); // wenn distance positiv ist, dann war die Bewegung nach rechts
        nextTrack(); 
    }
}
