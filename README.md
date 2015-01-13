# CloudBot [![Build Status](https://travis-ci.org/CloudBotIRC/CloudBot.svg?branch=python3.4)](https://travis-ci.org/CloudBotIRC/CloudBot) [![Coverage Status](https://coveralls.io/repos/CloudBotIRC/CloudBot/badge.png?branch=python3.4)](https://coveralls.io/r/CloudBotIRC/CloudBot?branch=python3.4)

CloudBot Refresh is the newest generation of CloudBot, the fun, fast, extendable Python IRC bot!

## Installing CloudBot

Firstly, CloudBot will only run on **Python 3.4 or higher**. Because we use the asyncio module, you will not be able to use any other versions of Python.

To install CloudBot on *nix (linux, etc), see [here](https://github.com/CloudBotIRC/CloudBot/wiki/Installing-on-*nix)

To install CloudBot on Windows, see [here](https://github.com/CloudBotIRC/CloudBot/wiki/Installing-on-Windows)

If you're going to be actively developing on CloudBot, and submitting PRs back, you can run CloudBot inside Vagrant. This allows everyone to have an identical development environment.

To install CloudBot in Vagrant (both *Unix and Windows), see [here](https://github.com/CloudBotIRC/CloudBot/wiki/Installing-with-Vagrant)


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

The CloudBot documentation is currently somewhat outdated and may not be correct. If you need any help, please visit our [IRC channel](irc://irc.esper.net/cloudbot) and we will be happy to assist you.

To write your own plugins, visit the [Plugins Wiki Page](https://github.com/CloudBotIRC/CloudBotRefresh/wiki/Writing-Refresh-Modules).

More at the [Wiki Main Page](https://github.com/CloudBotIRC/CloudBotRefresh/wiki).

### Support

The developers reside in [#CloudBot](irc://irc.esper.net/cloudbot) on [EsperNet](http://esper.net) and would be glad to help you.

If you think you have found a bug/have a idea/suggestion, please **open a issue** here on Github and contact us on IRC!

## Example CloudBots

You can find a number of example bots in [#CloudBot](irc://irc.esper.net/cloudbot "Connect via IRC to #CloudBot on irc.esper.net").

## License

CloudBot is **licensed** under the **GPL v3** license. The terms are as follows.

![GPL V3](https://www.gnu.org/graphics/gplv3-127x51.png)
    
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
    
This product includes GeoLite2 data created by MaxMind, available from
<a href="http://www.maxmind.com">http://www.maxmind.com</a>. GeoLite2 databases are distributed under the [Creative Commons Attribution-ShareAlike 3.0 Unported License](https://creativecommons.org/licenses/by-sa/3.0/).
