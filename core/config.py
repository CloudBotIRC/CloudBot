import inspect
import json
import os


def save(conf):
    json.dump(conf, open('config', 'w'), sort_keys=True, indent=2)

if not os.path.exists('config'):
    open('config', 'w').write(inspect.cleandoc(
        r'''
        {
          "connections":
          {
            "test connection":
            {
              "server": "localhost",
              "nick": "nickname",
              "user": "cloudbot",
              "realname": "CloudBot/DEV - http://j.mp/uS5Cvx",
              "nickserv_password": "",
              "channels": ["#channel"]
            }
          },
          "disabled_plugins": [],
          "disabled_commands": [],
          "prefix": ".",
          "acls": {},
          "api_keys":
          {
            "geoip": "INSERT API KEY FROM ipinfodb.com HERE",
            "tvdb": "INSERT API KEY FROM thetvdb.com HERE",
            "bitly_user": "INSERT USERNAME FROM bitly.com HERE",
            "bitly_api": "INSERT API KEY FROM bitly.com HERE",
            "wolframalpha": "INSERT API KEY FROM wolframalpha.com HERE",
            "mc_user": "INSERT MINECRAFT USERNAME HERE (used to check login servers in mctools.py)",
            "mc_pass": "INSERT MINECRAFT PASSWORD HERE (used to check login servers in mctools.py)"
          },
          "censored_strings":
          [
            "DCC SEND",
            "1nj3ct",
            "thewrestlinggame",
            "startkeylogger",
            "hybux",
            "\\0",
            "\\x01",
            "!coz",
            "!tell /x"
          ],
          "admins": []
        }''') + '\n')


def config():
    # reload config from file if file has changed
    config_mtime = os.stat('config').st_mtime
    if bot._config_mtime != config_mtime:
        try:
            bot.config = json.load(open('config'))
            bot._config_mtime = config_mtime
        except ValueError, e:
            print 'ERROR: malformed config!', e


bot._config_mtime = 0
