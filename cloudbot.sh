#!/bin/sh
echo "Welcome to:                                                                         "
echo "  ______  __        ______    __    __   _______  .______     ______   .___________."
echo " /      ||  |      /  __  \  |  |  |  | |       \ |   _  \   /  __  \  |           |"
echo "|  ,----'|  |     |  |  |  | |  |  |  | |  .--.  ||  |_)  | |  |  |  | \`---|  |----\`"
echo "|  |     |  |     |  |  |  | |  |  |  | |  |  |  ||   _  <  |  |  |  |     |  |     "
echo "|  \`----.|  \`----.|  \`--'  | |  \`--'  | |  '--'  ||  |_)  | |  \`--'  |     |  |     "
echo " \______||_______| \______/   \______/  |_______/ |______/   \______/      |__|     "
echo " http://git.io/cloudbot                                                 by lukeroge "

checkbackends() {
    backends=0
        if dpkg -l | grep ^ii | grep screen | grep -i 'turns other' > /dev/null; then
        backends=$((backends+1))
        else
            backend="daemon"
        fi
        if dpkg -l | grep ^ii | grep daemon | grep -i 'terminal multi' > /dev/null; then
        backends=$((backends+1))
        else
            backend="screen"
        fi
        if [ "$backends" -lt 1 ]; then
            echo "No `daemon` or `screen` detected, running manually"
            backend="manual"
        fi
    return 0
}

running() {
    ps ax|grep bot|grep -v grep|grep -v ./cloudbot
    return $?
}

setcommands() {
    if [ "$backend" == "daemon" ]; then
        start = "daemon -r -n cloudbot -O ./bot.log python ./bot.py"
        stop="daemon -n cloudbot --stop"
        restart="./cloudbot stop > /dev/null 2>&1 && ./cloudbot start > /dev/null 2>&1"
        pid="pidof /usr/bin/daemon"
    elif [ "$backend" == "screen" ]; then
        start="screen -d -m -S cloudbot -t cloudbot python ./bot.py > ./bot.log 2>&1"
        stop="kill `pidof /usr/bin/screen`"
        restart="./cloudbot stop > /dev/null 2>&1 && ./cloudbot start > /dev/null 2>&1"
        pid="pidof /usr/bin/screen"
    elif [ "$backend" == "manual" ]; then
}