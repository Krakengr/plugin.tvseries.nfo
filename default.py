import os
import re
import json
import six
import urllib
import sys
import time
import importlib
from urllib.parse import urlparse
from kodi_six import xbmc, xbmcvfs, xbmcaddon, xbmcplugin, xbmcgui
from six.moves import urllib_request, urllib_parse, http_cookiejar
from resources.search import *
from resources.functions import *
import urllib.parse
import logging

search_results = None
global addon_handle
addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()

xbmcplugin.setContent(addon_handle, 'movies')
addon = xbmcaddon.Addon()
viewtype = int(addon.getSetting('viewtype'))
view_modes = [50, 51, 500, 501, 502]
view_mode = view_modes[viewtype]
xbmc.executebuiltin('Container.SetViewMode({})'.format(view_mode))

def menulist():
    try:
        with open(homemenu, 'r') as mainmenu:
            content = mainmenu.read()
            match = re.findall('#.+,(.+?)\n(.+?)\n', content)
            return match
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print("An unknown error occurred: ", e)

def main():
    add_dir('Categories', 'categories', 1, logos + 'icon.png', fanart)
    add_dir('Networks', 'networks', 5, logos + 'icon.png', fanart)

def display_categories():
    xbmc.log('start categories', xbmc.LOGINFO)
    response = urlopen("https://streamdb.homebrewgr.info/index.php?action=tv-categories") 
    data_json = json.loads(response.read())
    
    for _cat in data_json['data']:
        id      = _cat["id"]
        name    = _cat["name"]
        sef     = _cat["sef"]
        url     = sef + '_' + str(id) + '_1'
        add_dir(name.capitalize(), url, 2, logos + f'{name}.png', fanart)

def display_networks():
    xbmc.log('start networks', xbmc.LOGINFO)
    response = urlopen("https://streamdb.homebrewgr.info/index.php?action=tv-networks") 
    data_json = json.loads(response.read())
    
    for _net in data_json['data']:
        id      = _net["id"]
        name    = _net["name"] + ' (' + str(_net["items"]) + ')'
        sef     = _net["sef"]
        logo    = _net["logo"]
        url     = sef + '_' + str(id) + '_1'
        add_dir(name.capitalize(), url, 6, logo, fanart)

def display_network(url):
    addon_handle = int(sys.argv[1])
    add_home_button()
    tmp     = url.split("_")
    sef     = tmp[0]
    id      = tmp[1]
    page    = tmp[2]
    get     = "https://streamdb.homebrewgr.info/index.php?action=get-tv-shows&network=" + id + "&page=" + page
    xbmc.log('start getting data with url: ' + get, xbmc.LOGINFO)

    response = urlopen(get) 
    data_json = json.loads(response.read())

    if data_json["status"] != "OK":
        xbmc.log('Error getting data from: ' + get, xbmc.LOGINFO)
        return
    
    total_pages = int(data_json["total_pages"])
    curr_page   = int(data_json["page"])
    next_page   = curr_page + 1
    next_url    = sef + '_' + str(id) + '_' + str(next_page)

    for _item in data_json['data']:
        name    = data_json['data'][_item]["title"]
        desc    = data_json['data'][_item]["description"]
        imdb_id = data_json['data'][_item]["imdb_id"]
        poster  = data_json['data'][_item]["poster_path"]
        id      = data_json['data'][_item]["themoviedb_id"]
        url     = imdb_id + '_' + str(id)

        add_dir(name.capitalize(), url, 3, poster, fanart)

    if total_pages > 1 and curr_page < total_pages:
        add_dir('[COLOR blue]Next  Page  >>>>[/COLOR]', next_url, 2, logos + 'icon_nav.png', fanart)

    xbmcplugin.setContent(addon_handle, 'movies')
    addon = xbmcaddon.Addon()
    viewtype = int(addon.getSetting('viewtype'))
    view_modes = [50, 51, 500, 501, 502]
    view_mode = view_modes[viewtype]
    xbmc.executebuiltin('Container.SetViewMode({})'.format(view_mode))

def start(url):
    addon_handle = int(sys.argv[1])
    add_home_button()
    tmp     = url.split("_")
    sef     = tmp[0]
    id      = tmp[1]
    page    = tmp[2]
    get     = "https://streamdb.homebrewgr.info/index.php?action=get-tv-shows&cat=" + id + "&page=" + page
    xbmc.log('start getting data with url: ' + get, xbmc.LOGINFO)

    response = urlopen(get) 
    data_json = json.loads(response.read())

    if data_json["status"] != "OK":
        xbmc.log('Error getting data from: ' + get, xbmc.LOGINFO)
        return
    
    total_pages = int(data_json["total_pages"])
    curr_page   = int(data_json["page"])
    next_page   = curr_page + 1
    next_url    = sef + '_' + str(id) + '_' + str(next_page)

    for _item in data_json['data']:
        name    = data_json['data'][_item]["title"]
        desc    = data_json['data'][_item]["description"]
        imdb_id = data_json['data'][_item]["imdb_id"]
        poster  = data_json['data'][_item]["poster_path"]
        id      = data_json['data'][_item]["themoviedb_id"]
        url     = imdb_id + '_' + str(id)

        add_dir(name.capitalize(), url, 3, poster, fanart)

    if total_pages > 1 and curr_page < total_pages:
        add_dir('[COLOR blue]Next  Page  >>>>[/COLOR]', next_url, 2, logos + 'icon_nav.png', fanart)

    xbmcplugin.setContent(addon_handle, 'movies')
    addon = xbmcaddon.Addon()
    viewtype = int(addon.getSetting('viewtype'))
    view_modes = [50, 51, 500, 501, 502]
    view_mode = view_modes[viewtype]
    xbmc.executebuiltin('Container.SetViewMode({})'.format(view_mode))

def add_home_button():
    add_dir("Home", "", 100, os.path.join(logos, 'icon.png'), fanart)

def get_params():
    param = {}
    try:
        paramstring = sys.argv[2]
        if len(paramstring) >= 2:
            params = sys.argv[2]
            cleanedparams = params.replace('?', '')
            if (params[len(params) - 1] == '/'):
                params = params[0:len(params) - 2]
            pairsofparams = cleanedparams.split('&')
            param = {}
            for pair in pairsofparams:
                if '=' in pair:
                    key, value = pair.split('=')
                    param[key] = value
    except:
        pass
    return param

def media_list(url):
    now         = int( time.time() )
    tmp         = url.split("_")
    imdb        = tmp[0]
    id          = int(tmp[1])
    filename    = imdb + '.json'

    if file_exists(filename) or file_time(name):
        xbmc.log('file found and data loaded from: ' + filename, xbmc.LOGINFO)
        data_json = open_cache(filename)
    else:
        xbmc.log('file not found: ' + filename, xbmc.LOGINFO)
        get =   'https://coverapi.store/embed/' + imdb +'/'
        d = make_request(get)
        z = re.search(r"news_id:.+'(.*?)'", d)
        
        if (z is None):
            xbmc.log('news_id not found for: ' + get, xbmc.LOGINFO)
            dialog = xbmcgui.Dialog()
            dialog.ok('Error', 'Error getting playlist info. Please try again later.')
            return
        
        news_id = z.group(1)
        play_url = 'https://coverapi.store/uploads/playlists/' + str(news_id) + '.txt?v=' + str(now)
        list     = urlopen(play_url)
        data_json = json.loads(list.read())
        write_cache(filename, data_json)

    if data_json['playlist'] == "" :
        dialog = xbmcgui.Dialog()
        dialog.ok('Error', 'Error getting playlist info. Please try again later.')
        #dialog.notification('TV Series NFO', 'Error getting playlist info', xbmcgui.NOTIFICATION_INFO, 5000)
        return

    for _item in data_json['playlist']:
        
        #No seasons?
        if 'playlist' not in _item.keys():
            episode_name    = _item['comment']
            episode_url     = _item['file']
            add_dir(episode_name, episode_url, 4, '', fanart, False)
        
        else:
            season = _item['comment']
            for _index in _item['playlist']:
                episode_name    = _index['comment'] + ' (' + season + ')'
                episode_url     = _index['file']
                #xbmc.log('base_url: ' + episode_url, xbmc.LOGINFO)
                add_dir(episode_name, episode_url, 4, '', fanart, False)

def play_video(url):
    #media_url = url.replace('www.', '')
    media_url = url.replace('https://', 'http://')
    add_play_data(media_url)
    xbmc.Player().play(item=media_url)
    xbmc.log('media_url: ' + media_url, xbmc.LOGINFO)

if __name__ == '__main__':
    params = get_params()
    url = params.get("url") and urllib_parse.unquote_plus(params["url"])
    name = params.get("name") and urllib_parse.unquote_plus(params["name"])
    mode = params.get("mode") and int(params["mode"])
    iconimage = params.get("iconimage") and urllib_parse.unquote_plus(params["iconimage"])

    if name is not None:
        xbmc.log('name ΙΝ main: ' + name, xbmc.LOGINFO)

    if mode is None or url is None or len(url) < 1:
        main()
    elif mode == 1:
        display_categories()
    elif mode == 2:
        start(url)
    elif mode == 3:
        media_list(url)
    elif mode == 4:
        play_video(url)
    elif mode == 5:
        display_networks()
    elif mode == 6:
        display_network(url)
        
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
