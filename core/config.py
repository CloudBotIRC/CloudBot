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
              "invite_join": true,
              "auto_rejoin": false,
              "command_prefix": "."
            }
          },
          "disabled_plugins": [],
          "disabled_commands": [],
          "acls": {},
          "api_keys":
          {
            "tvdb": "",
            "wolframalpha": "",
            "lastfm": "",
            "rottentomatoes": "",
            "soundcloud": "",
            "twitter_consumer_key": "",
            "twitter_consumer_secret": "",
            "twitter_access_token": "",
            "twitter_access_secret": "",
            "wunderground": ""
          },
          "plugins":
          {
            "factoids":
            {
              "prefix": false
            },
            "ignore":
            {
              "ignored": []
            }
          },
          "censored_strings":
          [
            "mypass",
            "mysecret"
          ],
          "admins": ["myname@myhost"]
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

