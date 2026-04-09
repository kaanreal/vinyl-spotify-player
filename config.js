const SPOTIFY_CLIENT_ID = "8fb5fd75086e41e7b90deeef062e055b";
const SPOTIFY_REDIRECT_URI = "http://127.0.0.1:3000/callback"; 
async function getAccessToken() {
    const response = await fetch("access_token.txt");
    return response.text();
}