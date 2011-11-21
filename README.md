##CloudBot/DEV

### About
CloudBot is very heavily based on Skybot by rmmh. (https://github.com/rmmh/skybot)

### Install
Before you can run the bot, you need to install a few Python modules. These are *LXML*, *BeautifulSoup* and *simplejson*.  On Ubuntu these can be installed using the following commands:

```sudo apt-get install python-lxml
```

```sudo apt-get install python-beautifulsoup
```

```sudo apt-get install python-simplejson
```

If you use another OS or distro you can find source packages on the module web sites, or try to find the modules packages in your package manager.

Once installing these packages run the bot once with ```python bot.py``` to generate the config file. Stop the bot, edit the config, and run the bot again with ```python bot.py``` to start it up :)

### Requirements
CloudBot runs on Python 2.7. Many of the plugins require lxml and BeautifulSoup. It is developed on Ubuntu 11.10 with Python 2.7.2.
