# User Docs for CloudBot

## Introduction

In this guide, we will cover the setup and configuration procedures in the following files:

 - main_user.md: (This File) contains the introductory material for setting up CloudBot.
 - configuration.md: Contains more information on creating a JSON configuration file for CloudBot.
 - XXXX_api.md: Describes the setup procedures for that specific API and their use in CloudBot.

## 1 - Getting CloudBot

Setting up CloudBot on a new server instance is simple. To begin, you need a compatible server that supports **Python 3.4**. Earlier versions of Python are not compatible due to the use of *asyncIO*.

We recommend using the stable releases of CloudBot that can be found [on the releases page](https://github.com/CloudBotIRC/CloudBot/releases), or from the `master` branch on GitHub.

#### Using HTTP

If you only have command-line access, run the following in your terminal:

  **On Linux:**
  ```
  wget https://github.com/CloudBotIRC/CloudBot/archive/master.zip
  ```
  
  **On OS X:**
  ```
  curl -O https://github.com/CloudBotIRC/CloudBot/archive/master.zip
  ```
  
  Followed by `unzip master.zip` on both OSs.
  
#### Using Git
  
  You can also use Git to pull a new version of CloudBot, (which is useful for making upgrades easier). This can be accomplished with
  
  ```
  git clone https://github.com/CloudBotIRC/CloudBot.git
  cd CloudBot
  ```

## 2 - Getting Python 3.4
Setting up Python 3.4 on most OSs usually goes as follows.

  **On Linux (Debian Based):**
  Run the following in your terminal:
  ```
  [sudo] apt-get install python python3.4-dev git libenchant-dev libxml2-dev libxslt-dev zlib1g-dev
  ```

  **On OS X:**
  Mac OS X already comes with Python 2.7 pre-installed, this is not sufficient for CloudBot. The latest binaries can be found at https://www.python.org/downloads/

  **On Windows:**
  You can download releases of Python 3.4 for Windows at https://www.python.org/downloads/
  
  **todo**: section on adding python to PATH on windows so it is usable from the console!!!

  **On another OS (Solaris/BSD/ActivePython/etc):**
  You can try compiling Python 3.4 from source, note however that you may run into issues with CloudBot or its dependencies (many of the Other OSs only support Python 2.x).

  You can find source at https://www.python.org/downloads/source/

## 3 - Get PIP
PIP is suggested to make installation of CloudBot's dependencies easier, and is used extensively in this guide.

  **On Linux:**
  Run the following in your terminal:
  ```
  wget https://bootstrap.pypa.io/get-pip.py
  [sudo] python3.4 get-pip.py
  ```
  **On OS X:**
  Run the following in your terminal:
  ```
  curl https://bootstrap.pypa.io/get-pip.py | sudo python3.4
  ```
  **On Windows:**
  ```
  Luke, you should really fill this bit.
  ```

## CloudBot Depdendencies and APIs

Before running CloudBot, you'll need to get some of the required dependencies and APIs configured/installed.

  **Using PIP:**
  Assuming the current directory is that of your CloudBot installation (in the terminal):
  ```
  pip install -r requirements.txt
  ```
  

