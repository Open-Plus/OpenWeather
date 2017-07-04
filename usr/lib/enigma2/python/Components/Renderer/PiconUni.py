# OPWeather Renderer
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# Adapted by Iqas & Villak for OpenPlus 2017

from Renderer import Renderer
from enigma import ePixmap, eTimer, getDesktop
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Tools.LoadPixmap import LoadPixmap
from Components.Pixmap import Pixmap
HD = getDesktop(0).size()
if HD.width() > 1280:
    iconpath = 'iconmeteo'
else:
    iconpath = 'iconmeteo'

class PiconUni(Renderer):
    __module__ = __name__
    searchPaths = ('/usr/share/enigma2/%s/', '/media/cf/%s/', '/media/sda1/%s/', '/media/usb/%s/', '/media/hdd/%s/', '/usr/lib/enigma2/python/Plugins/Extensions/OPWeather/%s/')

    def __init__(self):
        Renderer.__init__(self)
        self.path = iconpath
        self.nameCache = {}
        self.pngname = ''

    def applySkin(self, desktop, parent):
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == 'path':
                self.path = iconpath
            else:
                attribs.append((attrib, value))

        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if self.instance:
            pngname = ''
            if what[0] != self.CHANGED_CLEAR:
                sname = self.source.text
                pngname = self.nameCache.get(sname, '')
                if pngname == '':
                    pngname = self.findPicon(sname)
                    if pngname != '':
                        self.nameCache[sname] = pngname
            if pngname == '':
                pngname = self.nameCache.get('default', '')
                if pngname == '':
                    pngname = self.findPicon('picon_meteo')
                    if pngname == '':
                        tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_meteo.png')
                        if fileExists(tmp):
                            pngname = tmp
                        else:
                            pngname = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_meteo.png')
                    self.nameCache['default'] = pngname
            if self.pngname != pngname:
                self.pngname = pngname
                self.rTimer()
                self.instance.setPixmapFromFile(self.pngname)

    def findPicon(self, serviceName):
        for path in self.searchPaths:
            pngname = path % self.path + serviceName + '.png'
            if fileExists(pngname):
                return pngname

        return ''

    def rTimer(self):
        self.slide = 1
        self.pics = []
        self.pics.append(LoadPixmap(self.path + '/' + 'picon_meteo.png'))
        self.timer = eTimer()
        self.timer.callback.append(self.timerEvent)
        self.timer.start(1, True)

    def timerEvent(self):
        if self.slide != 0:
            self.timer.stop()
            self.instance.setPixmap(self.pics[self.slide - 1])
            self.slide = self.slide - 1
            self.timer.start(1, True)
        else:
            self.timer.stop()
            self.instance.setPixmapFromFile(self.pngname)