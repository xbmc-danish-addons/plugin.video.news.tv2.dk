import os
import sys
import cgi as urlparse
import urllib2
import re

import xbmcgui
import xbmcaddon
import xbmcplugin

VIDEO_LIST_URL = 'http://news.tv2.dk/js/video-list.js.php/'
PLAYLIST_URL = 'http://common-dyn.tv2.dk/flashplayer/playlist.xml.php/alias-player_news/autoplay-1/clipid-%s/keys-NEWS,PLAYER.xml'

class TV2NewsAddon(object):
    def listCategories(self):
        data = self._loadJson()
        m = re.match('.*sections: \[(.*?)\]', data, re.DOTALL)
        for idx, m in enumerate(re.finditer('title: "([^"]+)"', m.group(1))):
            title = m.group(1)

            item = xbmcgui.ListItem(title, iconImage = ICON)
            item.setProperty('Fanart_Image', FANART)
            url = PATH + '?idx=' + str(idx)
            xbmcplugin.addDirectoryItem(HANDLE, url, item, isFolder = True)

        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(HANDLE)

    def listCategory(self, idx):
        data = self._loadJson()

        clips = list()
        for m in re.finditer('sources: \[(.*?)\] \}', data, re.DOTALL):
            clips.append(m.group(1))

        for m in re.finditer('id: ([0-9]+),\s+title:"(.*?)",\s+image:"([^"]+)",\s+description: "(.*?)",\s+.*?date: "([^"]+)"', clips[idx], re.DOTALL):
            print m
            id = m.group(1)
            title = m.group(2).replace("\\'", "'").replace('\\"', '"')
            image = m.group(3)
            description = m.group(4)
            date = m.group(5)

            item = xbmcgui.ListItem(title, iconImage = image)
            item.setInfo('video', {
                'title' : title,
                'plot' : description,
                'date' : date[6:].replace('-', '.')
            })
            item.setProperty('IsPlayable', 'true')
            item.setProperty('Fanart_Image', FANART)
            url = PATH + '?clip=' + str(id)
            xbmcplugin.addDirectoryItem(HANDLE, url, item)

        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.endOfDirectory(HANDLE)

    def playClip(self, clipId):
        u = urllib2.urlopen(PLAYLIST_URL % clipId)
        playlist = u.read()
        u.close()

        m = re.match('.*video="([^"]+)"', playlist, re.DOTALL)
        if m:
            print m.group(1)
            item = xbmcgui.ListItem(path = m.group(1))
            xbmcplugin.setResolvedUrl(HANDLE, True, item)

    def _loadJson(self):
        u = urllib2.urlopen(VIDEO_LIST_URL)
        data = u.read()
        u.close()

        return data.decode('iso-8859-1')


if __name__ == '__main__':
    ADDON = xbmcaddon.Addon(id = 'plugin.video.news.tv2.dk')
    PATH = sys.argv[0]
    HANDLE = int(sys.argv[1])
    PARAMS = urlparse.parse_qs(sys.argv[2][1:])

    FANART = os.path.join(ADDON.getAddonInfo('path'), 'fanart.jpg')
    ICON = os.path.join(ADDON.getAddonInfo('path'), 'icon.png')

    tv2News = TV2NewsAddon()
    if PARAMS.has_key('idx'):
        tv2News.listCategory(int(PARAMS['idx'][0]))
    elif PARAMS.has_key('clip'):
        tv2News.playClip(PARAMS['clip'][0])
    else:
        tv2News.listCategories()


