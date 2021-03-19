const BASE_URL = "http://localhost:5000/api";

videoIDs = []

async function getVideoIDs(){
    let response = await axios.get(`${BASE_URL}/data`);
    response = new Set(response.data)
    response = Array.from(response)
    console.log(response)
    videoIDs = response;
}

// This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

//  This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player;

    
function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
    height: '450',
    width: '100%',
    videoId: getRandomVideoID() || "Q8bmv-14OVI",
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
//    The function indicates that when playing a video (state=1),
//    the player should play for six seconds and then stop.
var done = false;
function onPlayerStateChange(event) {
    
    if (player.getPlayerState() === 0){
        player.cueVideoById(getRandomVideoID())
        player.playVideo()
    }

}

function stopVideo() {
    player.stopVideo();
}


function getRandomVideoID(){
    
    let why = Math.floor(Math.random() * 16)
    console.log("random number is " + why)
    console.log("youtube emded is " + videoIDs[why])
    return videoIDs[why]
}

getVideoIDs();