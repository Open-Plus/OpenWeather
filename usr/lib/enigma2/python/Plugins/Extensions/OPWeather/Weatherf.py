# -*- coding: UTF-8 -*-
#
# Plugin - Weather Foreca
# Adapted by Iqas & Villak for Openplus
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
#
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.Language import language
from Components.MenuList import MenuList
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigText, ConfigYesNo, ConfigSubsection, ConfigSelection, config, configfile, NoSave
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from xml.etree.cElementTree import fromstring as cet_fromstring
from urllib2 import Request, urlopen, URLError, HTTPError
from twisted.web.client import downloadPage
from enigma import eTimer, ePoint, getDesktop
from os import system, environ
import time
import os
import gettext
def _(txt):
	t = gettext.dgettext("OPWeather", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
HD = getDesktop(0).size()


config.plugins.weatherfor = ConfigSubsection()
config.plugins.weatherfor.city = ConfigText(default="Madrid", visible_width = 250, fixed_size = False)
config.plugins.weatherfor.degreetype = ConfigSelection(default="C", choices = [
	("C", _("Celsius")),
	("F", _("Fahrenheit"))])
	

class Weatherfor(ConfigListScreen, Screen):
	def __init__(self, session):
                if HD.width() > 1280:
                        path = '/usr/lib/enigma2/python/Plugins/Extensions/OPWeather/Skin/Weatherf1080.xml'
                        with open(path, 'r') as f:
                            self.skin = f.read()
                            f.close()
                else:
                        path = '/usr/lib/enigma2/python/Plugins/Extensions/OPWeather/Skin/Weatherf720.xml'
                        with open(path, 'r') as f:
                            self.skin = f.read()
                            f.close()
		Screen.__init__(self, session)
		self.session = session
		self.skinName = ["Weatherfor"]

		self.time_update = 20
		self.language = config.osd.language.value.replace('_', '-')
		if self.language == 'en-EN':
			self.language = 'en-US'
		self.city = config.plugins.weatherfor.city.value
		self.degreetype = config.plugins.weatherfor.degreetype.value
		

		self.location = {'Location':''}
		self.timezone = {'Timezone':''}
		self.latitude = {'Latitude':''}
		self.longitude = {'Longitude':''}
		self.observationtime = {'Time':''}
		self.observationpoint = {'Point':''}
		self.attribution = {'Attribution':''}
		self.temperature = {'Temperature':''}
		self.feelslike = {'Feelslike':''}
		self.skytext = {'Skytext':''}
		self.humidity = {'Humidity':''}
                self.winddisplay = {'Wind':''}
                
		self.pic = {'Pic':''}

		self.lowtemp0 = {'Lowtemp0':''}
		self.hightemp0 = {'Hightemp0':''}
		self.skytext0 = {'Skytext0':''}
		self.precip0 = {'Precip0':''}
		self.date0 = {'Date0':''}
		self.day0 = {'Day0':''}
		self.pic0 = {'Pic0':''}

		self.lowtemp1 = {'Lowtemp1':''}
		self.hightemp1 = {'Hightemp1':''}
		self.skytext1 = {'Skytext1':''}
		self.precip1 = {'Precip1':''}
		self.date1 = {'Date1':''}
		self.day1 = {'Day1':''}
		self.pic1 = {'Pic1':''}

		self.lowtemp2 = {'Lowtemp2':''}
		self.hightemp2 = {'Hightemp2':''}
		self.skytext2 = {'Skytext2':''}
		self.precip2 = {'Precip2':''}
		self.date2 = {'Date2':''}
		self.day2 = {'Day2':''}
		self.pic2 = {'Pic2':''}

		self.lowtemp3 = {'Lowtemp3':''}
		self.hightemp3 = {'Hightemp3':''}
		self.skytext3 = {'Skytext3':''}
		self.precip3 = {'Precip3':''}
		self.date3 = {'Date3':''}
		self.day3 = {'Day3':''}
		self.pic3 = {'Pic3':''}

		self.lowtemp4 = {'Lowtemp4':''}
		self.hightemp4 = {'Hightemp4':''}
		self.skytext4 = {'Skytext4':''}
		self.precip4 = {'Precip4':''}
		self.date4 = {'Date4':''}
		self.day4 = {'Day4':''}
		self.pic4 = {'Pic4':''}

		self["shortcuts"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions", "EPGSelectActions"], 
		{ "cancel": self.exit,
                "ok": self.exit,
		"red": self.openVirtualKeyBoard,
                "menu": self.config,
		}, -1)

		self.forecast = []
		self.forecastdata = {}
		self["Title"] = StaticText(_("OpenPlus! Weather"))
		self["locationtxt"] = StaticText(_("Location:"))
		self["timezonetxt"] = StaticText(_("Timezone:"))
		self["latitudetxt"] = StaticText(_("Latitude:"))
		self["longitudetxt"] = StaticText(_("Longitude:"))
		self["temperaturetxt"] = StaticText(_("Temperature:"))
		self["feelsliketxt"] = StaticText(_("Feels like:"))
		self["humiditytxt"] = StaticText(_("Humidity:"))
		self["preciptxt"] = StaticText(_("Chance precip:"))
		self["windtxt"] = StaticText(_("Wind:"))
		self["pointtxt"] = StaticText(_("Observation point:"))
		self["datetxt"] = StaticText(_("Date:"))
		self["daytxt"] = StaticText(_("Day week:"))
                self["lab3b"] = StaticText(_("Last Updated:"))
                self["key_red"] = Label(_("Change city"))

		self["location"] = StaticText()
		self["timezone"] = StaticText()
		self["latitude"] = StaticText()
		self["longitude"] = StaticText()
		self["observationtime"] = StaticText()
		self["observationpoint"] = StaticText()
		self["attribution"] = StaticText()
		self["temperature"] = StaticText()
		self["feelslike"] = StaticText()
		self["skytext"] = StaticText()
		self["humidity"] = StaticText()
                self["winddisplay"] = StaticText()
                
		self["pic"] = Pixmap()

		self["temperature0"] = StaticText()
		self["skytext0"] = StaticText()
		self["precip0"] = StaticText()
		self["date0"] = StaticText()
		self["day0"] = StaticText()
		self["pic0"] = Pixmap()

		self["temperature1"] = StaticText()
		self["skytext1"] = StaticText()
		self["precip1"] = StaticText()
		self["date1"] = StaticText()
		self["day1"] = StaticText()
		self["pic1"] = Pixmap()

		self["temperature2"] = StaticText()
		self["skytext2"] = StaticText()
		self["precip2"] = StaticText()
		self["date2"] = StaticText()
		self["day2"] = StaticText()
		self["pic2"] = Pixmap()

		self["temperature3"] = StaticText()
		self["skytext3"] = StaticText()
		self["precip3"] = StaticText()
		self["date3"] = StaticText()
		self["day3"] = StaticText()
		self["pic3"] = Pixmap()

		self["temperature4"] = StaticText()
		self["skytext4"] = StaticText()
		self["precip4"] = StaticText()
		self["date4"] = StaticText()
		self["day4"] = StaticText()
		self["pic4"] = Pixmap()

		self.notdata = False
		self.onShow.append(self.get_weather_data)

	def get_xmlfile(self):
		xmlfile = "http://weather.service.msn.com/data.aspx?weadegreetype=%s&culture=%s&weasearchstr=%s&src=outlook" % (self.degreetype, self.language, self.city)
		downloadPage(xmlfile, "/tmp/weatherfore.xml").addCallback(self.downloadFinished).addErrback(self.downloadFailed)

	def get_weather_data(self):
		if not os.path.exists("/tmp/weatherfore.xml") or int((time.time() - os.stat("/tmp/weatherfore.xml").st_mtime)/60) >= self.time_update or self.notdata:
			self.get_xmlfile()
		else:
			self.parse_weather_data()

	def downloadFinished(self, result):
		print "[Weatherfor] Download finished"
		self.notdata = False
		self.parse_weather_data()

	def downloadFailed(self, result):
		self.notdata = True
		print "[Weatherfor] Download failed!"

	def parse_weather_data(self):
		self.forecast = []
		for line in open("/tmp/weatherfore.xml"):
			try:
				if "<weather" in line:
					self.location['Location'] = line.split('weatherlocationname')[1].split('"')[1].split(',')[0]
					if not line.split('timezone')[1].split('"')[1][0] is '0':
						self.timezone['Timezone'] = '+' + line.split('timezone')[1].split('"')[1]
					else:
						self.timezone['Timezone'] = line.split('timezone')[1].split('"')[1]
					self.latitude['Latitude'] = line.split(' lat')[1].split('"')[1]
					self.longitude['Longitude'] = line.split(' long')[1].split('"')[1]
					self.observationtime['Time'] = line.split('observationtime')[1].split('"')[1]
					self.observationpoint['Point'] = line.split('observationpoint')[1].split('"')[1]
					self.attribution['Attribution'] = line.split('attribution')[1].split('"')[1]
				if "<current" in line:
					if not line.split('temperature')[1].split('"')[1][0] is '-' and not line.split('temperature')[1].split('"')[1][0] is '0':
						self.temperature['Temperature'] = '+' + line.split('temperature')[1].split('"')[1]
					else:
						self.temperature['Temperature'] = line.split('temperature')[1].split('"')[1]
					if not line.split('feelslike')[1].split('"')[1][0] is '-' and not line.split('feelslike')[1].split('"')[1][0] is '0':
						self.feelslike['Feelslike'] = '+' + line.split('feelslike')[1].split('"')[1]
					else:
						self.feelslike['Feelslike'] = line.split('feelslike')[1].split('"')[1]
					self.pic['Pic'] = line.split('skycode')[1].split('"')[1]
					self.skytext['Skytext'] = line.split('skytext')[1].split('"')[1]
					self.humidity['Humidity'] = line.split('humidity')[1].split('"')[1]
					self.winddisplay['Wind'] = line.split('winddisplay')[1].split('"')[1]
					
#	today	#
				if "<forecast" in line:
					if not line.split('low')[1].split('"')[1][0] is '-' and not line.split('low')[1].split('"')[1][0] is '0':
						self.lowtemp0['Lowtemp0'] = '+' + line.split('low')[1].split('"')[1]
					else:
						self.lowtemp0['Lowtemp0'] = line.split('low')[1].split('"')[1]
					if not line.split('high')[1].split('"')[1][0] is '-' and not line.split('high')[1].split('"')[1][0] is '0':
						self.hightemp0['Hightemp0'] = '+' + line.split('high')[1].split('"')[1]
					else:
						self.hightemp0['Hightemp0'] = line.split('high')[1].split('"')[1]
					self.pic0['Pic0'] = line.split('skycodeday')[1].split('"')[1]
					self.date0['Date0'] = line.split('date')[2].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[2].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[2].split('"')[1].split('-')[0].strip()
					self.day0['Day0'] = line.split(' day')[2].split('"')[1]
					self.skytext0['Skytext0'] = line.split('skytextday')[1].split('"')[1]
					self.precip0['Precip0'] = line.split('precip')[1].split('"')[1]
#	day 1	#
				if "<forecast" in line:
					if not line.split('low')[2].split('"')[1][0] is '-' and not line.split('low')[2].split('"')[1][0] is '0':
						self.lowtemp1['Lowtemp1'] = '+' + line.split('low')[2].split('"')[1]
					else:
						self.lowtemp1['Lowtemp1'] = line.split('low')[2].split('"')[1]
					if not line.split('high')[2].split('"')[1][0] is '-' and not line.split('high')[2].split('"')[1][0] is '0':
						self.hightemp1['Hightemp1'] = '+' + line.split('high')[2].split('"')[1]
					else:
						self.hightemp1['Hightemp1'] = line.split('high')[2].split('"')[1]
					self.pic1['Pic1'] = line.split('skycodeday')[2].split('"')[1]
					self.date1['Date1'] = line.split('date')[3].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[3].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[3].split('"')[1].split('-')[0].strip()
					self.day1['Day1'] = line.split(' day')[3].split('"')[1]
					self.skytext1['Skytext1'] = line.split('skytextday')[2].split('"')[1]
					self.precip1['Precip1'] = line.split('precip')[2].split('"')[1]
#	day 2	#
				if "<forecast" in line:
					if not line.split('low')[3].split('"')[1][0] is '-' and not line.split('low')[3].split('"')[1][0] is '0':
						self.lowtemp2['Lowtemp2'] = '+' + line.split('low')[3].split('"')[1]
					else:
						self.lowtemp2['Lowtemp2'] = line.split('low')[3].split('"')[1]
					if not line.split('high')[3].split('"')[1][0] is '-' and not line.split('high')[3].split('"')[1][0] is '0':
						self.hightemp2['Hightemp2'] = '+' + line.split('high')[3].split('"')[1]
					else:
						self.hightemp2['Hightemp2'] = line.split('high')[3].split('"')[1]
					self.pic2['Pic2'] = line.split('skycodeday')[3].split('"')[1]
					self.date2['Date2'] = line.split('date')[4].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[4].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[4].split('"')[1].split('-')[0].strip()
					self.day2['Day2'] = line.split(' day')[4].split('"')[1]
					self.skytext2['Skytext2'] = line.split('skytextday')[3].split('"')[1]
					self.precip2['Precip2'] = line.split('precip')[3].split('"')[1]
#	day 3	#
				if "<forecast" in line:
					if not line.split('low')[4].split('"')[1][0] is '-' and not line.split('low')[4].split('"')[1][0] is '0':
						self.lowtemp3['Lowtemp3'] = '+' + line.split('low')[4].split('"')[1]
					else:
						self.lowtemp3['Lowtemp3'] = line.split('low')[4].split('"')[1]
					if not line.split('high')[4].split('"')[1][0] is '-' and not line.split('high')[4].split('"')[1][0] is '0':
						self.hightemp3['Hightemp3'] = '+' + line.split('high')[4].split('"')[1]
					else:
						self.hightemp3['Hightemp3'] = line.split('high')[4].split('"')[1]
					self.pic3['Pic3'] = line.split('skycodeday')[4].split('"')[1]
					self.date3['Date3'] = line.split('date')[5].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[5].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[5].split('"')[1].split('-')[0].strip()
					self.day3['Day3'] = line.split(' day')[5].split('"')[1]
					self.skytext3['Skytext3'] = line.split('skytextday')[4].split('"')[1]
					self.precip3['Precip3'] = line.split('precip')[4].split('"')[1]
#	day 4	#
				if "<forecast" in line:
					if not line.split('low')[5].split('"')[1][0] is '-' and not line.split('low')[5].split('"')[1][0] is '0':
						self.lowtemp4['Lowtemp4'] = '+' + line.split('low')[5].split('"')[1]
					else:
						self.lowtemp4['Lowtemp4'] = line.split('low')[5].split('"')[1]
					if not line.split('high')[5].split('"')[1][0] is '-' and not line.split('high')[5].split('"')[1][0] is '0':
						self.hightemp4['Hightemp4'] = '+' + line.split('high')[5].split('"')[1]
					else:
						self.hightemp4['Hightemp4'] = line.split('high')[5].split('"')[1]
					self.pic4['Pic4'] = line.split('skycodeday')[5].split('"')[1]
					self.date4['Date4'] = line.split('date')[6].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[6].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[6].split('"')[1].split('-')[0].strip()
					self.day4['Day4'] = line.split(' day')[6].split('"')[1]
					self.skytext4['Skytext4'] = line.split('skytextday')[5].split('"')[1]
					self.precip4['Precip4'] = line.split('precip')[5].split('"')[1]
			except:
				pass
		defpic = "%sExtensions/OPWeather/iconmeteo/na.png" % resolveFilename(SCOPE_PLUGINS)
		if self.location['Location'] is not '':
			self["location"].text = _('%s') % self.location['Location']
		else:
			self["location"].text = _('n/a')
			self.notdata = True
		if self.timezone['Timezone'] is not '':
			self["timezone"].text = _('%s h') % self.timezone['Timezone']
		else:
			self["timezone"].text = _('n/a')
			self.notdata = True
		if self.latitude['Latitude'] is not '':
			self["latitude"].text = _('%s') % self.latitude['Latitude']
		else:
			self["latitude"].text = _('n/a')
			self.notdata = True
		if self.longitude['Longitude'] is not '':
			self["longitude"].text = _('%s') % self.longitude['Longitude']
		else:
			self["longitude"].text = _('n/a')
			self.notdata = True
		if self.observationtime['Time'] is not '':
			self["observationtime"].text = _('%s') % self.observationtime['Time']
		else:
			self["observationtime"].text = _('n/a')
			self.notdata = True
		if self.observationpoint['Point'] is not '':
			self["observationpoint"].text = _('%s') % self.observationpoint['Point']
		else:
			self["observationpoint"].text = _('n/a')
			self.notdata = True
			
		if self.attribution['Attribution'] is not '':
			self["attribution"].text = _('%s') % self.attribution['Attribution']
		else:
			self["attribution"].text = _('n/a')
			self.notdata = True
		if self.temperature['Temperature'] is not '':
			self["temperature"].text = _('%s%s%s') % (self.temperature['Temperature'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature"].text = _('n/a')
			self.notdata = True
		if self.feelslike['Feelslike'] is not '':
			self["feelslike"].text = _('%s%s%s') % (self.feelslike['Feelslike'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["feelslike"].text = _('n/a')
			self.notdata = True
		if self.skytext['Skytext'] is not '':
			self["skytext"].text = _('%s') % self.skytext['Skytext']
		else:
			self["skytext"].text = _('n/a')
			self.notdata = True
		if self.humidity['Humidity'] is not '':
			self["humidity"].text = _('%s %s') % (self.humidity['Humidity'], unichr(37).encode("latin-1"))
		else:
			self["humidity"].text = _('n/a')
			self.notdata = True
                if self.winddisplay['Wind'] is not '':
			self["winddisplay"].text = _('%s') % self.winddisplay['Wind']
		else:
			self["winddisplay"].text = _('n/a')
			self.notdata = True
		self["pic"].instance.setScale(1)
		if self.pic['Pic'] is not '':
			self["pic"].instance.setPixmapFromFile("%sExtensions/OPWeather/iconmeteo/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic['Pic']))
		else:
			self["pic"].instance.setPixmapFromFile(defpic)
		self["pic"].instance.show()

		if self.lowtemp0['Lowtemp0'] is not '' and self.hightemp0['Hightemp0'] is not '':
			self["temperature0"].text = _('%s%s%s / %s%s%s') % (self.hightemp0['Hightemp0'], unichr(176).encode("latin-1"), self.degreetype, self.lowtemp0['Lowtemp0'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature0"].text = _('n/a')
			self.notdata = True
		if self.skytext0['Skytext0'] is not '':
			self["skytext0"].text = _('%s') % self.skytext0['Skytext0']
		else:
			self["skytext0"].text = _('n/a')
			self.notdata = True
		if self.precip0['Precip0'] is not '':
			self["precip0"].text = _('%s %s') % (self.precip0['Precip0'], unichr(37).encode("latin-1"))
		else:
			self["precip0"].text = _('n/a')
			self.notdata = True
		if self.date0['Date0'] is not '':
			self["date0"].text = _('%s') % self.date0['Date0']
		else:
			self["date0"].text = _('n/a')
			self.notdata = True
		if self.day0['Day0'] is not '':
			self["day0"].text = _('%s') % self.day0['Day0']
		else:
			self["day0"].text = _('n/a')
			self.notdata = True
		self["pic0"].instance.setScale(1)
		if self.pic0['Pic0'] is not '':
			self["pic0"].instance.setPixmapFromFile("%sExtensions/OPWeather/iconmeteo/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic0['Pic0']))
		else:
			self["pic0"].instance.setPixmapFromFile(defpic)
		self["pic0"].instance.show()

		if self.lowtemp1['Lowtemp1'] is not '' and self.hightemp1['Hightemp1'] is not '':
			self["temperature1"].text = _('%s%s%s / %s%s%s') % (self.hightemp1['Hightemp1'], unichr(176).encode("latin-1"), self.degreetype, self.lowtemp1['Lowtemp1'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature1"].text = _('n/a')
			self.notdata = True
		if self.skytext1['Skytext1'] is not '':
			self["skytext1"].text = _('%s') % self.skytext1['Skytext1']
		else:
			self["skytext1"].text = _('n/a')
			self.notdata = True
		if self.precip1['Precip1'] is not '':
			self["precip1"].text = _('%s %s') % (self.precip1['Precip1'], unichr(37).encode("latin-1"))
		else:
			self["precip1"].text = _('n/a')
			self.notdata = True
		if self.date1['Date1'] is not '':
			self["date1"].text = _('%s') % self.date1['Date1']
		else:
			self["date1"].text = _('n/a')
			self.notdata = True
		if self.day1['Day1'] is not '':
			self["day1"].text = _('%s') % self.day1['Day1']
		else:
			self["day1"].text = _('n/a')
			self.notdata = True
		self["pic1"].instance.setScale(1)
		if self.pic1['Pic1'] is not '':
			self["pic1"].instance.setPixmapFromFile("%sExtensions/OPWeather/iconmeteo/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic1['Pic1']))
		else:
			self["pic1"].instance.setPixmapFromFile(defpic)
		self["pic1"].instance.show()

		if self.lowtemp2['Lowtemp2'] is not '' and self.hightemp2['Hightemp2'] is not '':
			self["temperature2"].text = _('%s%s%s / %s%s%s') % (self.hightemp2['Hightemp2'], unichr(176).encode("latin-1"), self.degreetype, self.lowtemp2['Lowtemp2'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature2"].text = _('n/a')
			self.notdata = True
		if self.skytext2['Skytext2'] is not '':
			self["skytext2"].text = _('%s') % self.skytext2['Skytext2']
		else:
			self["skytext2"].text = _('n/a')
			self.notdata = True
		if self.precip2['Precip2'] is not '':
			self["precip2"].text = _('%s %s') % (self.precip2['Precip2'], unichr(37).encode("latin-1"))
		else:
			self["precip2"].text = _('n/a')
			self.notdata = True
		if self.date2['Date2'] is not '':
			self["date2"].text = _('%s') % self.date2['Date2']
		else:
			self["date2"].text = _('n/a')
			self.notdata = True
		if self.day2['Day2'] is not '':
			self["day2"].text = _('%s') % self.day2['Day2']
		else:
			self["day2"].text = _('n/a')
			self.notdata = True
		self["pic2"].instance.setScale(1)
		if self.pic2['Pic2'] is not '':
			self["pic2"].instance.setPixmapFromFile("%sExtensions/OPWeather/iconmeteo/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic2['Pic2']))
		else:
			self["pic2"].instance.setPixmapFromFile(defpic)
		self["pic2"].instance.show()

		if self.lowtemp3['Lowtemp3'] is not '' and self.hightemp3['Hightemp3'] is not '':
			self["temperature3"].text = _('%s%s%s / %s%s%s') % (self.hightemp3['Hightemp3'], unichr(176).encode("latin-1"), self.degreetype, self.lowtemp3['Lowtemp3'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature3"].text = _('n/a')
			self.notdata = True
		if self.skytext3['Skytext3'] is not '':
			self["skytext3"].text = _('%s') % self.skytext3['Skytext3']
		else:
			self["skytext3"].text = _('n/a')
			self.notdata = True
		if self.precip3['Precip3'] is not '':
			self["precip3"].text = _('%s %s') % (self.precip3['Precip3'], unichr(37).encode("latin-1"))
		else:
			self["precip3"].text = _('n/a')
			self.notdata = True
		if self.date3['Date3'] is not '':
			self["date3"].text = _('%s') % self.date3['Date3']
		else:
			self["date3"].text = _('n/a')
			self.notdata = True
		if self.day3['Day3'] is not '':
			self["day3"].text = _('%s') % self.day3['Day3']
		else:
			self["day3"].text = _('n/a')
			self.notdata = True
		self["pic3"].instance.setScale(1)
		if self.pic3['Pic3'] is not '':
			self["pic3"].instance.setPixmapFromFile("%sExtensions/OPWeather/iconmeteo/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic3['Pic3']))
		else:
			self["pic3"].instance.setPixmapFromFile(defpic)
		self["pic3"].instance.show()

		if self.lowtemp4['Lowtemp4'] is not '' and self.hightemp4['Hightemp4'] is not '':
			self["temperature4"].text = _('%s%s%s / %s%s%s') % (self.hightemp4['Hightemp4'], unichr(176).encode("latin-1"), self.degreetype, self.lowtemp4['Lowtemp4'], unichr(176).encode("latin-1"), self.degreetype)
		else:
			self["temperature4"].text = _('n/a')
			self.notdata = True
		if self.skytext4['Skytext4'] is not '':
			self["skytext4"].text = _('%s') % self.skytext4['Skytext4']
		else:
			self["skytext4"].text = _('n/a')
			self.notdata = True
		if self.precip4['Precip4'] is not '':
			self["precip4"].text = _('%s %s') % (self.precip4['Precip4'], unichr(37).encode("latin-1"))
		else:
			self["precip4"].text = _('n/a')
			self.notdata = True
		if self.date4['Date4'] is not '':
			self["date4"].text = _('%s') % self.date4['Date4']
		else:
			self["date4"].text = _('n/a')
			self.notdata = True
		if self.day4['Day4'] is not '':
			self["day4"].text = _('%s') % self.day4['Day4']
		else:
			self["day4"].text = _('n/a')
			self.notdata = True
		self["pic4"].instance.setScale(1)
		if self.pic4['Pic4'] is not '':
			self["pic4"].instance.setPixmapFromFile("%sExtensions/OPWeather/iconmeteo/%s.png" % (resolveFilename(SCOPE_PLUGINS), self.pic4['Pic4']))
		else:
			self["pic4"].instance.setPixmapFromFile(defpic)
		self["pic4"].instance.show()

	def config (self):
		self.session.open(ConfigWeatherfor)


	def exit(self):
		os.system("rm -f /tmp/weatherfore.xml")
		self.close()

        def openVirtualKeyBoard(self):
		self.session.openWithCallback(self.ShowsearchBarracuda, VirtualKeyBoard, title=_('Enter text to search city'))

	def ShowsearchBarracuda(self, name):
		if name is not None:
			self.session.open(SearchLocationFOR, name)

class ConfigWeatherfor(ConfigListScreen, Screen):
	def __init__(self, session):
                skin = "/usr/lib/enigma2/python/Plugins/Extensions/OPWeather/Skin/Weatherconf.xml"
                if os.path.exists(skin):  
                    f = open(skin, "r")
                    self.skin = f.read()
                    f.close()			
		Screen.__init__(self, session)
		self.session = session
		self.skinName = ["Weatherconf"]
		self.list = []

		ConfigListScreen.__init__(self, self.list, session = session)

                self['titleheader'] = Label(_('Config Weather Foreca'))
		self.city = config.plugins.weatherfor.city.value
		self.language = config.osd.language.value.replace('_', '-')
		if self.language == 'en-EN':
			self.language = 'en-US'
		self.degreetype = config.plugins.weatherfor.degreetype.value
		self.createSetup()

		self["setupActions"] = ActionMap(["DirectionActions", "SetupActions", "ColorActions"], 
		{ "red": self.cancel,
		"cancel": self.cancel,
		"green": self.save,
		"ok": self.save
		}, -2)

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))

	
	def createSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Scale of temperature:"), config.plugins.weatherfor.degreetype))
		self["config"].list = self.list
		self["config"].l.setList(self.list)


	def cancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close(False)

	def save(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		self.mbox = self.session.open(MessageBox,(_("Configuration is saved")), MessageBox.TYPE_INFO, timeout = 3 )
		self.close()

class SearchLocationFOR(Screen):
	def __init__(self, session, name):
                skin = "/usr/lib/enigma2/python/Plugins/Extensions/OPWeather/Skin/Weatherlistf.xml"
                if os.path.exists(skin):  
                    f = open(skin, "r")
                    self.skin = f.read()
                    f.close()
		Screen.__init__(self, session)
		self.session = session
		self.skinName = ["SearchLocationfore"]
		self.eventname = name
		self.resultlist = []
		self["menu"] = MenuList(self.resultlist)
                self["key_red"] = Label(_("Cancel"))
                self["key_green"] = Label(_("Save"))
                self['titleheader'] = Label(_('OpenPlus! Weather'))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], 
		{"ok": self.okClicked,
                "green": self.okClicked,
		"cancel": self.close,
                "red": self.close,
		"up": self.pageUp,
		"down": self.pageDown
		}, -1)

		self.showMenu()

	def pageUp(self):
		self['menu'].instance.moveSelection(self['menu'].instance.moveUp)

	def pageDown(self):
		self['menu'].instance.moveSelection(self['menu'].instance.moveDown)

	def showMenu(self):
		try:
			results = search_title(self.eventname)
		except:
			results = []

		if len(results) == 0:
			return False
		self.resultlist = []
		for searchResult in results:
			try:
				self.resultlist.append(searchResult)
			except:
				pass
		self['menu'].l.setList(self.resultlist)

	def okClicked(self):
		id = self['menu'].getCurrent()
		if id:
			config.plugins.weatherfor.city.value = id.replace(' ', '%20')
			config.plugins.weatherfor.city.save()
                        self.close()

def search_title(id):
	url = 'http://weather.service.msn.com/find.aspx?outputview=search&weasearchstr=%s&culture=es-ES&src=outlook' % id.replace(' ', '%20')
	watchrequest = Request(url)
	try:
		watchvideopage = urlopen(watchrequest)
	except (URLError, HTTPException, socket.error) as err:
		print '[Location] Error: Unable to retrieve page - Error code: ', str(err)
	content = watchvideopage.read()
	root = cet_fromstring(content)
	search_results = []
	if content:
		for childs in root:
			if childs.tag == 'weather':
				locationcode = childs.attrib.get('weatherlocationname').encode('utf-8', 'ignore')
				search_results.append(locationcode)
	return search_results




