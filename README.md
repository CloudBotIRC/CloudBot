# xsBot: based on CloudBot (modified by xshotD)

xsBot was forked from CloudBot, which you can find [here](https://github.com/CloudBotIRC/CloudBot).
I have no plans to change licenses or anything. Although it's my repo, I won't change much. (Expect some major overhauls, but not too much.)

## Getting xsBot

There are currently two different branches of upstream, each with a different level of stability:

*UPSTREAM:* 
- **master** *(stable)*: This branch contains stable, tested code. This is the branch you should be using if you just want to run your own CloudBot! [![Build Status](https://travis-ci.org/CloudBotIRC/CloudBot.svg?branch=master)](https://travis-ci.org/CloudBotIRC/CloudBot)
 - **python3.4** *(unstable)*: This branch is where we test and develop new features. If you would like to help develop CloudBot, you can use this branch. [![Build Status](https://travis-ci.org/CloudBotIRC/CloudBot.svg?branch=python3.4)](https://travis-ci.org/CloudBotIRC/CloudBot)

*FORK:*

 - Travis CI for this fork will be added **soon**.
 
New releases will be pushed from **python3.4** to **master** whenever we have a stable version to release. This should happen on a fairly regular basis, so you'll never be too far behind the latest improvements.

## Installing CloudBot

Firstly, xsBot will only run on **Python 3.4 or higher**. Because we use the asyncio module, you will not be able to use any other versions of Python.

To install xsBot on *nix (linux, etc), see [the upstream wiki.](https://github.com/CloudBotIRC/CloudBot/wiki/Installing-on-*nix)

You should be able to install the bot in the same way it is done upstream. Also, I do recommend running it on *nix.

Conflicting software I have seen (so far): Bitdefender (in my testing. Windows only.)

To install CloudBot on Windows, see [the upstream wiki.](https://github.com/CloudBotIRC/CloudBot/wiki/Installing-on-Windows)


### Running CloudBot

Before you run the bot, rename `config.default.json` to `config.json` and edit it with your preferred settings. You can check if your JSON is valid using [JSONLint](http://jsonlint.com/)!

Once you have installed the required dependencies and renamed the config file, you can run the bot! Make sure you are in the correct folder and run the following command:

```
python3.4 -m cloudbot
```

Usually you can run it from the command `python3 /path/to/cloudbot/__main__.py`.

## Getting help with CloudBot

### Documentation

The CloudBot documentation is currently somewhat outdated and may not be correct. If you need any help, please visit our [IRC channel](irc://irc.esper.net/cloudbot) and we will be happy to assist you.

To write your own plugins, visit the [Plugins Wiki Page](https://github.com/CloudBotIRC/CloudBot/wiki/Writing-your-first-command-plugin).

More at the [Wiki Main Page](https://github.com/CloudBotIRC/CloudBot/wiki).

### Support

The developers reside in [#CloudBot](irc://irc.esper.net/cloudbot) on [EsperNet](http://esper.net) and would be glad to help you.

If you think you have found a bug/have a idea/suggestion, please **open a issue** here on Github and contact us on IRC!

## Example CloudBots

You can find a number of example bots in [#CloudBot](irc://irc.esper.net/cloudbot "Connect via IRC to #CloudBot on irc.esper.net").

## Changelog

See [CHANGELOG.md](https://github.com/CloudBotIRC/CloudBot/blob/master/CHANGELOG.md)

## License

CloudBot is **licensed** under the **GPL v3** license. The terms are as follows.

![GPL V3](https://www.gnu.org/graphics/gplv3-127x51.png)
    
    xsBot

    Upstream code: Copyright © 2011-2015 Luke Rogers / CloudBot Project
    Fork code: Copyright © 2016 xshotD / xs Devs.

    xsBot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    xsBot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with xsBot.  If not, see <http://www.gnu.org/licenses/>.
    
This product includes GeoLite2 data created by MaxMind, available from
<a href="http://www.maxmind.com">their website</a>. GeoLite2 databases are distributed under the [Creative Commons Attribution-ShareAlike 3.0 Unported License](https://creativecommons.org/licenses/by-sa/3.0/)

![Powered by wordnik](https://www.wordnik.com/img/wordnik_badge_a1.png)

This product uses data from <a href="http://wordnik.com">Wordnik</a> in accordance with the wordnik.com API <a href="http://developer.wordnik.com/#!/terms">ToS</a>.
