#!/usr/bin/env bash

# update sources
sudo apt-get update

# install things:
# pip               so we can install rependencies
# git               so pip can clone from repository
# libenchant-dev    so python-enchant can use it
# python3-lxml      so we can use precompiled binaries instead of compiling them

sudo apt-get install -y python3-pip git libenchant-dev python3-lxml

# install requirements using pip
sudo pip3 install -r /vagrant/requirements.txt

# create link from project to ~/bot
ln -sf /vagrant /home/vagrant/bot

# create start.sh script
cat > /usr/local/bin/start-bot <<- _EOF_
    #!/usr/bin/env bash
    cd /home/vagrant/bot
    python3 -m cloudbot
_EOF_
chmod +x /usr/local/bin/start-bot
