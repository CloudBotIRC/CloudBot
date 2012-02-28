##CloudBot/DEV

### About
CloudBot is very heavily based on [Skybot](https://github.com/rmmh/skybot) by rmmh.  

CloudBot is meant to be a simple, extendable python IRC bot, with minimal magic.  To write your own plugins, vist the [Plugin Wiki Page](http://git.io/cloudbotplugins).

More at the [wiki](http://git.io/cloudbotwiki).

### Download
Get Cloudbot at [git.io/getcloudbot](http://git.io/getcloudbot "CloudBot").
Unzip, and follow the install directions.

### Install
Before you can run the bot, you need to install a few Python modules. These are `lXML`, `BeautifulSoup`, and `Enchant`.  On Debian based systems, these can be installed using the following commands:

`sudo apt-get install python-lxml`

`sudo apt-get install python-beautifulsoup`

`sudo apt-get install python-enchant`

In addition, for .whois to work optimally, you must have `whois` installed. Again, on Debian based systems, install it with 
`sudo apt-get install whois`

If you are a user of another Linux disto, use your package manager to install the modules, or use Google to locate source packages you can install.
Once you have installed the required dependencies, run the bot with 

`python bot.py`

It will generate a default config for you.  Once you have editied the config, run it again with

`python bot.py`

and it will connect to any server(s) you have added to the config. (Config docs at the [wiki](http://git.io/cloudbotconfig))

### Requirements
CloudBot runs on Python 2.7.x. It is developed on Debian Wheezy/Testing with Python 2.7.2.

### Example CloudBots
The developers of CloudBot run two Cloudbots on [Espernet](http://esper.net).

They can both be found in [#CloudBot](irc://irc.esper.net/cloudbot "Connect via IRC to #CloudBot on irc.esper.net).

**mau5bot** is the stable bot, and runs on the lastest release version of CloudBot. (mau5bot is running on Ubuntu Server Oneric Ocelot/11.10 with Python 2.7.2)

**neerbot** is the unstable bot, and runs on the lastest development version of CloudBot. (neerbot is running on Debian Wheezy/Testing with Python 2.7.2)

### License
CloudBot is licenced under the GPL v3 license. The terms are as follows.

#### CloudBot/DEV

    Copyright © 2011 Luke Rogers <http://www.dempltr.com/> - <lukeroge@gmail.com>

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
