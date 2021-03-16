

def processResponse(response, flag):
    """ sadsa """
    
    myList = []

    if flag == 'trending': 
        for i in range(0, 16):
            myList.append((response['data'][i]['attributes']['canonicalTitle'],
            response['data'][i]['attributes']['synopsis'],
            response['data'][i]['attributes']['coverImage']['original'],
            response['data'][i]['attributes']['averageRating'],
            response['data'][i]['attributes']['ageRatingGuide']
            ))
    else: 
        for i in range(0, len(response)):
            myList.append((
            response['data'][i]['id'],
            response['data'][i]['attributes']['canonicalTitle'],
            response['data'][i]['attributes']['synopsis'],
            response['data'][i]['attributes']['coverImage']['original'],
            response['data'][i]['attributes']['averageRating'],
            response['data'][i]['attributes']['ageRatingGuide']
            ))

    return myList
        
    