from bs4 import BeautifulSoup
from requests_html import HTMLSession 
from operator import itemgetter



def extractHeatmapCurve(url: str, renderTime: int = 4, retries: int = 0, maxRetries: int = 2)->str:
    """
    Given a Youtube URL, returns a string of letters and numbers representing
    a series of bezier curves mapping the heatmap.
    url: the YouTube URL to extract the heatmap from.
    renderTime: the time in seconds for the program to wait for requests_html to render the HTML file.
                A LOWER VALUE MAY RESULT IN THE FUNCTION NOT WORKING!
    retries: the number of retries this function has taken
                INTERNAL VARIABLE; MODIFY AT YOUR OWN RISK
    maxRetries: the maximium number of tries this function will take in trying to get the heatmap.
                INTERNAL VARIABLE; MODIFY AT YOUR OWN RISK
    Throws an exception if the function is unable to find the heatmap after a given number of retries.
    """
    session = HTMLSession()
    response = session.get(url)
    response.html.render(sleep = renderTime) #needs time to render
    soup = BeautifulSoup(response.html.html, "html.parser")
    heatmapElement = soup.find(class_ = "ytp-heat-map-path")
    if heatmapElement == None:
        if retries > maxRetries:
            raise Exception("request_html could not render HTML file or heatmap does not exist. " +
                            "Try incrementing renderTime or double checking if a heatmap does exist for the given url.")
        else:
            print("Unable to get heatmap from the HTML file. Retrying with increased renderTime.")
            return extractHeatmapCurve(url, renderTime + 2, retries + 1)
    return heatmapElement['d']
    
def convertHeatmapCurve(heatmap: str)->list:
    """
    given a heatmap extracted from extractHeatmapCurve, converts the curve 
    into a time-based set of datapoints.
    heatmap: a string of numbers and letters from extractHeatmapCurve
    return: a list of tuples, where the first value of the tuple is time 
            of the datapoint as a fraction of the whole video (from 0 to 1)
    """
    datapointsStr = heatmap.split(' ')
    datapointsStr = datapointsStr[5:] #Shifts list
    #gets every fourth element. The first through 3rd elements are for modelling the bezier curve
    datapointsStr = datapointsStr[::4] 
    datapointsStr.pop() #pop last two elements (2 points at 99.5%) so that we get 100 datapoints evenly spaced.
    datapointsStr.pop() 
    datapoints = []
    for datapoint in datapointsStr:
        x,y = datapoint.split(',')
        #convert strings to a floats and normalize values to between 0 and 1
        #x, y = float(x), float(y)
        x = round((float(x) - 5)/1000, 3)
        y = round((100 - float(y))/100, 3)
        datapoints.append((x, y))
    return datapoints

def getHeatmapPoints(url: str) -> list:
    """
    Given a YouTube URL with a heatmap, return a list of tuples with viewership datapoints.
    See extractHeatmapCurve and convertHeatmapCurve for further details.
    """
    return convertHeatmapCurve(extractHeatmapCurve(url))
