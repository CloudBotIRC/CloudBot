#!/usr/bin/env bash

# update sources
sudo apt-get update

# install python
sudo apt-get install -y python3.4

curl -Ls https://bootstrap.pypa.io/get-pip.py | sudo python3.4

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
