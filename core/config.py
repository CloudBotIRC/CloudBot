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
            "EsperNet":
            {
              "server": "irc.esper.net",
              "nick": "MyNewCloudBot",
              "user": "cloudbot",
              "realname": "CloudBot - http://git.io/cloudbotirc",
              "nickserv_password": "",
              "channels": ["#cloudbot"],
              "invitejoin": true,
              "autorejoin": false,
              "command_prefix": ".",
              "stayalive": false,
              "stayalive_delay": 20
            }
          },
          "disabled_plugins": [],
          "disabled_commands": [],
          "acls": {},
          "api_keys":
          {
            "geoip": "INSERT API KEY FROM ipinfodb.com HERE",
            "tvdb": "INSERT API KEY FROM thetvdb.com HERE",
            "bitly_user": "INSERT USERNAME FROM bitly.com HERE",
            "bitly_api": "INSERT API KEY FROM bitly.com HERE",
            "wolframalpha": "INSERT API KEY FROM wolframalpha.com HERE",
            "lastfm": "INSERT API KEY FROM lastfm HERE",
            "mc_user": "INSERT MINECRAFT USERNAME HERE",
            "mc_pass": "INSERT MINECRAFT PASSWORD HERE"
          },
          "plugins":
          {
            "factoids":
            {
              "prefix": false
            }
          },
          "censored_strings":
          [
            "mypass",
            "mysecret"
          ],
          "admins": ["myname"]
        }''') + '\n')
    print "Config generated!"
    print "Please edit the config now!"
    print "For help, see http://git.io/cloudbotircwiki"
    print "Thank you for using CloudBot!"
    sys.exit()


def config():
    # reload config from file if file has changed
    config_mtime = os.stat('config').st_mtime
    if bot._config_mtime != config_mtime:
        try:
            bot.config = json.load(open('config'))
            bot._config_mtime = config_mtime
        except ValueError, e:
            print 'error: malformed config', e


bot._config_mtime = 0

