import requests
import random

BASE_PATH = "https://kitsu.io/api/edge"     # Base path for external API. 
videoIDs = []     # To hold our list of trending animes youtube embed codes. 

# Process our response for home page ('index.html') or searching on ('search.html').
def processResponse(response, flag, animeIDs):
    """ Add our external API data into a list for animes. 

        response: contains our external API data.
        
        flag: how to process the external API data if its to display 
            trending animes or searching. This is needed because len(response('data'))
            would give us the desired length for trending animes query 
            while making a search query length is always 1 (even though there are more than 1).
        
        animeIDs: To contain the external API youtube embed IDs. 
    
    """
    
    myList = []     # To store our anime data: id, title, deesc, age rating, genre. 
    
    # As of now, it limited to 20 entries until optimization update. 
    if flag == 'trending': 
        for i in range(0, 20):
            myList.append((
            response['data'][i]['id'],
            response['data'][i]['attributes']['canonicalTitle'],
            response['data'][i]['attributes']['synopsis'],
            response['data'][i]['attributes']['coverImage']['original'],
            response['data'][i]['attributes']['averageRating'],
            response['data'][i]['attributes']['ageRatingGuide'],
            isUserWatching(int(response['data'][i]['id']), animeIDs),
            videoIDs.append(response['data'][i]['attributes']['youtubeVideoId'])
            ))
    else: 
        for i in range(0, len(response['data'])):

            # Check if the source has a valid image.  
            try:
                image = response['data'][i]['attributes']['coverImage']['original']
            except TypeError:
                image = response['data'][i]['attributes']['posterImage']['original']
            
            myList.append((
            response['data'][i]['id'],
            response['data'][i]['attributes']['canonicalTitle'],
            response['data'][i]['attributes']['synopsis'],
            image,
            response['data'][i]['attributes']['averageRating'],
            response['data'][i]['attributes']['ageRatingGuide']
            ))
    
    # myList will now contain all our anime data.
    return myList
        

# Validates if an anime is in an user's watch list. 
def isUserWatching(anime, animes):
    """ Determine if the user is watching or not watching the anime. """
    return 'user_is_watching' if anime in animes else 'user_not_watching'


def getAnimeData(user_list):
    """ Get the anime data from external API for each anime in user's list. """
    
    # Convert the sqlalchemy object into a list. 
    user_list = list(user_list)
    myList = []

    # Process the user's list, get data for each anime. 
    for i in range(0, len(user_list)):
        
        # Get the data from external API. 
        response = requests.get(f'{BASE_PATH}/anime/{user_list[i].anime_id}')
        response = response.json()
        
        # Check the image source, results will break if coverImage is empty. 
        try:
            image = response['data']['attributes']['coverImage']['original']
        except TypeError:
            image = response['data']['attributes']['posterImage']['original']

        myList.append((
            response['data']['id'],
            response['data']['attributes']['canonicalTitle'],
            response['data']['attributes']['synopsis'],
            image,
            response['data']['attributes']['averageRating'],
            response['data']['attributes']['ageRatingGuide']
            ))
    
    # myList will now contain anime data for each entry in user's list. 
    return myList

def randomIntroVideo(videoIDs):
    """ Returns a random youtube embed ID in our list. """
    
    video = videoIDs[random.randint(0,20)]
    
    # This is for Heroku APP Deployment, owners blocks them on Heroku Site. 
    if video == 'EHzBhrncmac':
        video = 'DpEfsDmMyF4'
    elif video == 'LHtdKWJdif4':
        video = 'MGRm4IzK1SQ'
    elif video == 'MDrjS3ePLso':
        video = 'FY17vwF0Bqc'
    elif video == 'tMblzsXwAKo':
        video = '2JAElThbKrI'
    elif video == '5kh7ClVck4Y':
        video = 'k4iTICgLOtw'

    return video

