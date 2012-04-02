# CloudBot/1.2

## About

CloudBot is a Python IRC bot very heavily based on [Skybot](http://git.io/skybot) by [rmmh](http://git.io/rmmh).  

### Goals

* Easy to use wrapper
* Intuitive configuration
* Fully controlled from IRC
* Fully compatable with existing skybot plugins
* Easily extendable
  * Thorough documentation
  * Cross-platform
* Muti-threaded, efficient
  * Automatic reloading
  * Little boilerplate

## Download

Get CloudBot at [git.io/getcloudbotirc](http://git.io/getcloudbotirc "Get CloudBot from Github!").

Unzip the resulting file, and continue to read this document.

## Install

Before you can run the bot, you need to install a few Python modules. These are `lXML`, `BeautifulSoup`, `psutil`, and `HTTPlib2`.  These can be installed with PIP (The Python package manager):

`sudo pip install lxml`

`sudo pip install beautifulsoup`

`sudo pip install psutil`

`sudo pip install httplib2`

On Debian based systems, you can get pip with

`sudo apt-get install pip`

For `.spell` to work, we also need a library called `Enchant`.  On Debian based systems, install it with:

`sudo apt-get install python-enchant`

In addition, for `.whois` to work optimally, you must have `whois` installed. Again, on Debian based systems, install it with:

`sudo apt-get install whois`

For the wrapper to work best, install `screen`, or `daemon`:

`sudo apt-get install screen`

`sudo apt-get install daemon`

If you are a user of another Linux disto, use your package manager to install the dependencies, or, for other operating systems,  use **Google** to locate source packages you can install.

Once you have installed the required dependencies, run the bot¹:

`./cloudbot start`

It will generate a default config for you.  Once you have edited the config, run it again with:

`./cloudbot start`

and it will connect to any server(s) you have added to the config. (Config docs at the [wiki](http://git.io/cloudbotircconfig))

## Documentation

To configure your CloudBot, visit the [Config Wiki Page](http://git.io/cloudbotircconfig).

To write your own plugins, visit the [Plugin Wiki Page](http://git.io/cloudbotircplugins).

More at the [Wiki Main Page](http://git.io/cloudbotircwiki).

## Support

The developers reside in [#CloudBot](irc://irc.esper.net/cloudbot "Connect via IRC to #CloudBot on irc.esper.net) on [EsperNet](http://esper.net) and would be glad to help you.

If you think you have found a bug/have a idea/suggestion, please **open a issue** here on Github.

## Example CloudBots

The developers of CloudBot run two CloudBots on [Espernet](http://esper.net).

They can both be found in [#CloudBot](irc://irc.esper.net/cloudbot "Connect via IRC to #CloudBot on irc.esper.net).

**mau5bot** is the stable bot, and runs on the latest release version of CloudBot. (mau5bot is running on **Ubuntu Server** *Oneric Ocelot/11.10* with **Python** *2.7.2*)

**neerbot** is the unstable bot, and runs on the latest development² version of CloudBot. (neerbot is running on **Debian** *Wheezy/Testing* with **Python** *2.7.2*)

## Requirements

CloudBot runs on **Python** *2.7.x*. It is developed on **Debian** *Wheezy/Testing* and **Ubuntu** *11.10* with **Python** *2.7.2*.

It **requires Python modules** `lXML`, `BeautifulSoup`, `Enchant`, `psutil`, and `HTTPlib2`.

The programs `screen` or `daemon` are recomended for the wrapper to run optimaly.

**Windows** users: Windows compatibility with the wrapper and some plugins is **broken** (such as the ping), but we do intend to add it.³

## License
CloudBot is **licensed** under the **GPL v3** license. The terms are as follows.
    
    CloudBot/1.2

    Copyright © 2011 ClouDev - <[cloudev.github.com](http://cloudev.github.com)>

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

## Notes

¹ if you prefer to run the bot with a custom backend/run it manually, or are on **Windows**, run the bot with `./bot.py`

² or whatever version [neersighted](http://git.io/neersighted) is currently hacking on

³ eventually
