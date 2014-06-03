## Installing on *Unix systems

### Downloading

#### Manual Download
Download CloudBotRefresh from [https://github.com/CloudBotIRC/CloudBot/zipball/python3.4.zip](https://github.com/CloudBotIRC/CloudBotRefresh/archive/python3.4.zip) and unzip, or execute the following commands:
```
curl -Ls https://github.com/CloudBotIRC/CloudBotRefresh/archive/python3.4.zip > CloudBot.zip
unzip CloudBot.zip
cd CloudBotRefresh-python3.4
```

#### Git

Alternately, you can also clone CloudBotRefresh by using:
```
git clone https://github.com/CloudBotIRC/CloudBotRefresh.git
cd CloudBotRefresh
```

### Installing Dependencies

All of CloudBot's python dependencies are stored in the `requirements.txt` file, and can be installed with pip.

But first, you will need `git`, `python3.4-dev` and `libenchant1c2a`, `libxml2-dev`, `libxslt-dev` and `zlib1g-dev`. Install these with your system's package manager.

For example, on a Debian-based system, you could use:
```
[sudo] apt-get install -y python3.4-dev git libenchant-dev libxml2-dev libxslt-dev zlib1g-dev
```

Now we can install a python3.4 version of pip using the following command:
```
curl -Ls https://bootstrap.pypa.io/get-pip.py | [sudo] python3.4
```

Note that you need a **python3.4** version of pip, which is why we recommend using get-pip.py rather than installing python-pip or python3-pip in your system's package manager.

Finally, install the python dependencies using `pip` using the following command in the CloudBot directory:
```
pip install -r requirements.txt
```
