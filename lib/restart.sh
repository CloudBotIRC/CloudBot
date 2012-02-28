#!/bin/sh
sleep 5
if [ -f ./control.sh ]; then
    ./control.sh restart
elif [ -f ./bot.sh ]; then
    ./bot.sh restart
else
    ./bot.py
fi
exit 0