# OPWeather by Openplus 
# Last modified 28-10-2013
# Coded by Iqas & Villak for OpenPlus 2017

from . import _
from Plugins.Plugin import PluginDescriptor
from boxbranding import getBoxType, getMachineBrand, getMachineName
from Weather import *
from Weatherf import *
from Search_Id import *
from enigma import getDesktop
from Components.Language import language
from Components.MenuList import MenuList
from Screens.Standby import TryQuitMainloop
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigText, ConfigYesNo, ConfigSubsection, ConfigSelection, config, configfile, NoSave
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import gettext
def _(txt):
	t = gettext.dgettext("OPWeather", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

    
config.plugins.weatherconf = ConfigSubsection()
config.plugins.weatherconf.datafrom = ConfigSelection(default="F", choices = [
	("Y", _("Yahoo")),
	("F", _("Foreca"))])

class ConfigWeatherMenu(ConfigListScreen, Screen):
	def __init__(self, session):
                skin = "/usr/lib/enigma2/python/Plugins/Extensions/OPWeather/Skin/WeatherconfGen.xml"
                if os.path.exists(skin):  
                    f = open(skin, "r")
                    self.skin = f.read()
                    f.close()			
		Screen.__init__(self, session)
		self.session = session
		self.skinName = ["Weatherconfmenu"]
		self.list = []
                
                ConfigListScreen.__init__(self, self.list, session = session)
                
                self['titleheader'] = Label(_('Config Weather OpenPlus'))
                self.degreetype = config.plugins.weatherconf.datafrom.value
		self.createSetup()
                
                
		self["setupActions"] = ActionMap(["DirectionActions", "SetupActions", "ColorActions"], 
		{ "red": self.cancel,
		"cancel": self.cancel,
		"green": self.save,
                "yellow": self.foreca,
                "blue": self.yahoo,
		"ok": self.save
		}, -2)

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
                self["key_yellow"] = StaticText(_("Weather Foreca"))
		self["key_blue"] = StaticText(_("Weather Yahoo"))

	def foreca(self):
                self.session.open(Weatherfor)
            
        def yahoo(self):
                self.session.open(MeteoMain)
                   
	def createSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("The Weather in Menu by:"), config.plugins.weatherconf.datafrom))
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
                self.session.openWithCallback(self.Restartbox,MessageBox,_('Restart your %s %s to apply service settings\nRestart now?') % (getMachineBrand(), getMachineName()), MessageBox.TYPE_YESNO)
               
               
	def Restartbox(self, val):
		if val:
			self.session.open(TryQuitMainloop, 2)
		else:
			
			self.close()        

def main(session, **kwargs):
	session.open(ConfigWeatherMenu)
        
def mainy(session,**kwargs):
	session.open(MeteoMain)
        
def mainf(session,**kwargs):
	session.open(Weatherfor)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("OpenWeather"), main, "openweather", 7)]
	return []
        
def Weathery(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("OpenWeather"), mainy, "openweather", 7)]
	return []

        
def Weatherf(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("OpenWeather"), mainf, "openweather", 7)]
	return []

        
def Plugins(**kwargs):
	if config.plugins.weatherconf.datafrom.value == 'Y':
		result = [
		PluginDescriptor(name=_("OpenWeather"),
		where=PluginDescriptor.WHERE_MENU,
		fnc=Weathery),
		PluginDescriptor(name=_("OpenWeather"),
		description=_("Your city weather for Openplus!"),
		where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
		icon="openywhd.png",
		fnc=main)
		]
		return result
	else:
		result = [
                PluginDescriptor(name=_("OpenWeather"),
		where=PluginDescriptor.WHERE_MENU,
		fnc=Weatherf),
		PluginDescriptor(name=_("OpenWeather"),
		description=_("Your city weather for Openplus!"),
		where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
		icon="openywhd.png",
		fnc=main)
		]
		return result
