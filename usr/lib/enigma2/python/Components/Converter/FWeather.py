# -*- coding: UTF-8 -*-
#
# Converter - OpenWeather
# Mod by iqas & Villak for Openplus
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
from Tools.Directories import fileExists, pathExists
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config, configfile
from Components.Console import Console as iConsole
from Components.Language import language
from os import environ
from Poll import Poll
import gettext
import time
import os

weather_city = config.plugins.weatherfor.city.value
degreetype = config.plugins.weatherfor.degreetype.value
weather_location = config.osd.language.value.replace('_', '-')

if weather_location == 'en-EN':
	weather_location = 'en-US'

time_update = 20
time_update_ms = 3000

class FWeather(Poll, Converter, object):

	VFD = 1
	DATE = 2
	SHORTDATE = 3
	DAY = 4
	SHORTDAY = 5
	LOCATION = 6
	TIMEZONE = 7
	LATITUDE = 8
	LONGITUDE = 9
	TEMP = 10
	PICON = 11
	SKYTEXT = 12
	FEELSLIKE = 13
	HUMIDITY = 14
	WINDDISPLAY = 15
	DATE0 = 20
	SHORTDATE0 = 21
	DAY0 = 22
	SHORTDAY0 = 23
	TEMP0 = 24
	LOWTEMP0 = 25
	HIGHTEMP0 = 26
	PICON0 = 27
	SKYTEXT0 = 28
	PRECIP0 = 29
	DATE1 = 30
	SHORTDATE1 = 31
	DAY1 = 32
	SHORTDAY1 = 33
	TEMP1 = 34
	LOWTEMP1 = 35
	HIGHTEMP1 = 36
	PICON1 = 37
	SKYTEXT1 = 38
	PRECIP1 = 39
	DATE2 = 40
	SHORTDATE2 = 41
	DAY2 = 42
	SHORTDAY2 = 43
	TEMP2 = 44
	LOWTEMP2 = 45
	HIGHTEMP2 = 46
	PICON2 = 47
	SKYTEXT2 = 48
	PRECIP2 = 49
	DATE3 = 50
	SHORTDATE3 = 51
	DAY3 = 52
	SHORTDAY3 = 53
	TEMP3 = 54
	LOWTEMP3 = 55
	HIGHTEMP3 = 56
	PICON3 = 57
	SKYTEXT3 = 58
	PRECIP3 = 59
	DATE4 = 60
	SHORTDATE4 = 61
	DAY4 = 62
	SHORTDAY4 = 63
	TEMP4 = 64
	LOWTEMP4 = 65
	HIGHTEMP4 = 66
	PICON4 = 67
	SKYTEXT4 = 68
	PRECIP4 = 69

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		if type == "Vfd":
			self.type = self.VFD
		elif type == "Date":
			self.type = self.DATE
		elif type == "Shortdate":
			self.type = self.SHORTDATE
		elif type == "Day":
			self.type = self.DAY
		elif type == "Shortday":
			self.type = self.SHORTDAY
		elif type == "Location":
			self.type = self.LOCATION
		elif type == "Timezone":
			self.type = self.TIMEZONE
		elif type == "Latitude":
			self.type = self.LATITUDE
		elif type == "Longitude":
			self.type = self.LONGITUDE
		elif type == "Temp":
			self.type = self.TEMP
		elif type == "Picon":
			self.type = self.PICON
		elif type == "Skytext":
			self.type = self.SKYTEXT
		elif type == "Feelslike":
			self.type = self.FEELSLIKE
		elif type == "Humidity":
			self.type = self.HUMIDITY
                elif type == "Winddisplay":
			self.type = self.WINDDISPLAY

#	today	#
		elif type == "Date0":
			self.type = self.DATE0
		elif type == "Shortdate0":
			self.type = self.SHORTDATE0
		elif type == "Day0":
			self.type = self.DAY0
		elif type == "Shortday0":
			self.type = self.SHORTDAY0
		elif type == "Temp0":
			self.type = self.TEMP0
		elif type == "Lowtemp0":
			self.type = self.LOWTEMP0
		elif type == "Hightemp0":
			self.type = self.HIGHTEMP0
		elif type == "Picon0":
			self.type = self.PICON0
		elif type == "Skytext0":
			self.type = self.SKYTEXT0
		elif type == "Precip0":
			self.type = self.PRECIP0
#	day 1	#
		elif type == "Date1":
			self.type = self.DATE1
		elif type == "Shortdate1":
			self.type = self.SHORTDATE1
		elif type == "Day1":
			self.type = self.DAY1
		elif type == "Shortday1":
			self.type = self.SHORTDAY1
		elif type == "Temp1":
			self.type = self.TEMP1
		elif type == "Lowtemp1":
			self.type = self.LOWTEMP1
		elif type == "Hightemp1":
			self.type = self.HIGHTEMP1
		elif type == "Picon1":
			self.type = self.PICON1
		elif type == "Skytext1":
			self.type = self.SKYTEXT1
		elif type == "Precip1":
			self.type = self.PRECIP1
#	day 2	#
		elif type == "Date2":
			self.type = self.DATE2
		elif type == "Shortdate2":
			self.type = self.SHORTDATE2
		elif type == "Day2":
			self.type = self.DAY2
		elif type == "Shortday2":
			self.type = self.SHORTDAY2
		elif type == "Temp2":
			self.type = self.TEMP2
		elif type == "Lowtemp2":
			self.type = self.LOWTEMP2
		elif type == "Hightemp2":
			self.type = self.HIGHTEMP2
		elif type == "Picon2":
			self.type = self.PICON2
		elif type == "Skytext2":
			self.type = self.SKYTEXT2
		elif type == "Precip2":
			self.type = self.PRECIP2
#	day 3	#
		elif type == "Date3":
			self.type = self.DATE3
		elif type == "Shortdate3":
			self.type = self.SHORTDATE3
		elif type == "Day3":
			self.type = self.DAY3
		elif type == "Shortday3":
			self.type = self.SHORTDAY3
		elif type == "Temp3":
			self.type = self.TEMP3
		elif type == "Lowtemp3":
			self.type = self.LOWTEMP3
		elif type == "Hightemp3":
			self.type = self.HIGHTEMP3
		elif type == "Picon3":
			self.type = self.PICON3
		elif type == "Skytext3":
			self.type = self.SKYTEXT3
		elif type == "Precip3":
			self.type = self.PRECIP3
#	day 4	#
		elif type == "Date4":
			self.type = self.DATE4
		elif type == "Shortdate4":
			self.type = self.SHORTDATE4
		elif type == "Day4":
			self.type = self.DAY4
		elif type == "Shortday4":
			self.type = self.SHORTDAY4
		elif type == "Temp4":
			self.type = self.TEMP4
		elif type == "Lowtemp4":
			self.type = self.LOWTEMP4
		elif type == "Hightemp4":
			self.type = self.HIGHTEMP4
		elif type == "Picon4":
			self.type = self.PICON4
		elif type == "Skytext4":
			self.type = self.SKYTEXT4
		elif type == "Precip4":
			self.type = self.PRECIP4

		self.iConsole = iConsole()
		self.poll_interval = time_update_ms
		self.poll_enabled = True

	def control_xml(self, result, retval, extra_args):
		if retval is not 0:
			self.write_none()

	def write_none(self):
		with open("/tmp/weatherfore.xml", "w") as noneweather:
			noneweather.write("None")
		noneweather.close()

	def get_xmlfile(self):
		self.iConsole.ePopen("wget -P /tmp -T2 'http://weather.service.msn.com/data.aspx?weadegreetype=%s&culture=%s&weasearchstr=%s&src=outlook' -O /tmp/weatherfore.xml" % (degreetype, weather_location, weather_city), self.control_xml)

	@cached
	def getText(self):
		info, weze = 'n/a', ''
		foreweather = {'Vfd':'', 'Date':'', 'Shortdate':'', 'Day':'', 'Shortday':'',\
			'Location':'', 'Timezone':'', 'Latitude':'', 'Longitude':'',\
			'Temp':'', 'Picon':'', 'Skytext':'', 'Feelslike':'', 'Humidity':'', 'Winddisplay':'', 'Wind':'',\
			'Date0':'', 'Shortdate0':'', 'Day0':'', 'Shortday0':'', 'Temp0':'', 'Lowtemp0':'', 'Hightemp0':'', 'Picon0':'', 'Skytext0':'', 'Precip0':'',\
			'Date1':'', 'Shortdate1':'', 'Day1':'', 'Shortday1':'', 'Temp1':'', 'Lowtemp1':'', 'Hightemp1':'', 'Picon1':'', 'Skytext1':'', 'Precip1':'',\
			'Date2':'', 'Shortdate2':'', 'Day2':'', 'Shortday2':'', 'Temp2':'', 'Lowtemp2':'', 'Hightemp2':'', 'Picon2':'', 'Skytext2':'', 'Precip2':'',\
			'Date3':'', 'Shortdate3':'', 'Day3':'', 'Shortday3':'', 'Temp3':'', 'Lowtemp3':'', 'Hightemp3':'', 'Picon3':'', 'Skytext3':'', 'Precip3':'',\
			'Date4':'', 'Shortdate4':'', 'Day4':'', 'Shortday4':'', 'Temp4':'', 'Lowtemp4':'', 'Hightemp4':'', 'Picon4':'', 'Skytext4':'', 'Precip4':'',\
			}
		low0weather, hi0weather, low1weather, hi1weather, low2weather, hi2weather, low3weather, hi3weather, low4weather, hi4weather = '', '', '', '', '', '', '', '', '', ''
		if fileExists("/tmp/weatherfore.xml"):
			if int((time.time() - os.stat("/tmp/weatherfore.xml").st_mtime)/60) >= time_update:
				self.get_xmlfile()
		else:
			self.get_xmlfile()
		if not fileExists("/tmp/weatherfore.xml"):
			self.write_none()
			return info
		if fileExists("/tmp/weatherfore.xml") and open("/tmp/weatherfore.xml").read() is 'None':
			return info
		for line in open("/tmp/weatherfore.xml"):
			try:
				if "<weather" in line:
					foreweather['Location'] = line.split('weatherlocationname')[1].split('"')[1].split(',')[0]
					if not line.split('timezone')[1].split('"')[1][0] is '0':
						foreweather['Timezone'] = '+' + line.split('timezone')[1].split('"')[1] + ' h'
					else:
						foreweather['Timezone'] = line.split('timezone')[1].split('"')[1] + ' h'
					foreweather['Latitude'] = line.split(' lat')[1].split('"')[1]
					foreweather['Longitude'] = line.split(' long')[1].split('"')[1]
				if "<current" in line:
					if not line.split('temperature')[1].split('"')[1][0] is '-' and not line.split('temperature')[1].split('"')[1][0] is '0':
						foreweather['Temp'] = '+' + line.split('temperature')[1].split('"')[1] + '%s%s' % (unichr(176).encode("latin-1"), degreetype)
					else:
						foreweather['Temp'] = line.split('temperature')[1].split('"')[1] + '%s%s' % (unichr(176).encode("latin-1"), degreetype)
					if not line.split('feelslike')[1].split('"')[1][0] is '-' and not line.split('feelslike')[1].split('"')[1][0] is '0':
						foreweather['Feelslike'] = '+' + line.split('feelslike')[1].split('"')[1] + '%s%s' % (unichr(176).encode("latin-1"), degreetype)
					else:
						foreweather['Feelslike'] = line.split('feelslike')[1].split('"')[1] + '%s%s' % (unichr(176).encode("latin-1"), degreetype)
					foreweather['Picon'] = line.split('skycode')[1].split('"')[1]
					foreweather['Skytext'] = line.split('skytext')[1].split('"')[1]
					foreweather['Humidity'] = line.split('humidity')[1].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
                                        foreweather['Winddisplay'] = line.split('winddisplay')[1].split('"')[1]
					foreweather['Date'] = line.split('date')[1].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[1].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[1].split('"')[1].split('-')[0].strip()
					foreweather['Shortdate'] = line.split('shortday')[1].split('"')[1] + ' ' + line.split('date')[1].split('"')[1].split('-')[2].strip()
					foreweather['Day'] = line.split(' day')[1].split('"')[1]
					foreweather['Shortday'] = line.split('shortday')[1].split('"')[1]
#	today	#
				if "<forecast" in line:
					if not line.split('low')[1].split('"')[1][0] is '-' and not line.split('low')[1].split('"')[1][0] is '0':
						low0weather = '+' + line.split('low')[1].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Lowtemp0'] = '%s%s' % (low0weather, degreetype)
					else:
						low0weather = line.split('low')[1].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Lowtemp0'] = '%s%s' % (low0weather, degreetype)
					if not line.split('high')[1].split('"')[1][0] is '-' and not line.split('high')[1].split('"')[1][0] is '0':
						hi0weather = '+' + line.split('high')[1].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Hightemp0'] = '%s%s' % (hi0weather, degreetype)
					else:
						hi0weather = line.split('high')[1].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Hightemp0'] = '%s%s' % (hi0weather, degreetype)
					foreweather['Temp0'] =  '%s / %s' % (hi0weather, low0weather)
					foreweather['Picon0'] = line.split('skycodeday')[1].split('"')[1]
					foreweather['Date0'] = line.split('date')[2].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[2].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[2].split('"')[1].split('-')[0].strip()
					foreweather['Shortdate0'] = line.split('shortday')[2].split('"')[1] + ' ' + line.split('date')[2].split('"')[1].split('-')[2].strip()
					foreweather['Day0'] = line.split(' day')[2].split('"')[1]
					foreweather['Shortday0'] = line.split('shortday')[2].split('"')[1]
					foreweather['Skytext0'] = line.split('skytextday')[1].split('"')[1]
					foreweather['Precip0'] = line.split('precip')[1].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
#	day 1	#
				if "<forecast" in line:
					if not line.split('low')[2].split('"')[1][0] is '-' and not line.split('low')[2].split('"')[1][0] is '0':
						low1weather = '+' + line.split('low')[2].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Lowtemp1'] = '%s%s' % (low1weather, degreetype)
					else:
						low1weather = line.split('low')[2].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Lowtemp1'] = '%s%s' % (low1weather, degreetype)
					if not line.split('high')[2].split('"')[1][0] is '-' and not line.split('high')[2].split('"')[1][0] is '0':
						hi1weather = '+' + line.split('high')[2].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Hightemp1'] = '%s%s' % (hi1weather, degreetype)
					else:
						hi1weather = line.split('high')[2].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Hightemp1'] = '%s%s' % (hi1weather, degreetype)
					foreweather['Temp1'] =  '%s / %s' % (hi1weather, low1weather)
					foreweather['Picon1'] = line.split('skycodeday')[2].split('"')[1]
					foreweather['Date1'] = line.split('date')[3].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[3].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[3].split('"')[1].split('-')[0].strip()
					foreweather['Shortdate1'] = line.split('shortday')[3].split('"')[1] + ' ' + line.split('date')[3].split('"')[1].split('-')[2].strip()
					foreweather['Day1'] = line.split(' day')[3].split('"')[1]
					foreweather['Shortday1'] = line.split('shortday')[3].split('"')[1]
					foreweather['Skytext1'] = line.split('skytextday')[2].split('"')[1]
					foreweather['Precip1'] = line.split('precip')[2].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
#	day 2	#
				if "<forecast" in line:
					if not line.split('low')[3].split('"')[1][0] is '-' and not line.split('low')[3].split('"')[1][0] is '0':
						low2weather = '+' + line.split('low')[3].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Lowtemp2'] = '%s%s' % (low2weather, degreetype)
					else:
						low2weather = line.split('low')[3].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Lowtemp2'] = '%s%s' % (low2weather, degreetype)
					if not line.split('high')[3].split('"')[1][0] is '-' and not line.split('high')[3].split('"')[1][0] is '0':
						hi2weather = '+' + line.split('high')[3].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Hightemp2'] = '%s%s' % (hi2weather, degreetype)
					else:
						hi2weather = line.split('high')[3].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Hightemp2'] = '%s%s' % (hi2weather, degreetype)
					foreweather['Temp2'] =  '%s / %s' % (hi2weather, low2weather)
					foreweather['Picon2'] = line.split('skycodeday')[3].split('"')[1]
					foreweather['Date2'] = line.split('date')[4].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[4].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[4].split('"')[1].split('-')[0].strip()
					foreweather['Shortdate2'] = line.split('shortday')[4].split('"')[1] + ' ' + line.split('date')[4].split('"')[1].split('-')[2].strip()
					foreweather['Day2'] = line.split(' day')[4].split('"')[1]
					foreweather['Shortday2'] = line.split('shortday')[4].split('"')[1]
					foreweather['Skytext2'] = line.split('skytextday')[3].split('"')[1]
					foreweather['Precip2'] = line.split('precip')[3].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
#	day 3	#
				if "<forecast" in line:
					if not line.split('low')[4].split('"')[1][0] is '-' and not line.split('low')[4].split('"')[1][0] is '0':
						low3weather = '+' + line.split('low')[4].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Lowtemp3'] = '%s%s' % (low3weather, degreetype)
					else:
						low3weather = line.split('low')[4].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Lowtemp3'] = '%s%s' % (low3weather, degreetype)
					if not line.split('high')[4].split('"')[1][0] is '-' and not line.split('high')[4].split('"')[1][0] is '0':
						hi3weather = '+' + line.split('high')[4].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Hightemp3'] = '%s%s' % (hi3weather, degreetype)
					else:
						hi3weather = line.split('high')[4].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Hightemp3'] = '%s%s' % (hi3weather, degreetype)
					foreweather['Temp3'] =  '%s / %s' % (hi3weather, low3weather)
					foreweather['Picon3'] = line.split('skycodeday')[4].split('"')[1]
					foreweather['Date3'] = line.split('date')[5].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[5].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[5].split('"')[1].split('-')[0].strip()
					foreweather['Shortdate3'] = line.split('shortday')[5].split('"')[1] + ' ' + line.split('date')[5].split('"')[1].split('-')[2].strip()
					foreweather['Day3'] = line.split(' day')[5].split('"')[1]
					foreweather['Shortday3'] = line.split('shortday')[5].split('"')[1]
					foreweather['Skytext3'] = line.split('skytextday')[4].split('"')[1]
					foreweather['Precip3'] = line.split('precip')[4].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
#	day 4	#
				if "<forecast" in line:
					if not line.split('low')[5].split('"')[1][0] is '-' and not line.split('low')[5].split('"')[1][0] is '0':
						low4weather = '+' + line.split('low')[5].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Lowtemp4'] = '%s%s' % (low4weather, degreetype)
					else:
						low4weather = line.split('low')[5].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Lowtemp4'] = '%s%s' % (low4weather, degreetype)
					if not line.split('high')[5].split('"')[1][0] is '-' and not line.split('high')[5].split('"')[1][0] is '0':
						hi4weather = '+' + line.split('high')[5].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Hightemp4'] = '%s%s' % (hi4weather, degreetype)
					else:
						hi4weather = line.split('high')[5].split('"')[1] + '%s' % unichr(176).encode("latin-1")
						foreweather['Hightemp4'] = '%s%s' % (hi4weather, degreetype)
					foreweather['Temp4'] =  '%s / %s' % (hi4weather, low4weather)
					foreweather['Picon4'] = line.split('skycodeday')[5].split('"')[1]
					foreweather['Date4'] = line.split('date')[6].split('"')[1].split('-')[2].strip() + '.' + line.split('date')[6].split('"')[1].split('-')[1].strip() + '.' + line.split('date')[6].split('"')[1].split('-')[0].strip()
					foreweather['Shortdate4'] = line.split('shortday')[6].split('"')[1] + ' ' + line.split('date')[6].split('"')[1].split('-')[2].strip()
					foreweather['Day4'] = line.split(' day')[6].split('"')[1]
					foreweather['Shortday4'] = line.split('shortday')[6].split('"')[1]
					foreweather['Skytext4'] = line.split('skytextday')[5].split('"')[1]
					foreweather['Precip4'] = line.split('precip')[5].split('"')[1] + ' %s'  % unichr(37).encode("latin-1")
			except:
				pass
#
		if self.type is self.VFD:
			try:
				weze = foreweather['Skytext'].split(' ')[1]
			except:
				weze = foreweather['Skytext']
			info = foreweather['Temp'] + ' ' + weze
		if self.type is self.DATE:
			info = foreweather['Date']
		if self.type is self.SHORTDATE:
			info = foreweather['Shortdate']
		if self.type is self.DAY:
			info = foreweather['Day']
		if self.type is self.SHORTDAY:
			info = foreweather['Shortday']
		if self.type is self.LOCATION:
			info = foreweather['Location']
		if self.type is self.TIMEZONE:
			info = foreweather['Timezone']
		if self.type is self.LATITUDE:
			info = foreweather['Latitude']
		if self.type is self.LONGITUDE:
			info = foreweather['Longitude']
		if self.type is self.TEMP:
			info = foreweather['Temp']
		if self.type is self.PICON:
			info = foreweather['Picon']
		if self.type is self.SKYTEXT:
			info = foreweather['Skytext']
		if self.type is self.FEELSLIKE:
			info = foreweather['Feelslike']
		if self.type is self.HUMIDITY:
			info = foreweather['Humidity']
                if self.type is self.WINDDISPLAY:
			info = foreweather['Winddisplay']
		
#	today	#
		if self.type is self.DATE0:
			info = foreweather['Date0']
		if self.type is self.SHORTDATE0:
			info = foreweather['Shortdate0']
		if self.type is self.DAY0:
			info = foreweather['Day0']
		if self.type is self.SHORTDAY0:
			info = foreweather['Shortday0']
		if self.type is self.TEMP0:
			info = foreweather['Temp0']
		if self.type is self.LOWTEMP0:
			info = foreweather['Lowtemp0']
		if self.type is self.HIGHTEMP0:
			info = foreweather['Hightemp0']
		if self.type is self.PICON0:
			info = foreweather['Picon0']
		if self.type is self.SKYTEXT0:
			info = foreweather['Skytext0']
		if self.type is self.PRECIP0:
			info = foreweather['Precip0']
#	day 1	#
		if self.type is self.DATE1:
			info = foreweather['Date1']
		if self.type is self.SHORTDATE1:
			info = foreweather['Shortdate1']
		if self.type is self.DAY1:
			info = foreweather['Day1']
		if self.type is self.SHORTDAY1:
			info = foreweather['Shortday1']
		if self.type is self.TEMP1:
			info = foreweather['Temp1']
		if self.type is self.LOWTEMP1:
			info = foreweather['Lowtemp1']
		if self.type is self.HIGHTEMP1:
			info = foreweather['Hightemp1']
		if self.type is self.PICON1:
			info = foreweather['Picon1']
		if self.type is self.SKYTEXT1:
			info = foreweather['Skytext1']
		if self.type is self.PRECIP1:
			info = foreweather['Precip1']
#	day 2	#
		if self.type is self.DATE2:
			info = foreweather['Date2']
		if self.type is self.SHORTDATE2:
			info = foreweather['Shortdate2']
		if self.type is self.DAY2:
			info = foreweather['Day2']
		if self.type is self.SHORTDAY2:
			info = foreweather['Shortday2']
		if self.type is self.TEMP2:
			info = foreweather['Temp2']
		if self.type is self.LOWTEMP2:
			info = foreweather['Lowtemp2']
		if self.type is self.HIGHTEMP2:
			info = foreweather['Hightemp2']
		if self.type is self.PICON2:
			info = foreweather['Picon2']
		if self.type is self.SKYTEXT2:
			info = foreweather['Skytext2']
		if self.type is self.PRECIP2:
			info = foreweather['Precip2']
#	day 3	#
		if self.type is self.DATE3:
			info = foreweather['Date3']
		if self.type is self.SHORTDATE3:
			info = foreweather['Shortdate3']
		if self.type is self.DAY3:
			info = foreweather['Day3']
		if self.type is self.SHORTDAY3:
			info = foreweather['Shortday3']
		if self.type is self.TEMP3:
			info = foreweather['Temp3']
		if self.type is self.LOWTEMP3:
			info = foreweather['Lowtemp3']
		if self.type is self.HIGHTEMP3:
			info = foreweather['Hightemp3']
		if self.type is self.PICON3:
			info = foreweather['Picon3']
		if self.type is self.SKYTEXT3:
			info = foreweather['Skytext3']
		if self.type is self.PRECIP3:
			info = foreweather['Precip3']
#	day 4	#
		if self.type is self.DATE4:
			info = foreweather['Date4']
		if self.type is self.SHORTDATE4:
			info = foreweather['Shortdate4']
		if self.type is self.DAY4:
			info = foreweather['Day4']
		if self.type is self.SHORTDAY4:
			info = foreweather['Shortday4']
		if self.type is self.TEMP4:
			info = foreweather['Temp4']
		if self.type is self.LOWTEMP4:
			info = foreweather['Lowtemp4']
		if self.type is self.HIGHTEMP4:
			info = foreweather['Hightemp4']
		if self.type is self.PICON4:
			info = foreweather['Picon4']
		if self.type is self.SKYTEXT4:
			info = foreweather['Skytext4']
		if self.type is self.PRECIP4:
			info = foreweather['Precip4']
		return info
	text = property(getText)

	def changed(self, what):
		Converter.changed(self, (self.CHANGED_POLL,))
