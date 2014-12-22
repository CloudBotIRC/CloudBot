## Installing on *Unix systems

### Downloading

#### Manual Download
Download CloudBot from [https://github.com/daboross/cloudbot/archive/master.zip](https://github.com/daboross/cloudbot/archive/master.zip) and unzip, or execute the following commands:
```
curl -Ls https://github.com/daboross/cloudbot/archive/master.zip > CloudBot.zip
unzip CloudBot.zip
cd cloudbot-master
```

#### Git

Alternately, you can also clone CloudBot by using:
```
git clone https://github.com/daboross/cloudbot.git
cd cloudbot
```

### Installing Dependencies

All of CloudBot's python dependencies are stored in the `requirements.txt` file, and can be installed with pip.

But first, you will need `python3.4` installed on your system. Install this with your system's package manager.

For example, on a Debian-based system, you could use:
```
[sudo] apt-get install -y python3.4
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
