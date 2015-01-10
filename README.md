# CloudBot Refresh

## About

CloudBotRefresh is the newest generation of CloudBot, the fun, fast, extendable Python IRC bot!

## Installing CloudBot

Firstly, CloudBot will only run on **Python 3.4 or higher**. Because we use the asyncio module, you will not be able to use any other versions of Python. If you **really** want to run CloudBot on Python 2.x, you can find the old **unsupported** version of CloudBot at [this location](https://github.com/ClouDev/CloudBot).

To install CloudBotRefresh on *nix (linux, etc), see [docs/installing-unix.md](https://github.com/CloudBotIRC/CloudBotRefresh/blob/python3.4/docs/installing-unix.md)

To install CloudBotRefresh on Windows, see [docs/installing-windows.md](https://github.com/CloudBotIRC/CloudBotRefresh/blob/python3.4/docs/installing-windows.md)

If you're going to be actively developing on CloudBotRefresh, and submitting PRs back, we recommend running CloudBotRefresh inside Vagrant. This allows everyone to have an identical development environment.

To install CloudBotRefresh in Vagrant (both *Unix and Windows), see [docs/installing-vagrant.md](https://github.com/CloudBotIRC/CloudBotRefresh/blob/python3.4/docs/installing-vagrant.md)


### Running CloudBot

Before you run the bot, rename `config.default` to `config.json` and edit it with your preferred settings. You can check if your JSON is valid using [jsonlint.com](http://jsonlint.com/)!

Once you have installed the required dependencies and renamed the config file, you can run the bot! Make sure you are in the correct folder and run the following command:

```
python3.4 -m cloudbot
```

Note that you can also run the `cloudbot/__main__.py` file directly, which will work from any directory.
```
python3.4 CloudBotRefresh/cloudbot/__main__.py
```
Specify the path as /path/to/repository/cloudbot/__main__.py, where `cloudbot` is inside the repository directory.

## Getting help with CloudBot

### Documentation

To configure your CloudBot, visit the [Config Wiki Page](https://github.com/CloudBotIRC/CloudBotRefresh/wiki/Config).

To write your own modules, visit the [Module Wiki Page](https://github.com/CloudBotIRC/CloudBotRefresh/wiki/Writing-Refresh-Modules).

More at the [Wiki Main Page](https://github.com/CloudBotIRC/CloudBotRefresh/wiki).

Note that the configuration page, and the main wiki page, are still for CloudBot Develop. The Module Wiki Page has been
rewritten for refresh, but the other pages are outdated.

### Support

The developers reside in [#CloudBot](irc://irc.esper.net/cloudbot) on [EsperNet](http://esper.net) and would be glad to help you.

If you think you have found a bug/have a idea/suggestion, please **open a issue** here on Github and contact us on IRC!

## Example CloudBots

You can find a number of example bots in [#CloudBot](irc://irc.esper.net/cloudbot "Connect via IRC to #CloudBot on irc.esper.net").

## License

CloudBot is **licensed** under the **GPL v3** license. The terms are as follows.

    CloudBot

    Copyright © 2011-2015 Luke Rogers and CloudBot Contributors

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
    
![GPL V3](https://www.gnu.org/graphics/gplv3-127x51.png)

This product includes GeoLite2 data created by MaxMind, available from
<a href="http://www.maxmind.com">http://www.maxmind.com</a>. GeoLite2 databases are distributed under the Creative Commons Attribution-ShareAlike 3.0 Unported License.
