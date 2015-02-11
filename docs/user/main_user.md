# User Docs for CloudBot

## Introduction

In this guide, we will cover the setup and configuration procedures in the following files:

 - main_user.md: (This File) contains the introductory material for setting up CloudBot.
 - configuration.md: Contains more information on creating a JSON configuration file for CloudBot.
 - XXXX_api.md: Describes the setup procedures for that specific API and their use in CloudBot.

## Getting CloudBot

Setting up CloudBot on a new server instance is simple. To begin, you need a compatible server that supports **Python 3.4**. Earlier versions of Python are not compatible due to the use of *asyncIO*.

We recommend using the stable releases of Cloudbot that can be found [on the releases page](https://github.com/CloudBotIRC/CloudBot/releases), or from the `master` branch on GitHub.

#### Using HTTP

If you only have command-line access, you can use the following to get CloudBot onto your server.

  **On Linux**: `wget https://github.com/CloudBotIRC/CloudBot/archive/master.zip`
  
  **On OS X**: `curl -O https://github.com/CloudBotIRC/CloudBot/archive/master.zip`
  
  Followed by `unzip master.zip` on both OSs.
  
#### Using Git
  
  You can also use Git to pull a new version of CloudBot, and it is useful for making updates easier. This can be accomplished with
  
  ```
  git clone https://github.com/CloudBotIRC/CloudBot.git
  cd CloudBot
  ```
## CloudBot Depdendencies and APIs

Before running CloudBot, you'll need to get some of the required dependencies and APIs configured/installed.
  

