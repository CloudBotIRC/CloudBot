# CloudBot

CloudBot is a simple, fast, expandable open-source Python IRC Bot!

## Project Status & A more updated CloudBot

CloudBot is currently unmaintained. The project possibly usable, but there are currently no developers building new features or fixing bugs.

There are several forks of CloudBot which you may want to use instead. These projects have much more work done on them, and are thus incompatible. If you already have a running CloudBot instance you will probably need to start over from
scratch.

- TotallyNotRobots/CloudBot : [https://github.com/snoonetIRC/CloudBot](https://github.com/TotallyNotRobots/CloudBot)

  This is a more active fork being created by members of Snoonet that might be a better option for your needs. Keep in mind that, as a project more than a thousand commits ahead of this one, if you already have a running CloudBot instance you will probably need to start over from scratch.

- gonzobot : https://github.com/edwardslabs/CloudBot

If there are any other maintained forks of CloudBot, pull requests to add them to the README are welcome.

## Getting CloudBot

There are currently two different branches of this repository, each with a different level of stability:
 - **master** *(stable)*: This branch contains stable, tested code. This is the branch you should be using if you just want to run your own CloudBot! [![Build Status](https://travis-ci.org/CloudBotIRC/CloudBot.svg?branch=master)](https://travis-ci.org/CloudBotIRC/CloudBot)
 - **python3.4** *(unstable)*: This branch is where we test and develop new features. If you would like to help develop CloudBot, you can use this branch. [![Build Status](https://travis-ci.org/CloudBotIRC/CloudBot.svg?branch=python3.4)](https://travis-ci.org/CloudBotIRC/CloudBot)
 
New releases will be pushed from **python3.4** to **master** whenever we have a stable version to release. This should happen on a fairly regular basis, so you'll never be too far behind the latest improvements.

## Installing CloudBot

Firstly, CloudBot will only run on **Python 3.4 or higher**. Because we use the asyncio module, you will not be able to use any other versions of Python.

To install CloudBot on *nix (linux, etc), see [here](https://github.com/CloudBotIRC/CloudBot/wiki/Installing-on-*nix)

To install CloudBot on Windows, see [here](https://github.com/CloudBotIRC/CloudBot/wiki/Installing-on-Windows)


### Running CloudBot

Before you run the bot, rename `config.default.json` to `config.json` and edit it with your preferred settings. You can check if your JSON is valid using [jsonlint.com](http://jsonlint.com/)!

Once you have installed the required dependencies and renamed the config file, you can run the bot! Make sure you are in the correct folder and run the following command:

```
python3.4 -m cloudbot
```

Note that you can also run the `cloudbot/__main__.py` file directly, which will work from any directory.
```
python3.4 CloudBot/cloudbot/__main__.py
```
Specify the path as /path/to/repository/cloudbot/__main__.py, where `cloudbot` is inside the repository directory.

## Getting help with CloudBot

### Documentation

The CloudBot documentation is currently somewhat outdated and may not be correct. If you need any help, please visit our [IRC channel](irc://irc.esper.net/cloudbot) and we will be happy to assist you.

To write your own plugins, visit the [Plugins Wiki Page](https://github.com/CloudBotIRC/CloudBot/wiki/Writing-your-first-command-plugin).

More at the [Wiki Main Page](https://github.com/CloudBotIRC/CloudBot/wiki).

### Support

The developers reside in [#CloudBot](irc://irc.esper.net/cloudbot) on [EsperNet](http://esper.net) and would be glad to help you.

If you think you have found a bug/have an idea/suggestion, please **open an issue** here on Github and contact us on IRC!

## Example CloudBots

You can find a number of example bots in [#CloudBot](irc://irc.esper.net/cloudbot "Connect via IRC to #CloudBot on irc.esper.net").

## Changelog

See [CHANGELOG.md](https://github.com/CloudBotIRC/CloudBot/blob/master/CHANGELOG.md)

## License

CloudBot is **licensed** under the **GPL v3** license. The terms are as follows.

![GPL V3](https://www.gnu.org/graphics/gplv3-127x51.png)
    
    CloudBot

    Copyright © 2011-2015 Luke Rogers / CloudBot Project

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
<a href="http://www.maxmind.com">http://www.maxmind.com</a>. GeoLite2 databases are distributed under the [Creative Commons Attribution-ShareAlike 3.0 Unported License](https://creativecommons.org/licenses/by-sa/3.0/)

![Powered by wordnik](https://www.wordnik.com/img/wordnik_badge_a1.png)

This product uses data from <a href="http://wordnik.com">http://wordnik.com</a> in accordance with the wordnik.com API <a href="http://developer.wordnik.com/#!/terms">terms of service</a>.
