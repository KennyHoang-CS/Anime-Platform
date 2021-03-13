

def processResponse(response):
    """ sadsa """
    
    myList = []

    for i in range(0, 12):
        #print(response['data'][i]['attributes']['slug'])
        
        myList.append((response['data'][i]['attributes']['canonicalTitle'],
        response['data'][i]['attributes']['synopsis'],
        response['data'][i]['attributes']['coverImage']['original']))

    return myList
        
    