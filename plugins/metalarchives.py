from util import hook, http, timesince
from datetime import datetime
from BeautifulSoup import BeautifulSoup
import re

baseurl = "http://www.metal-archives.com/"
api_url = "http://ws.audioscrobbler.com/2.0/?format=json"

@hook.command('maband', autohelp=False)
@hook.command(autohelp=False)
def maband(inp, conn=None, bot=None,nick=None, chan=None):
    """maband [band] -- Displays band info
     from metal archives."""

    if not inp:
        return "You must specify a band"

    response = http.get_json(baseurl + "search/ajax-advanced/searching/bands",
                             bandName=inp, exactBandMatch=0, sEcho=1, iColumns=3,
                             sColumns='', iDisplayStart=0, iDisplayLength=200, sNames=',,')

    if response["error"] != "":
        return "Error: {}.".format(response["error"])

    if response["iTotalRecords"] == 0:
        return "No bands were found"

    bands = response["aaData"]
    totalBands = response["iTotalRecords"]
    bandCounter = 5
    if totalBands < bandCounter:
        bandCounter = totalBands

    out = ""

    for band in bands[:bandCounter]:
        soup = BeautifulSoup(band[0])
        links = soup.findAll('a')
        bandLink = links[0]["href"]
        bandName = links[0].contents[0]
        bandGenre = band[1]
        bandCountry = band[2]

        conn.send(u"PRIVMSG {} :\x02{}\x0f - {} from {} (More info: {})".format(chan, bandName, bandGenre, bandCountr$

    return u"{} bands containing the name {}".format(len(bands), inp)

@hook.command('mareviews', autohelp=False)
@hook.command(autohelp=False)
def mareviews(inp, conn=None, bot=None,nick=None, chan=None):
    """marating [band] -- Displays band rating
     from metal archives."""

    if not inp:
        return "You must specify a band"

    comms = inp.split(",")

    album = None
    if(len(comms) == 1):
        inp = comms[0].strip()
    else:
        inp = comms[0].strip()
        album = comms[1]

    album = str(album).strip()

    response = http.get_json(baseurl + "search/ajax-advanced/searching/bands",
                             bandName=inp, exactBandMatch=0, sEcho=1, iColumns=3,
                             sColumns='', iDisplayStart=0, iDisplayLength=200, sNames=',,')

    if response["error"] != "":
        return "Error: {}.".format(response["error"])

    if response["iTotalRecords"] == 0:
        return u"No bands were found named {}".format(inp)

    bands = response["aaData"]

    band = BeautifulSoup(bands[0][0]).findAll("a")[0].contents[0]
    href = BeautifulSoup(bands[0][0]).findAll("a")[0]["href"]

    regex1 = re.compile("(?<=bands/).*\/")
    rawBand = regex1.findall(href)[0]

    regex2 = re.compile("(?<={}/).*".format(rawBand.replace("/", "")))
    bandId = regex2.findall(href)[0]

    reviews = http.get_json(baseurl + "review/ajax-list-band/id/{}/json/1".format(bandId),
                             sEcho=1, iColumns=4, sColums='', iDisplayStart=0, iDisplayLength=200,
                             mDataProp_0=0, mDataProp_1=1, mDataProp_2=2, mDataProp_3=3, iSortingCols=1, iSortCol_0=3,
                             sSortDir_0="desc", bSortable_0="true", bSortable_1="true", bSortable_2="true",
                             bSortable_3="true")

    percentages = []
    if not album:
        if type(reviews["aaData"]) == list and len(reviews["aaData"]) > 0:
            for review in reviews["aaData"]:
                percentages.append(int(review[1].replace("%", "")))

            average = reduce(lambda x, y: x + y, percentages) / len(percentages)

            return u'\x02{}\x0f has an average review of \x02{}\x0f% based on their album reviews. Use "," to separat$
        else:
            return u'Could not calculate average review for {} or too many bands with the same name. Use "," to seper$
    else:
        if type(reviews["aaData"]) == list  and len(reviews["aaData"]) > 0:
            fullAlbum = ""
            if reviews["aaData"] == list:
                for review in reviews["aaData"]:
                    ulink = review[0]
                    alink = BeautifulSoup(ulink).findAll("a")
                    text = alink[0].contents[0].lower()
                    if text == album.lower() or text.find(album) != -1:
                        percentages.append(int(review[1].replace("%", "")))
                        fullAlbum = alink[0].contents[0]

                if len(percentages) > 0:
                    average = reduce(lambda x, y: x + y, percentages) / len(percentages)

                    return u'The album \x02{}\x0f by \x02{}\x0f has an average review of \x02{}\x0f%'.format(fullAlbu$
                else:
                    return u'Could not find the album {} for the band {}'.format(album, band)
            else:
                return u'Could not find reviews for album like "{}" by {}.'.format(album, band)
        else:
            return u'Could not calculate average review for {} or too many bands with the same name'.format(band)




