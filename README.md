# CloudBot/DEV

## About
`CloudBot` is a `Python` very heavily based on [`Skybot`](http://git.io/skybot) by [rmmh](http://git.io/rmmh).  

### Goals

* Easily extendable
  * Though documentation
  * Cross-platform
* Muti-threaded, efficient
  * Automatic reloading
  * Little boilerplate
* Intuitive configuration
* Fully controlled from in IRC

## Download
Get `CloudBot` at [git.io/getcloudbot](http://git.io/getcloudbot "Get CloudBot from GitHub!").

Unzip the resulting file, and continue to read this document.

## Install
Before you can run the bot, you need to install a few `Python` modules. These are `lXML`, `BeautifulSoup`, `MyGengo`, and `HTTPlib2`.  These can be installed with PIP (The `Python` packager):

`sudo pip install lxml`

`sudo pip install beautifulsoup`

`sudo pip install mygengo`

`sudo pip install httplib2`

On `Debian` based systems, you can get pip with

`sudo apt-get install pip`

For .spell to work, we also need a library called `Enchant`.  On `Debian` based systems, install with

`sudo apt-get install python-enchant`

In addition, for .whois to work optimally, you must have `whois` installed. Again, on `Debian` based systems, install it with 

`sudo apt-get install whois`

If you are a user of another Linux disto, use your package manager to install the dependencies, or, for other operating systems,  use **Google** to locate source packages you can install.

Once you have installed the required dependencies, run the bot with 

`python bot.py`

It will generate a default config for you.  Once you have edited the config, run it again with

`python bot.py`

and it will connect to any server(s) you have added to the config. (Config docs at the [wiki](http://git.io/cloudbotconfig))

## Documentation

To configure your `CloudBot`, visit the [Config Wiki Page](http://git.io/cloudbotconfig).

To write your own plugins, visit the [Plugin Wiki Page](http://git.io/cloudbotplugins).

More at the [Wiki Home Page](http://git.io/cloudbotwiki).

## Example `CloudBot`s

The developers of `CloudBot` run two `CloudBot`s on [Espernet](http://esper.net).

They can both be found in [#CloudBot](irc://irc.esper.net/cloudbot "Connect via IRC to #CloudBot on irc.esper.net).

**mau5bot** is the stable bot, and runs on the latest release version of `CloudBot`. (mau5bot is running on `Ubuntu Server` *Oneric Ocelot/11.10* with `Python` 2.7.2)

**neerbot** is the unstable bot, and runs on the latest development version of `CloudBot`. (neerbot is running on `Debian` *Wheezy/Testing* with `Python` 2.7.2)

## Requirements

`CloudBot` runs on `Python` 2.7.x. It is developed on `Debian` *Wheezy/Testing* with `Python` 2.7.2.

It requires `Python` modules `lXML`, `BeautifulSoup`, `Enchant`, `MyGengo`, and `HTTPlib2`.

`Windows` users: `Windows` compatibility is broken, but we do intend to add it back. (Eventually)

## License
`CloudBot` is licensed under the GPL v3 license. The terms are as follows.
    
    CloudBot/DEV

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
