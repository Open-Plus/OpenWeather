# -*- coding: utf-8 -*-
# Yahoo! weather for Hotkey
# Copyright (c) openplus 2016
# Copyright (c) 2boom 2015 
# Based on yweather by 2boom
# Rewrited by Openplus
# v.1.0-r0
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

import os
import time
import gettext
import json
#import socket
import urllib2, urllib
from enigma import eTimer
from enigma import getDesktop, addFont
from twisted.web.client import downloadPage
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.config import getConfigListEntry, ConfigText, ConfigYesNo, ConfigSubsection, ConfigSelection, config, configfile
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.ScrollLabel import ScrollLabel
from Components.Language import language
from Components.Pixmap import Pixmap
from Components.Renderer import PiconUni
#from Components.Converter import YWeather
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.Screen import Screen
from Components.Console import Console as iConsole

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("YWeather", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/YWeather/locale/"))

addFont('/usr/lib/enigma2/python/Plugins/Extensions/YWeather/Audiowide-Regular.ttf', 'audiowide', 100, False)
def _(txt):
	t = gettext.dgettext("YWeather", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def iconsdirs():
	iconset = []
	dirs = os.listdir("%sExtensions/YWeather/istyle/" % resolveFilename(SCOPE_PLUGINS))
	for istyledir in dirs:
		if os.path.isdir("%sExtensions/YWeather/istyle/%s" % (resolveFilename(SCOPE_PLUGINS), istyledir)):
			iconset.append(istyledir)
	return iconset

config.plugins.yweather = ConfigSubsection();
config.plugins.yweather.celsius = ConfigYesNo(default = True)
config.plugins.yweather.weather_city = ConfigText(default = "753692", visible_width = 70, fixed_size = False)
config.plugins.yweather.enabled = ConfigYesNo(default = True)
config.plugins.yweather.skin = ConfigYesNo(default = False)
config.plugins.yweather.istyle = ConfigSelection(default = "default", choices = iconsdirs() )

help_txt = _("1. Visit http://open-plus.es/YWeather/. Enter your city or zip code and press enter...\\n2. Copy ID (digit only) ex:Madrid=766273.\\n3. Paste your ID in \"City code\" and press \"Save\" \\n4. Finally press Get Data. And down the name of your city appears.\\nNote: If you choose to display the weather in infobar you must restart enigma.")


class WeatherInfo(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
                self.session = session                            
		self.setTitle(_("OpenPlus! YWeather"))
		self.time_update = 20
		self.text = {'0':(_('Tornado')), '1':(_('Tropical storm')), '2':(_('Hurricane')), '3':(_('Severe thunderstorms')), '4':(_('Thunderstorms')),\
			'5':(_('Mixed rain and snow')), '6':(_('Mixed rain and sleet')), '7':(_('Mixed snow and sleet')), '8':(_('Freezing drizzle')), '9':(_('Drizzle')),\
			'10':(_('Freezing rain')), '11':(_('Showers')), '12':(_('Rain')), '13':(_('Snow flurries')), '14':(_('Light snow showers')), '15':(_('Blowing snow')),\
			'16':(_('Snow')), '17':(_('Hail')), '18':(_('Sleet')), '19':(_('Dust')), '20':(_('Foggy')), '21':(_('Haze')), '22':(_('Smoky')), '23':(_('Blustery')),\
			'24':(_('Windy')), '25':(_('Cold')), '26':(_('Cloudy')), '27':(_('Mostly cloudy (night)')), '28':(_('Mostly cloudy (day)')), '29':(_('Partly cloudy (night)')),\
			'30':(_('Partly cloudy (day)')), '31':(_('Clear (night)')), '32':(_('Sunny')), '33':(_('Fair (night)')), '34':(_('Fair (day)')), '35':(_('Mixed rain and hail')),\
			'36':(_('Hot')), '37':(_('Isolated thunderstorms')), '38':(_('Scattered thunderstorms')), '39':(_('Scattered thunderstorms')), '40':(_('Scattered showers')),\
			'41':(_('Heavy snow')), '42':(_('Scattered snow showers')), '43':(_('Heavy snow')), '44':(_('Partly cloudy')), '45':(_('Thundershowers')), '46':(_('Snow showers')),\
			'47':(_('Isolated thundershowers')), '3200':(_('Not available'))}
		self.weekday = {'Mon':(_('Monday')), 'Tue':(_('Tuesday')), 'Wed':(_('Wednesday')), 'Thu':(_('Thursday')), 'Fri':(_('Friday')), 'Sat':(_('Saturday')), 'Sun':(_('Sunday'))}
                self.location = {'city':'', 'country':''}
		self.geo = {'lat':'', 'long':''}
		self.units = {'temperature':'', 'distance':'', 'pressure':'', 'speed':''}
		self.wind = {'chill':'', 'direction':'', 'speed':''}
		self.atmosphere = {'humidity':'', 'visibility':'', 'pressure':'', 'rising':''}
		self.astronomy = {'sunrise':'', 'sunset':''}
		self.condition = {'text':'', 'code':'', 'temp':'', 'date':''}
		self.forecast = []
		self.forecastdata = {}
		self["temp_now"] = StaticText()
                self["date"] = StaticText()
                self["text_date"] = StaticText(_("Last Update:"))
		self["temp_now_nounits"] = StaticText()
                self["text_sunri"] = StaticText(_("Sunrise"))
		self["text_sunset"] = StaticText(_("Sunset"))
		self["temp_now_min"] = StaticText()
		self["temp_now_max"] = StaticText()
		self["feels_like"] = StaticText()
		self["wind"] = StaticText()
		self["text_now"] = StaticText()
		self["pressure"] = StaticText()
		self["humidity"] = StaticText()
		self["city_locale"] = StaticText()
		self['sunrise'] = StaticText()
		self['sunset'] = StaticText()
		self["picon_now"] = Pixmap()
		self["tomorrow"] = StaticText(_('Tomorrow'))
		
		for daynumber in ('0', '1', '2', '3', '4'):
			day = 'day' + daynumber
			self["temp_" + day] = StaticText()
			self["forecast_" + day] = StaticText()
			if not daynumber is '0':
				self["picon_" + day] = Pixmap()
				self["text_" + day] = StaticText()
		self.notdata = False
		self["actions"] = ActionMap(["WizardActions",  "MenuActions"], 
		{
			"back": self.close,
			"ok": self.close,
			"right": self.close,
			"left": self.close,
			"down": self.close,
			"up": self.close,
			"menu": self.conf,
		}, -2)
		self.onShow.append(self.get_weather_data)
		
	def conf(self):
		self.session.open(yweather_setup)

	def get_weather_data(self):
		if not os.path.exists("/tmp/yweather.json") or int((time.time() - os.stat("/tmp/yweather.json").st_mtime)/60) >= self.time_update or self.notdata:
                        self.get_jsonfile()
		else:
                        self.parse_weather_data()


	def parse_weather_data(self):
		
		f = open("/tmp/yweather.json")
                data = f.read()
                self.result = json.loads(str(data))
		self.forecast = []
		
		self.location['city'] = str(self.result['query']['results']['channel']['location']['city'])
		self.location['country'] = str(self.result['query']['results']['channel']['location']['country'])
		self.units['temperature'] = str(self.result['query']['results']['channel']['units']['temperature'])
		self.units['distance'] = str(self.result['query']['results']['channel']['units']['distance'])
		self.units['pressure']= str(self.result['query']['results']['channel']['units']['pressure'])
		self.units['speed'] = str(self.result['query']['results']['channel']['units']['speed'])
		self.wind['chill'] = str(self.result['query']['results']['channel']['wind']['chill'])
		self.wind['direction'] = str(self.result['query']['results']['channel']['wind']['direction'])
		self.wind['speed'] = str(self.result['query']['results']['channel']['wind']['speed'])
		self.atmosphere['humidity'] = str(self.result['query']['results']['channel']['atmosphere']['humidity'])
		self.atmosphere['visibility'] = str(self.result['query']['results']['channel']['atmosphere']['visibility'])
		self.atmosphere['pressure'] = str(self.result['query']['results']['channel']['atmosphere']['pressure'])
		self.atmosphere['rising'] = str(self.result['query']['results']['channel']['atmosphere']['rising'])
		self.astronomy['sunrise'] = str(self.result['query']['results']['channel']['astronomy']['sunrise'])
		self.astronomy['sunset'] = str(self.result['query']['results']['channel']['astronomy']['sunset'])
		self.geo['lat'] =  str(self.result['query']['results']['channel']['item']['lat'])
                self.geo['long'] = str(self.result['query']['results']['channel']['item']['long'])
		self.condition['text'] = str(self.result['query']['results']['channel']['item']['condition']['text'])
		self.condition['code'] = str(self.result['query']['results']['channel']['item']['condition']['code'])
		self.condition['temp'] = str(self.result['query']['results']['channel']['item']['condition']['temp'])
		self.condition['date'] = str(self.result['query']['results']['channel']['item']['condition']['date'])
		
		
		for data in ('day', 'date', 'low', 'high', 'text', 'code'):
			for daynumber in ('0', '1', '2', '3', '4'):
				self.forecastdata[data + daynumber] = ''
		
                for data in ('day', 'date', 'low', 'high', 'text', 'code'):
                        for daynumber in ('0', '1', '2', '3', '4'):
                                self.forecastdata[data + daynumber] = str(self.result['query']['results']['channel']['item']['forecast'][int(daynumber)][data])
		else:
			self.notdata = True
		
		for daynumber in ('0', '1', '2', '3', '4'):
			day = 'day' + daynumber
			if self.forecastdata[day] is not '':
				self["forecast_" + day].text = '%s' % self.weekday[self.forecastdata[day]]
			else:
				self["forecast_" + day].text = _('N/A')
				self.notdata = True
			if self.forecastdata['low' + daynumber] is not '' and self.forecastdata['high' + daynumber] is not '':
				self["temp_" + day].text = str('%s/%s' % (self.tempsing(self.forecastdata['low' + daynumber]), self.tempsing(self.forecastdata['high' + daynumber])))
			else:
				self["temp_" + day].text = _('N/A')
				self.notdata = True

                if self.forecastdata['low0'] is not '' and self.forecastdata['high0'] is not '':
                        self["temp_now_min"].text = _('min: %s') % self.tempsing(self.forecastdata['low0'])
                        self["temp_now_max"].text = _('max: %s') % self.tempsing(self.forecastdata['high0'])
                else:
                        self["temp_now_min"].text = _('N/A')
                        self["temp_now_max"].text = _('N/A')
                        self.notdata = True

		defpicon = "%sExtensions/YWeather/istyle/default/3200.png" % resolveFilename(SCOPE_PLUGINS)
		for daynumber in ('1', '2', '3', '4'):
			day = 'day' + daynumber
			self["picon_" + day].instance.setScale(1)
			if self.forecastdata['code' + daynumber] is not '':
				self["text_" + day].text = str(self.text[self.forecastdata['code' + str(daynumber)]])
				# self["picon_" + day].instance.setPixmapFromFile("%sExtensions/YWeather/istyle/%s/%s.png" % (resolveFilename(SCOPE_PLUGINS), config.plugins.yweather.istyle.value, self.forecastdata['code' + daynumber]))
				self["picon_" + day].instance.setPixmapFromFile(str("%sExtensions/YWeather/istyle/%s/%s.png" % (resolveFilename(SCOPE_PLUGINS), config.plugins.yweather.istyle.value, self.forecastdata['code' + str(daynumber)])))
			else:
				self["text_" + day].text = _('N/A')
				self["picon_" + day].instance.setPixmapFromFile(defpicon)
				self.notdata = True
			self["picon_" + day].instance.show()
		if self.condition['temp'] is not '':
			self["temp_now"].text = str(self.tempsing(self.condition['temp']))
			self["temp_now_nounits"].text = str(self.tempsing(self.condition['temp']))
			self["temp_now_min"].text = str(self.tempsing(self.forecastdata["low0"]))
                        self["temp_now_max"].text = str(self.tempsing(self.forecastdata["high0"]))
			                
		else:
			self["temp_now"].text = _('N/A')
			self["temp_now_nounits"].text = _('N/A')
			self["temp_now_min"].text = _('N/A')
                        self["temp_now_max"].text = _('N/A')
			self.notdata = True
                if self.condition['date'] is not '':
			self["date"].text = (self.condition['date'])
		else:
			self["date"].text = _('N/A')
			self.notdata = True
		if self.wind['chill'] is not '':
			self["feels_like"].text = _('Feels: %s') % self.tempsing(self.wind['chill'])
		else:
			self["feels_like"].text = _('N/A')
			self.notdata = True
		if not self.condition['code'] is '' and not self.wind['speed'] is '':
			direct = int(self.condition['code'])
			tmp_wind = (float(self.wind['speed']) * 1000)/3600
			if direct >= 0 and direct <= 20:
				self["wind"].text = _('N, %3.02f m/s') % tmp_wind
			elif direct >= 21 and direct <= 35:
				self["wind"].text = _('NNE, %3.02f m/s') % tmp_wind
			elif direct >= 36 and direct <= 55:
				self["wind"].text = _('NE, %3.02f m/s') % tmp_wind
			elif direct >= 56 and direct <= 70:
				self["wind"].text = _('ENE, %3.02f m/s') % tmp_wind
			elif direct >= 71 and direct <= 110:
				self["wind"].text = _('E, %3.02f m/s') % tmp_wind
			elif direct >= 111 and direct <= 125:
				self["wind"].text = _('ESE, %3.02f m/s') % tmp_wind
			elif direct >= 126 and direct <= 145:
				self["wind"].text = _('SE, %3.02f m/s') % tmp_wind
			elif direct >= 146 and direct <= 160:
				self["wind"].text = _('SSE, %3.02f m/s') % tmp_wind
			elif direct >= 161 and direct <= 200:
				self["wind"].text = _('S, %3.02f m/s') % tmp_wind
			elif direct >= 201 and direct <= 215:
				self["wind"].text = _('SSW, %3.02f m/s') % tmp_wind
			elif direct >= 216 and direct <= 235:
				self["wind"].text = _('SW, %3.02f m/s') % tmp_wind
			elif direct >= 236 and direct <= 250:
				self["wind"].text = _('WSW, %3.02f m/s') % tmp_wind
			elif direct >= 251 and direct <= 290:
				self["wind"].text = _('W, %3.02f m/s') % tmp_wind
			elif direct >= 291 and direct <= 305:
				self["wind"].text = _('WNW, %3.02f m/s') % tmp_wind
			elif direct >= 306 and direct <= 325:
				self["wind"].text = _('NW, %3.02f m/s') % tmp_wind
			elif direct >= 326 and direct <= 340:
				self["wind"].text = _('NNW, %3.02f m/s') % tmp_wind
			elif direct >= 341 and direct <= 360:
				self["wind"].text = _('N, %3.02f m/s') % tmp_wind
			else:
				self["wind"].text = _('N/A')
				self.notdata = True
		else:
			self.notdata = True
		if not self.condition['code'] is '':
			self["text_now"].text = self.text[self.condition['code']]
		else:
			self["text_now"].text = _('N/A')
			self.notdata = True
		if not self.atmosphere['pressure'] is '':
			tmp_pressure = round(float(self.atmosphere['pressure']) * 0.75)
			self["pressure"].text = _("%d mmHg") % tmp_pressure
		else:
			self["pressure"].text = _('N/A')
			self.notdata = True
		if not self.atmosphere['humidity'] is '':
			self["humidity"].text = _('%s%% humidity') % self.atmosphere['humidity']
		else:
			self["humidity"].text = _('N/A')
			self.notdata = True
			
		if not self.location['city'] is '' and not self.location['country'] is '':	
                        self["city_locale"].text = self.location['city'] + "-" +self.location['country']
                else:
                        self["city_locale"].text = _('N/A')
                        
                if not self.astronomy['sunrise'] is '' and not self.astronomy['sunset'] is '':        
                        self["sunrise"].text = self.astronomy['sunrise']
                        self["sunset"].text = self.astronomy['sunset']
                else:
                        self["sunrise"].text = _('N/A')
                        self["sunset"].text = _('N/A')
		
		self["picon_now"].instance.setScale(1)
		if not self.condition['code'] is '':
                        #self["picon_now"].instance.setPixmapFromFile(str("%sExtensions/YWeather/istyle/%s/%s.png" % (resolveFilename(SCOPE_PLUGINS), "default", self.condition['code'])))
                        self["picon_now"].instance.setPixmapFromFile(str("%sExtensions/YWeather/istyle/%s/%s.png" % (resolveFilename(SCOPE_PLUGINS), config.plugins.yweather.istyle.value, self.condition['code'])))
			#self["picon_now"].instance.setPixmapFromFile("%sExtensions/YWeather/istyle/%s/%s.png" % (resolveFilename(SCOPE_PLUGINS), "default", self.condition['code']))
                else:
			self["picon_now"].instance.setPixmapFromFile(defpicon)
		self["picon_now"].instance.show()

	def get_jsonfile(self):
                try:
                        baseurl = "https://query.yahooapis.com/v1/public/yql?"
                        yql_query = "select * from weather.forecast where woeid=%s" % config.plugins.yweather.weather_city.value
                        jsonfile = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
                        downloadPage(jsonfile, "/tmp/yweather.json").addCallback(self.downloadFinished).addErrback(self.downloadFailed)
                except TypeError:
                        self.downloadFailed()
                
	def downloadFinished(self, result):
                print "[YWeather] Download finished"
		self.notdata = False
		self.parse_weather_data()

	def downloadFailed(self, result):
		self.notdata = True
		print "[YWeather] Download failed!"

	def tempsing(self, what):
		if not what[0] is '-' and not what[0] is '0':
                        if self.units['temperature'] == "F":
			                return str(int((int(what)-32)/1.8)) + '%s' % unichr(176) + 'C'                
                        return '+' + what + '%s' % unichr(176) + self.units['temperature']
		else:
			return what + '%s' % unichr(176) + self.units['temperature']

##############################################################################
        screenWidth = getDesktop(0).size().width()
	if screenWidth and screenWidth == 1920:
            skin = """<screen name="WeatherInfo" position="0,0" size="1920,1080" title="OpenPlus! YWeather" zPosition="1" flags="wfNoBorder" backgroundColor="transparent">
  <eLabel position="493,307" size="457,2" backgroundColor="grey" zPosition="5" />
  <widget source="city_locale" render="Label" position="500,275" size="450,30" zPosition="2" font="audiowide; 27" halign="right" transparent="1" backgroundColor="background" foregroundColor="white" />
  <ePixmap position="421,839" size="81,40" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YWeather/images/key_exit2.png" transparent="1" alphatest="blend" />
  <widget name="picon_now" position="678,328" size="96,96" zPosition="2" alphatest="blend" />
  <widget source="temp_now_min" render="Label" position="473,391" size="190,20" zPosition="3" font="audiowide; 17" halign="right" transparent="1" backgroundColor="background" foregroundColor="white" />
  <widget source="temp_now_max" render="Label" position="473,415" size="190,20" zPosition="3" font="audiowide; 17" halign="right" transparent="1" backgroundColor="background" foregroundColor="white" />
  <widget source="temp_now" render="Label" position="473,344" size="190,43" zPosition="2" font="audiowide; 35" halign="right" transparent="1" foregroundColor="yellow" backgroundColor="background" />
  <widget source="feels_like" render="Label" position="473,321" size="190,20" zPosition="2" font="audiowide; 17" halign="right" transparent="2" backgroundColor="background" />
  <widget source="text_now" render="Label" position="478,446" size="484,22" zPosition="3" font="audiowide; 18" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
  <widget source="pressure" render="Label" position="787,368" size="160,20" zPosition="3" font="audiowide; 17" halign="left" transparent="1" foregroundColor="white" backgroundColor="background" />
  <widget source="humidity" render="Label" position="787,415" size="160,20" zPosition="3" font="audiowide; 17" halign="left" transparent="1" foregroundColor="white" backgroundColor="background" />
  <widget source="wind" render="Label" position="787,321" size="160,20" zPosition="3" font="audiowide; 17" halign="left" transparent="1" foregroundColor="white" backgroundColor="background" />
  <widget name="picon_day1" position="538,603" size="96,96" zPosition="2" alphatest="blend" />
  <widget source="tomorrow" render="Label" position="479,574" size="220,25" zPosition="2" font="audiowide; 19" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
  <widget source="temp_day1" render="Label" position="479,702" size="220,25" zPosition="3" font="audiowide; 19" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
  <widget source="text_day1" render="Label" position="479,729" size="220,45" zPosition="2" font="audiowide; 16" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
  <ePixmap position="1418,839" size="81,40" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YWeather/images/key_menu2.png" transparent="1" alphatest="blend" />
  <widget name="picon_day2" position="794,603" size="96,96" zPosition="2" alphatest="blend" />
  <widget source="forecast_day2" render="Label" position="732,574" size="220,25" zPosition="3" font="audiowide; 19" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
  <widget source="temp_day2" render="Label" position="732,702" size="220,25" zPosition="3" font="audiowide; 19" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
  <widget source="text_day2" render="Label" position="732,729" size="220,45" zPosition="3" font="audiowide; 16" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
  <widget name="picon_day3" position="1048,604" size="96,96" zPosition="2" alphatest="blend" />
  <widget source="forecast_day3" render="Label" position="986,574" size="220,25" zPosition="2" font="audiowide; 19" halign="center" transparent="1" valign="center" foregroundColor="white" backgroundColor="background" />
  <widget source="temp_day3" render="Label" position="986,702" size="220,25" zPosition="2" font="audiowide; 19" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
  <widget source="text_day3" render="Label" position="986,729" size="220,45" zPosition="2" font="audiowide; 16" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
  <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="center" position="410,833" size="1100,50" font="audiowide; 32" backgroundColor="background" foregroundColor="white" noWrap="1" />
  <widget name="picon_day4" position="1304,603" size="96,96" zPosition="2" alphatest="blend" />
  <widget source="forecast_day4" render="Label" position="1240,574" size="220,25" zPosition="2" font="audiowide; 19" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
  <widget source="temp_day4" render="Label" position="1240,702" size="220,25" zPosition="2" font="audiowide; 19" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
  <widget source="text_day4" render="Label" position="1240,729" size="220,45" zPosition="2" font="audiowide; 16" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
  <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YWeather/images/back.png" backgroundColor="background" position="center,center" size="1130,730" transparent="0" zPosition="-32" />
  <widget source="sunrise" render="Label" position="1104,336" size="133,30" zPosition="2" font="audiowide; 16" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
  <widget source="sunset" render="Label" position="1104,428" size="133,30" zPosition="2" font="audiowide; 16" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
  <ePixmap position="1018,297" size="73,73" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YWeather/images/sunri.png" transparent="1" alphatest="blend" />
  <ePixmap position="1026,393" size="61,61" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YWeather/images/sunset.png" transparent="1" alphatest="blend" />
  <widget transparent="1" zPosition="5" valign="center" halign="left" position="1104,302" size="138,30" font="audiowide; 19" foregroundColor="white" noWrap="1" source="text_sunri" render="Label" backgroundColor="background" />
  <widget transparent="1" zPosition="5" valign="center" halign="left" position="1104,395" size="137,30" font="audiowide; 19" foregroundColor="white" noWrap="1" source="text_sunset" render="Label" backgroundColor="background" />
  <widget source="text_date" position="539,805" size="357,25" backgroundColor="background" zPosition="5" transparent="1" halign="right" font="audiowide; 16" render="Label" />
  <widget source="date" render="Label" position="906,805" size="614,25" zPosition="2" font="audiowide; 16" halign="left" transparent="1" foregroundColor="yellow" backgroundColor="background" />
</screen>"""
        else:
            skin = """<screen name="WeatherInfo" position="center,center" size="1280,720" title="OpenPlus! YWeather" zPosition="1" flags="wfNoBorder" backgroundColor="transparent">
    <eLabel position="193,149" size="440,2" backgroundColor="grey" zPosition="5" />
    <ePixmap position="157,603" size="81,40" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YWeather/images/key_exit2.png" transparent="1" alphatest="blend" />
    <widget name="picon_now" position="377,168" size="96,96" zPosition="2" alphatest="blend" />
    <widget source="temp_now_min" render="Label" position="185,232" size="170,20" zPosition="3" font="Regular; 17" halign="right" transparent="1" backgroundColor="background" foregroundColor="white" />
    <widget source="city_locale" render="Label" position="205,115" size="417,29" zPosition="3" font="Regular; 25" halign="right" transparent="1" backgroundColor="background" foregroundColor="white" />
    <widget source="temp_now_max" render="Label" position="185,258" size="170,20" zPosition="3" font="Regular; 17" halign="right" transparent="1" backgroundColor="background" foregroundColor="white" />
    <widget source="temp_now" render="Label" position="185,185" size="170,43" zPosition="2" font="Regular; 35" halign="right" transparent="1" foregroundColor="yellow" backgroundColor="background" />
    <widget source="feels_like" render="Label" position="185,161" size="170,20" zPosition="2" font="Regular; 17" halign="right" transparent="2" backgroundColor="background" />
    <widget source="text_now" render="Label" position="180,289" size="464,22" zPosition="3" font="Regular; 19" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
    <widget source="pressure" render="Label" position="495,210" size="140,20" zPosition="3" font="Regular; 17" halign="left" transparent="1" foregroundColor="white" backgroundColor="background" />
    <widget source="humidity" render="Label" position="495,258" size="140,20" zPosition="3" font="Regular; 17" halign="left" transparent="1" foregroundColor="white" backgroundColor="background" />
    <widget source="wind" render="Label" position="495,161" size="140,20" zPosition="3" font="Regular; 17" halign="left" transparent="1" foregroundColor="white" backgroundColor="background" />
    <widget name="picon_day1" position="232,402" size="96,96" zPosition="2" alphatest="blend" />
    <widget source="tomorrow" render="Label" position="217,380" size="125,25" zPosition="2" font="Regular; 19" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
    <widget source="temp_day1" render="Label" position="220,502" size="120,21" zPosition="3" font="Regular; 19" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
    <widget source="text_day1" render="Label" position="205,526" size="150,40" zPosition="2" font="Regular; 16" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
    <ePixmap position="1044,603" size="81,40" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YWeather/images/key_menu2.png" transparent="1" alphatest="blend" />
    <widget name="picon_day2" position="471,402" size="96,96" zPosition="2" alphatest="blend" />
    <widget source="forecast_day2" render="Label" position="457,380" size="125,25" zPosition="2" font="Regular; 19" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
    <widget source="temp_day2" render="Label" position="458,502" size="120,21" zPosition="2" font="Regular; 19" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
    <widget source="text_day2" render="Label" position="443,526" size="150,40" zPosition="2" font="Regular; 16" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
    <widget name="picon_day3" position="710,402" size="96,96" zPosition="2" alphatest="blend" />
    <widget source="forecast_day3" render="Label" position="697,380" size="125,25" zPosition="2" font="Regular; 19" halign="center" transparent="1" valign="center" foregroundColor="white" backgroundColor="background" />
    <widget source="temp_day3" render="Label" position="697,502" size="120,21" zPosition="2" font="Regular; 19" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
    <widget source="text_day3" render="Label" position="682,526" size="150,40" zPosition="2" font="Regular; 16" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
    <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="center" position="125,598" size="1030,50" font="Regular; 32" backgroundColor="background" foregroundColor="white" noWrap="1" />
    <widget name="picon_day4" position="952,402" size="96,96" zPosition="2" alphatest="blend" />
    <widget source="forecast_day4" render="Label" position="938,380" size="125,25" zPosition="2" font="Regular; 19" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
    <widget source="temp_day4" render="Label" position="938,502" size="120,21" zPosition="2" font="Regular; 19" halign="center" transparent="1" foregroundColor="yellow" backgroundColor="background" />
    <widget source="text_day4" render="Label" position="923,526" size="150,40" zPosition="2" font="Regular; 16" halign="center" transparent="1" foregroundColor="white" backgroundColor="background" />
    <widget source="sunrise" render="Label" position="791,179" size="124,30" zPosition="2" font="audiowide; 16" halign="left" transparent="1" foregroundColor="yellow" backgroundColor="background" />
    <widget source="sunset" render="Label" position="791,266" size="124,30" zPosition="2" font="audiowide; 16" halign="left" transparent="1" foregroundColor="yellow" backgroundColor="background" />
    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YWeather/images/back7.png" backgroundColor="background" position="124,46" size="1030,630" transparent="0" zPosition="-32" />
    <ePixmap position="702,141" size="73,73" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YWeather/images/sunri.png" transparent="1" alphatest="blend" />
    <ePixmap position="709,233" size="61,61" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YWeather/images/sunset.png" transparent="1" alphatest="blend" />
    <widget transparent="1" zPosition="5" valign="center" halign="left" position="791,149" size="138,30" font="Regular; 19" foregroundColor="white" noWrap="1" source="text_sunri" render="Label" backgroundColor="background" />
    <widget transparent="1" zPosition="5" valign="center" halign="left" position="791,236" size="137,30" font="Regular; 19" foregroundColor="white" noWrap="1" source="text_sunset" render="Label" backgroundColor="background" />
</screen>"""

class yweather_setup(Screen, ConfigListScreen):
	skin = """<screen name="yweather_setup" position="center,center" size="750,545" title="OpenPlus! YWeather Configuration" flags="wfNoBorder" backgroundColor="background">
  <widget position="15,45" size="720,150" name="config" scrollbarMode="showOnDemand" backgroundColor="background" foregroundColor="white" itemHeight="25" />
  <eLabel position="30,200" size="690,2" backgroundColor="#00aaaaaa" zPosition="5" />
  <widget source="key_red" render="Label" position="20,488" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" transparent="0" backgroundColor="red" foregroundColor="white" />
  <widget source="key_green" render="Label" position="202,488" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" transparent="0" backgroundColor="green" foregroundColor="white" />
  <widget source="key_yellow" render="Label" position="385,488" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" transparent="0" backgroundColor="yellow" foregroundColor="white" />
  <widget source="key_blue" render="Label" position="567,488" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" transparent="0" backgroundColor="blue" foregroundColor="white" />
  <widget name="text" position="15,205" size="720,166" font="Regular; 20" halign="left" noWrap="1" backgroundColor="background" foregroundColor="yellow" />
  <widget name="icon1" position="100,381" size="96,96" zPosition="2" alphatest="blend" backgroundColor="background" />
  <widget name="icon2" position="245,381" size="96,96" zPosition="2" alphatest="blend" backgroundColor="background" />
  <widget name="icon3" position="390,381" size="96,96" zPosition="2" alphatest="blend" foregroundColor="background" backgroundColor="background" />
  <widget name="icon4" position="535,381" size="96,96" zPosition="2" alphatest="blend" foregroundColor="background" backgroundColor="background" />
  <widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="center" position="15,5" size="720,33" noWrap="1" font="Regular; 28" />
  <widget backgroundColor="background" foregroundColor="white" halign="right" render="Label" position="314,120" size="417,30" source="city_locale" transparent="1" zPosition="2" font="Regular; 19" />
  <widget transparent="1" zPosition="5" valign="center" halign="left" position="20,120" size="295,30" foregroundColor="white" noWrap="1" source="text_city" render="Label" backgroundColor="background" font="Regular; 19" />
</screen>"""
	def __init__(self, session):
		self.session = session
                self.iConsole = iConsole()
		Screen.__init__(self, session)
		config.plugins.yweather.istyle = ConfigSelection(choices = iconsdirs())
		self.setTitle(_("OpenPlus! YWeather Configuration"))
		self.list = []
		self.list.append(getConfigListEntry(_("City code"), config.plugins.yweather.weather_city))
		self.list.append(getConfigListEntry(_("Weather icons style"), config.plugins.yweather.istyle))
		#self.list.append(getConfigListEntry(_("Weather in Infobar (only openplusHD)"), config.plugins.yweather.skin))
		ConfigListScreen.__init__(self, self.list, session=session)
		self["text"] = ScrollLabel("")
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
		#self["key_yellow"] = StaticText(_("Get data"))
                self["key_blue"] = StaticText(_("Restart"))
                self["text_city"] = StaticText(_("City name"))
                self["city_locale"] = StaticText()
		self["text"].setText(help_txt)
		for item in ('1', '2', '3', '4'):
			self["icon" + item ] = Pixmap()
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"red": self.cancel,
			"cancel": self.cancel,
			"green": self.save,
			#"yellow": self.getdata,
                        "blue": self.restartGUI,
			"ok": self.save
		}, -2)
		self.onLayoutFinish.append(self.showicon)

	def showicon(self):
		count = 1
		for number in ('8', '18', '22', '32'):
			if fileExists("%sExtensions/YWeather/istyle/%s/%s.png" % (resolveFilename(SCOPE_PLUGINS), config.plugins.yweather.istyle.value, number)):
				self["icon%s" % str(count)].instance.setScale(1)
				self["icon%s" % str(count)].instance.setPixmapFromFile("%sExtensions/YWeather/istyle/%s/%s.png" % (resolveFilename(SCOPE_PLUGINS), config.plugins.yweather.istyle.value, number))
				self["icon%s" % str(count)].instance.show()
			count += 1

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.showicon()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.showicon()

	def cancel(self):
		for i in self["config"].list:
			i[1].cancel()
		self.close(False)

        def city_locale(self): 
                if not self.location['city'] is '' and not self.location['country'] is '':	
                        self["city_locale"].text = self.location['city'] + "-" +self.location['country']
                else:
                        self["city_locale"].text = _('N/A')
                        
	def restartGUI(self):
                self.session.open(TryQuitMainloop, 3)
                        
	def save(self):
		for i in self["config"].list:
			i[1].save()
		configfile.save()
                self.iConsole = iConsole()
		#if config.plugins.yweather.skin.value:
                #    
                #        print "infobar1 ok"
                #        if fileExists('%sExtensions/YWeather/skin_infobars.xml' % resolveFilename(SCOPE_PLUGINS)):
                #            self.iConsole.ePopen("cp /usr/lib/enigma2/python/Plugins/Extensions/YWeather/skin_infobars.xml /usr/share/enigma2/openplusHD/skin_infobars.xml")
                #else:
                #  if config.plugins.yweather.skin:
                #          print "infobar2 ok"
                #          if fileExists('%sExtensions/YWeather/skindef/skin_infobars.xml' % resolveFilename(SCOPE_PLUGINS)):
                #             self.iConsole.ePopen("cp /usr/lib/enigma2/python/Plugins/Extensions/YWeather/skindef/skin_infobars.xml /usr/share/enigma2/openplusHD/skin_infobars.xml")
		self.mbox = self.session.open(MessageBox,(_("configuration is saved")), MessageBox.TYPE_INFO, timeout = 4 )

def main(session, **kwargs):
	session.open(WeatherInfo)
########################################################################
def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("OpenWeather"), main, "openweather", 7)]
	return []
##############################################################################
def Plugins(**kwargs):
	screenwidth = getDesktop(0).size().width()
	if screenwidth and screenwidth == 1920:
		return [PluginDescriptor(name=_("OpenWeather"), description=_("Your city weather for Openplus! Yahoo Weather"), where=PluginDescriptor.WHERE_MENU, fnc=menu), PluginDescriptor(name=_("OpenPlus YWeather"), description=_("Your city weather for Openplus! Yahoo Weather"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="openywhd.png", fnc=main)]
	else:
		return [PluginDescriptor(name=_("OpenWeather"), description=_("Your city weather for Openplus! Yahoo Weather"), where=PluginDescriptor.WHERE_MENU, fnc=menu), PluginDescriptor(name=_("OpenPlus YWeather"), description=_("Your city weather for Openplus! Yahoo Weather"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="openyw.png", fnc=main)]
