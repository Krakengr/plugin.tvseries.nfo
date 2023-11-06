import os
from os.path import exists
import json
import six
import time
import sys
import hashlib
from kodi_six import xbmc, xbmcvfs, xbmcaddon, xbmcplugin, xbmcgui
from six.moves import urllib_request, urllib_parse, http_cookiejar
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from resources.functions import *
import xbmcaddon
import cloudscraper2

from default import addon_handle
addon = xbmcaddon.Addon()

addon = xbmcaddon.Addon(id='plugin.tvseries.nfo')
home = addon.getAddonInfo('path')
if home[-1] == ';':
    home = home[0:-1]
cacheDir = os.path.join(home, 'cache')
cookiePath = os.path.join(home, 'cookies.lwp')
fanart = os.path.join(home, 'resources/logos/fanart.jpg')
icon = os.path.join(home, 'resources/logos/icon.png')
logos = os.path.join(home, 'resources/logos\\')  # subfolder for logos
homemenu = os.path.join(home, 'resources', 'playlists')
urlopen = urllib_request.urlopen
cookiejar = http_cookiejar.LWPCookieJar()
cookie_handler = urllib_request.HTTPCookieProcessor(cookiejar)
urllib_request.build_opener(cookie_handler)


# Setting the log level constants
# INFO is used for Python 3 and NOTICE for Python 2
LOG_LEVEL = xbmc.LOGINFO

# Setzen der Standard-Opener und Cookie-Jar
COOKIE_JAR = http_cookiejar.LWPCookieJar()
COOKIE_HANDLER = urllib_request.HTTPCookieProcessor(COOKIE_JAR)
urllib_request.install_opener(urllib_request.build_opener(COOKIE_HANDLER))

# Maximale Anzahl von Versuchen, um eine fehlgeschlagene Anfrage zu wiederholen
MAX_RETRY_ATTEMPTS = int(addon.getSetting('max_retry_attempts'))

def search_views(imdb):
    # Get the path to the add-on directory
    home = xbmcaddon.Addon().getAddonInfo('path')
    # Use the os.path.join function to construct the file path
    file_path = os.path.join(home, 'resources/last_query.json')
    f = open(file_path)
    views = json.load(f)

    if views[0] == "":
        return False
    
    data = []
    
    for j in views[0]['data']:
        for jj in j:
            im = j[jj]
            time = j[jj]
            play = j[jj]

            if im == imdb:
                data.append({"time":time, "playlist":play})
                break
    
    return data

def add_play_data(url):
    md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
    write_json('last_content.json', md5 )

def file_exists(name):
    home = xbmcaddon.Addon().getAddonInfo('path')
    file_path = os.path.join(home, 'resources/cache/' + name)

    if exists(file_path):
        xbmc.log('file found: ' + file_path, xbmc.LOGINFO)
        return True
    else:
        xbmc.log('file not found: ' + file_path, xbmc.LOGINFO)
        return False

def file_time(name):
    home = xbmcaddon.Addon().getAddonInfo('path')
    file_path = os.path.join(home, 'resources/cache/' + name)

    if not os.path.exists(file_path):
        return False
    
    now = int( time.time() )
    xbmc.log('now: ' + now, xbmc.LOGINFO)
    #21600 = 6hrs; default 3600 = 1 hour
    if os.path.getmtime(file_path) > (now - 21600):
        return True
    else:
        return False

def open_cache(name):
    home = xbmcaddon.Addon().getAddonInfo('path')
    file_path = os.path.join(home, 'resources/cache/' + name)

    if not os.path.exists(file_path):
        xbmc.log('Cache file not found: ' + file_path, xbmc.LOGINFO)
        return False
    
    return json.load(open(file_path))

def write_cache(name, data):
    home = xbmcaddon.Addon().getAddonInfo('path')
    file_path = os.path.join(home, 'resources/cache/' + name)

    if os.path.exists(file_path):
        os.remove(file_path)
    
    with open(file_path, 'w') as f:
        json.dump(data, f)

def open_json(name):
    home = xbmcaddon.Addon().getAddonInfo('path')
    file_path = os.path.join(home, 'resources/' + name)

    if not os.path.exists(file_path):
        xbmc.log('Json file not found: ' + file_path, xbmc.LOGINFO)
        return False

    return json.load(open(file_path))

def write_json(name, id, data = []):
     # Get the path to the add-on directory
    home = xbmcaddon.Addon().getAddonInfo('path')
    # Use the os.path.join function to construct the file path
    file_path = os.path.join(home, 'resources/' + name)

    now = int( time.time() )

    all_queries = []
    
    with open(file_path, 'r') as f:
        try:
            all_queries = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    if not isinstance(all_queries, list):
        all_queries = []

    # Check if query already exists in list
    if id not in all_queries:
        # Add the new query to the list
        all_queries.append(id)

        # Write all queries to the file
        with open(file_path, 'w') as f:
            json.dump(all_queries, f)

def add_dir(name, url, mode, iconimage, fanart, isAFolder = True):
    u = sys.argv[0] + '?url=' + urllib_parse.quote_plus(url) + '&mode=' + str(mode) +\
        '&name=' + urllib_parse.quote_plus(name) + '&iconimage=' + str(iconimage)
    #xbmc.log("Adding directory: Name: {}, URL: {}, Mode: {}, Icon: {}, Fanart: {}".format(name, url, mode, iconimage, fanart), level=xbmc.LOGINFO)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({ 'thumb': iconimage, 'icon': icon, 'fanart': fanart})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,
                                    listitem=liz, isFolder=isAFolder)
    return ok

def add_sub_dir(parent_name, name, url, mode, iconimage, fanart, description=''):
    u = (url + "?url=" + urllib_parse.quote_plus(url) +
         "&mode=" + str(mode) + "&name=" + urllib_parse.quote_plus(parent_name + '/' + name) +
         "&iconimage=" + urllib_parse.quote_plus(iconimage) +
         "&description=" + urllib_parse.quote_plus(description))
    liz = xbmcgui.ListItem(name)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    liz.setArt({'thumb': iconimage, 'icon': iconimage, 'fanart': fanart})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz, isFolder=True)



def add_link(name, url, mode, iconimage, fanart):
    quoted_url = urllib_parse.quote(url)
    u = sys.argv[0] + '?url=' + quoted_url + '&mode=' + str(mode) \
        + '&name=' + str(name) + "&iconimage=" + str(iconimage)
    xbmc.log("Adding link to directory: Name: {}, URL: {}, Mode: {}, Icon: {}, Fanart: {}".format(name, url, mode, iconimage, fanart), level=xbmc.LOGINFO)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({'thumb': iconimage, 'icon': icon, 'fanart': iconimage})
    liz.getVideoInfoTag().setTitle(name)
    try:
        liz.setContentLookup(False)
    except:
        pass
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,
                                    listitem=liz, isFolder=False)

def resolve_url(url, websites):
    xbmc.log("Input URL for resolve_url: {}".format(url), level=xbmc.LOGDEBUG)
    for website in websites:
        xbmc.log("Checking website URL: {}".format(website["url"]), level=xbmc.LOGDEBUG)
        if website["url"] in url:
            xbmc.log("Matching website found: {}".format(website["name"]), level=xbmc.LOGDEBUG)
            media_url = website['play_function'](url)
            break
        else:
            xbmc.log("No match found: website URL not in input URL", level=xbmc.LOGDEBUG)
    else:
        media_url = url
    return media_url



                                    
def make_request(url, max_retry_attempts=3, retry_wait_time=5000, mobile=False, method='GET'):
    scraper = cloudscraper2.create_scraper()
    return scraper.get(url).text

def get_search_query():
    keyb = xbmc.Keyboard('', '[COLOR yellow]Enter search text[/COLOR]')
    keyb.doModal()
    if keyb.isConfirmed():
        return urllib_parse.quote_plus(keyb.getText())
    return None


    xbmcplugin.endOfDirectory(int(sys.argv[1]))
