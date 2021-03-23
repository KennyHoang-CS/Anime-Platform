const BASE_URL = "http://localhost:5000/api";

// Get reference to our button that holds our initial video embed code. 
let videoURL = document.getElementById('videoURL')

// To hold our list of youtube embed codes for our Youtube Iframe API to use. 
let videoIDs = []

// Get our list of youtube embed codes from our python flask back-end. 
async function getVideoIDs(){
    let response = await axios.get(`${BASE_URL}/trailers`);
    // Temporary fix until optimization update, 
    // the data gets duplicated and expands the list every time home page is accessed.
    response = new Set(response.data)   
    response = Array.from(response)
    videoIDs = response
}

/************************************************** 
 * YOUTUBE IFRAME API 
 */ 

// This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

//  This function creates an <iframe> (and YouTube player)
//   after the API code downloads.
var player;

window.onYouTubeIframeAPIReady = function() {
    player = new YT.Player('player', {
    height: '450',
    width: '100%',
    // get our initial video embed code that is placed into our index.html document from our flask python back-end.
    videoId: videoURL.value, 
    events: {
    'onReady': onPlayerReady,
    'onStateChange': onPlayerStateChange
    }});
}

// The API will call this function when the video player is ready.
function onPlayerReady(event) {
    event.target.playVideo();
}

//  The API calls this function when the player's state changes.
//    The function indicates that when video stop playing (state=0),
function onPlayerStateChange(event) {
    
    status = player.getPlayerState() 

    // Our video reached the end, now play a random video from our 
    if (player.getPlayerState() === 0){
        player.cueVideoById(getRandomVideoID())
        player.playVideo()
    } else {
        console.log('getPlayerState() called', status)
    }



}

// To stop the video. 
function stopVideo() {
    player.stopVideo();
}

// Fisher-Yates Shuffle Algorithm. 
function getRandomVideoID(){
    // Shuffle our videoIDs (array of youtube embed IDs). 
    let i = videoIDs.length, k, temp;
    while(--i > 0){
        k = Math.floor(Math.random() * (i + 1));
        temp = videoIDs[k];
        videoIDs[k] = videoIDs[i];
        videoIDs[i] = temp;
    }
    return videoIDs[0]  // Return the first element, after videoIDs is shuffled. 
}

// Make a call to our flask-python backend to get our youtube embed IDs data. 
getVideoIDs();