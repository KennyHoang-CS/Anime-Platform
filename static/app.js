const BASE_URL = "http://localhost:5000/api";

let videoURL = document.getElementById('videoURL')

videoIDs = []
introVideoIDs = ["Q8bmv-14OVI", "P_YtFPg9tNE", "68UROyvw-Ac", "LFVKmVTAHpk", "Lk3fJsIOnKw&t=108s"]


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


window.onYouTubeIframeAPIReady = function() {
    player = new YT.Player('player', {
    height: '450',
    width: '100%',
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
    console.log('get random vid () called')
    let i = videoIDs.length, k, temp;
    while(--i > 0){
        k = Math.floor(Math.random() * (i + 1));
        temp = videoIDs[k];
        videoIDs[k] = videoIDs[i];
        videoIDs[i] = temp;
    }
    return videoIDs[0]
}

getVideoIDs();