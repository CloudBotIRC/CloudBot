# CloudBot Refresh

## About

CloudBot Refresh is an updated version of CloudBot, the python IRC bot origially based on [Skybot](http://git.io/skybot) by [rmmh](http://git.io/rmmh).

## Getting and using CloudBot

### Download 

Get CloudBot at [https://github.com/CloudBotIRC/CloudBot/zipball/3.4-refactoring](https://github.com/CloudBotIRC/CloudBot/zipball/3.4-refactoring "Get CloudBot from Github!").

Unzip the resulting file, and continue to read this document.

### Install

Before you can run the bot, you need to install a few Python dependencies. lxml, watchdog, sqlalchemy and BeautifulSoup4
are required by CloudBot. `pyenchant`, `pydns`, `pygeoip`, `tweepy`, `pycrypto` and `pbkdf2` are also required for various plugins.

Make sure you're running python version **3.4** or higher.

These can be installed with `pip` (The Python package manager) by running the following command in the bot directory:

    pip install -r requirements.txt

**Note:** If you use `pip`, you will also need the following packages on linux or `pip` will fail to install the requirements.

```
python, python-dev, libenchant-dev, libenchant1c2a, libxslt-dev, libxml2-dev.
```

(this can be done using your package manager (eg: *apt-get* or *yum*)

#### How to install `pip`

You can usually install pip on linux by installing the `python-pip` package using your package manager (eg. *apt-get install python-pip* or *yum install python-pip* as root), or you can try the below code to download and install it manually.

    curl -O http://python-distribute.org/distribute_setup.py # or download with your browser on windows
    python distribute_setup.py
    easy_install pip

If you need help installing pip on Windows, follow [this guide](http://simpledeveloper.com/how-to-install-easy_install/) and then run `easy_install pip` on the command line.


Note for **Windows** users: Windows compatibility some modules is **broken** (such as ping), but we do intend to add it, eventually.

### Run

Before you run the bot, rename `config.default` to `config.json` and edit it with your preferred settings. You can check if your JSON is valid on [this site](http://jsonlint.com/)!

Once you have installed the required dependencies and renamed the config file, you can run the bot! Make sure you are in the correct folder and run the following command:

`python3.4 -m cloudbot`

## Getting help with CloudBot

### Documentation

To configure your CloudBot, visit the [Config Wiki Page](https://github.com/CloudBotIRC/Refresh/wiki/Config).

To write your own modules, visit the [Module Wiki Page](https://github.com/CloudBotIRC/CloudBot/wiki/Writing-Refresh-Modules).

More at the [Wiki Main Page](https://github.com/CloudBotIRC/Refresh/wiki).

Note that the configuration page, and the main wiki page, are still for CloudBot Develop. The Module Wiki Page has been
rewriten for refresh, but the other pages are outdated.

### Support

The developers reside in [#CloudBot](irc://irc.esper.net/cloudbot) on [EsperNet](http://esper.net) and would be glad to help you.

If you think you have found a bug/have a idea/suggestion, please **open a issue** here on Github and contact us on IRC!

### Requirements

CloudBot runs on **Python** *3.4+*. It is currently developed on **Windows** *8* with **Python** *3.4*.

It **requires the python modules** lxml, watchdog, sqlalchemy and BeautifulSoup4.

Besides that, `pyenchant` is needed for spellcheck plugin, `pydns` is required for srv lookups in the minecraftping
plugin, `pygeoip` is required for the geoip plugin, `tweepy` is required for the twitter plugin, and `pycrypto` and
`pbkdf2` are required for the encrypt plugin.

**Windows** users: Windows compatibility some plugins is **broken** (such as ping), but we do intend to add it. Eventually.

## Example CloudBots

You can find a number of example bots in [#CloudBot](irc://irc.esper.net/cloudbot "Connect via IRC to #CloudBot on irc.esper.net").

## License

CloudBot is **licensed** under the **GPL v3** license. The terms are as follows.

    CloudBot

    Copyright © 2011-2014 Luke Rogers and CloudBot Contributors

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
