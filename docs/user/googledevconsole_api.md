# Setting up the Google Developers Console API

## Introduction
In this guide, we will cover the setup of the GDC API for use within CloudBot. This API is used by:
 - plugins/books.py
 - plugins/youtube.py
 - plugins/google_translate.py

## 1 - Sign Up for the Google Developers Console
You can create a GDC account at https://console.developers.google.com/. You need to create a Google account or use an existing one.

## 2 - Create a new project
Select ***Create New Project*** if you haven't already done so:

![GDC Create a New Project](img/gdev_1.png?raw=true "Create a New Project")

Give your bot a name (and optionally change the name of the project ID), agree to the Terms of Service, then select ***Create***.

![GDC Name Your Bot](img/gdev_2.png?raw=true "Name Your Bot")

## 3 - Enable APIs

Once you have created the project, select it in the main panel (if it already hasn't been), then on the sidebar go to **APIs and Auth -> APIs**. Scroll through the list to select ***ON*** for the following services:

 - Books API
 - Youtube Data API v3
 - Geocoding API
 - Time Zone API
 - Optional: Google Custom Search API, if using Google Search
 - Optional: Translate API, if using Google Translate

Optional APIs are only used if you got the right modules or a payment type to use.

 ![GDC Select the APIs](img/gdev_3.png?raw=true "Select the APIs")
 
 For each API, you may have to first accept their individual Terms of Service, then select ***Accept***.
 
![GDC Agree to the ToS](img/gdev_4.png?raw=true "Agree to the ToS")
 
## 4 - Generate an API Key
GDC API services only need one key for all Google Services used. You must generate a key for each bot instance you plan to use. Go to **APIs and Auth -> Credentials** then select ***Create a new Key***
 
![GDC Create a Key](img/gdev_5.png?raw=true "Create a Key")
 
Select to create a ***Server Key***
 
![GDC Server Key](img/gdev_6.png?raw=true "Server Key")
 
Enter the Public IPs of the Cloudbot instance you plan to assign to this key. If you don't know it, running `wget -qO- http://icanhazip.com/` within your terminal should return it. Click ***Create***.
 
![GDC Enter IPs](img/gdev_7.png?raw=true "Enter IPs")
 
Your new key should now appear on the main panel, simply copy it to the *google_dev_key* object in your CloudBot's configuration.

![GDC Copy the key](img/gdev_8.png?raw=true "Copy the key")
