# CloudBot

## About

CloudBot is a Python IRC bot based on [Skybot](http://git.io/skybot) by [rmmh](http://git.io/rmmh).

## Getting and using CloudBot

### Download 

Get CloudBot at [https://github.com/ClouDev/CloudBot/zipball/develop](https://github.com/ClouDev/CloudBot/zipball/develop "Get CloudBot from Github!").

Unzip the resulting file, and continue to read this document.

### Install

Before you can run the bot, you need to install a few Python dependencies. LXML is required while Enchant and PyDNS are needed for several plugins.


These can be installed with `pip` (The Python package manager):

    [sudo] pip install -r requirements.txt
    
If you use `pip`, you will also need the following packages on linux or `pip` will fail to install the requirements.
   ```python, python-dev, libenchant-dev, libenchant1c2a, libxslt-dev, libxml2-dev.```

#### How to install `pip`

    curl -O http://python-distribute.org/distribute_setup.py # or download with your browser on windows
    python distribute_setup.py
    easy_install pip
    
If you are unable to use pip, there are Windows installers for LXML available for [64 bit](https://pypi.python.org/packages/2.7/l/lxml/lxml-2.3.win-amd64-py2.7.exe) and [32 bit](https://pypi.python.org/packages/2.7/l/lxml/lxml-2.3.win32-py2.7.exe) versions of Python.

### Run

Before you run the bot, rename `config.default` to `config` and edit it with your preferred settings.

Once you have installed the required dependencies and renamed the config file, you can run the bot! Make sure you are in the correct folder and run the following command:

`python bot.py`

On Windows you can usually just double-click `bot.py` to start the bot, as long as you have Python installed correctly.

## Getting help with CloudBot

### Documentation

To configure your CloudBot, visit the [Config Wiki Page](http://git.io/cloudbotircconfig).

To write your own plugins, visit the [Plugin Wiki Page](http://git.io/cloudbotircplugins).

More at the [Wiki Main Page](http://git.io/cloudbotircwiki).

(some of the information on the wiki is outdated and needs to be rewritten)

### Support

The developers reside in [#CloudBot](irc://irc.esper.net/cloudbot) on [EsperNet](http://esper.net) and would be glad to help you.

If you think you have found a bug/have a idea/suggestion, please **open a issue** here on Github.

### Requirements

CloudBot runs on **Python** *2.7.x*. It is currently developed on **Windows** *8* with **Python** *2.7.5*.

It **requires the Python module** lXML.
The module `Enchant` is needed for the spellcheck plugin.
The module `PyDNS` is needed for SRV record lookup in the mcping plugin.

**Windows** users: Windows compatibility some plugins is **broken** (such as ping), but we do intend to add it. Eventually.

## Example CloudBots

You can find a number of example bots in [#CloudBot](irc://irc.esper.net/cloudbot "Connect via IRC to #CloudBot on irc.esper.net").

## License

CloudBot is **licensed** under the **GPL v3** license. The terms are as follows.

    CloudBot

    Copyright © 2011-2013 Luke Rogers

    CloudBot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CloudBot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CloudBot.  If not, see <http://www.gnu.org/licenses/>.
