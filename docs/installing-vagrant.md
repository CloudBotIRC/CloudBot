## Installing Using Vagrant

When developing CloudBot, it is recommended that you run the bot inside a CloudBot Vagrant VM. This guarantees that everyone developing CloudBot will have an identical working environment.

#### Archive

Download CloudBot from [https://github.com/CloudBotIRC/CloudBot/zipball/python3.4.zip](https://github.com/CloudBotIRC/CloudBot/archive/python3.4.zip) and u$
```
curl -Ls https://github.com/CloudBotIRC/CloudBot/archive/python3.4.zip > CloudBot.zip
unzip CloudBot.zip
cd CloudBot-python3.4
```

#### Git

Alternately, you can also clone CloudBot by using:
```
git clone https://github.com/CloudBotIRC/CloudBot.git
cd CloudBot
```

### Setting up the Virtual Machine

First, you need to install Vagrant. See [docs.vagrantup.com](http://docs.vagrantup.com/v2/installation/index.html) for a guide on installing Vagrant

Next, use the `vagrant up` command in the CloudBot directory. This may take a while, but when it's finished, you will have a fully installed CloudBot virtual machine.

To run the bot, connect to the virtual machine using `vagrant ssh`, then use the `start-bot` command in the ssh terminal.
