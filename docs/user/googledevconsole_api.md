# Setting up the Google Developers Console API

## Introduction
In this guide, we will cover the setup of the GDC API for use within CloudBot. This API is used by:
 - plugins/books.py
 - plugins/youtube.py
 - plugins/google_translate.py

## 1 - Sign Up for the Google Developers Console
You can create a GDC account at https://console.developers.google.com/. You need to create a Google account or use an existing one.

## 2 - Create a new project
Select "Create New Project" if you haven't already done so:

![GDC Create a New Project](img/gdev_1.png?raw=true "Create a New Project")

Give your bot a name (and optionally change the name of the project ID), agree to the terms of service, then press "Create".

![GDC Name Your Bot](img/gdev_2.png?raw=true "Name Your Bot")

## 3 - Enable APIs

Once you have created the project, select it in the main panel (if it already hasnt been), then on the sidebar go to **APIs and Auth -> APIs**. Scroll through the list to set on for the following services:

 - Books API
 - Youtube Data API v3
 - (Optional: Google Custom Search API, if using Google Search)
 - (Optional: Translate API, if using Google Translate)

 ![GDC Select the APIs](img/gdev_3.png?raw=true "Select the APIs")
