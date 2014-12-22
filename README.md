# CloudBot

## Installing

To install on *Unix, see [docs/installing-unix.md](https://github.com/CloudBotIRC/CloudBotRefresh/blob/python3.4/docs/installing-unix.md)

To install on Windows, see [docs/installing-windows.md](https://github.com/CloudBotIRC/CloudBotRefresh/blob/python3.4/docs/installing-windows.md)

If you're going to be actively developing CloudBot, and submitting PRs back, we recommend running inside Vagrant. This allows everyone to have an identical development environment.

To install in Vagrant (both *Unix and Windows), see [docs/installing-vagrant.md](https://github.com/CloudBotIRC/CloudBotRefresh/blob/python3.4/docs/installing-vagrant.md)


### Running CloudBot

Before you run the bot, rename `config.default.json` to `config.json` and edit it with your preferred settings. You can check if your JSON is valid using [jsonlint.com](http://jsonlint.com/)!

Once you have installed the required dependencies and renamed the config file, you can run the bot! Make sure you are in the correct folder and run the following command:

```
python3.4 -m cloudbot
```

Note that you can also run the `cloudbot/__main__.py` file directly, which will work from any directory.
```
python3.4 cloudbot/cloudbot/__main__.py
```
Specify the path as /path/to/repository/cloudbot/__main__.py, where `cloudbot` is inside the repository directory.

## License

CloudBot is **licensed** under the **GPL v3** license. The terms are as follows.

    CloudBot

    Copyright © 2011-2014 Luke Rogers and CloudBot Contributors

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
