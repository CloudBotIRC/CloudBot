#!/usr/bin/env bash

# update sources
sudo apt-get update

# install things:
# python3.4-dev     so we can install things with pip
# libenchant1c2a    pyenchant dependency
# libxml2-dev       python-lxml dependency
# libxslt-dev       python-lxml dependency
# zlib1g-dev        python-lxml dependency
sudo apt-get install -y python3-pip git libenchant1c2a libxml2-dev libxslt-dev zlib1g-dev

curl -Ls https://bootstrap.pypa.io/get-pip.py | python3.4

# install requirements using pip
sudo pip3 install -r /vagrant/requirements.txt

# create link from project to ~/bot
ln -sf /vagrant /home/vagrant/bot

# create start.sh script
cat > /usr/local/bin/start-bot <<- _EOF_
    #!/usr/bin/env bash
    cd /home/vagrant/bot
    export BOTCONFIG=\`cat /home/vagrant/bot/config-local.json\`
    python3 -m cloudbot
_EOF_
chmod +x /usr/local/bin/start-bot
