#!/bin/bash
echo
echo "Welcome to:                                                                         "
echo "  ______  __        ______    __    __   _______  .______     ______   .___________."
echo " /      ||  |      /  __  \  |  |  |  | |       \ |   _  \   /  __  \  |           |"
echo "|  ,----'|  |     |  |  |  | |  |  |  | |  .--.  ||  |_)  | |  |  |  | \`---|  |----\`"
echo "|  |     |  |     |  |  |  | |  |  |  | |  |  |  ||   _  <  |  |  |  |     |  |     "
echo "|  \`----.|  \`----.|  \`--'  | |  \`--'  | |  '--'  ||  |_)  | |  \`--'  |     |  |     "
echo " \______||_______| \______/   \______/  |_______/ |______/   \______/      |__|     "
echo " http://git.io/cloudbot                                                 by lukeroge "
echo

checkbackend() {
        if dpkg -l| grep ^ii|grep daemon|grep 'turns other' > /dev/null; then
            backend="daemon"
            echo "backend: daemon"
        elif dpkg -l| grep ^ii|grep screen|grep 'terminal multi' > /dev/null; then
            backend="screen"
            echo "backend: screen"
        else
            backend="manual"
            echo "backend: manual"
        fi
    return 0
}

setcommands() {
    if [ "$backend" == "daemon" ]; then
        start="daemon -r -n cloudbot -O ./bot.log python ./bot.py"
        stop="daemon -n cloudbot --stop"
        pid="pidof /usr/bin/daemon"
    elif [ "$backend" == "screen" ]; then
        start="screen -d -m -S cloudbot -t cloudbot python ./bot.py > ./bot.log 2>&1"
        stop="kill $(pidof /usr/bin/screen)"
        pid="pidof /usr/bin/screen"
    elif [ "$backend" == "manual" ]; then
        start="./bot.py"
        stop="kill $(pidof ./bot.py)"
        restart="./cloudbot stop > /dev/null 2>&1 && ./cloudbot start > /dev/null 2>&1"
    fi
    restart="./cloudbot stop > /dev/null 2>&1 && ./cloudbot start > /dev/null 2>&1"
}

running() {
    ps ax|grep bot|grep -v grep|grep -v ./cloudbot
    return $?
}

processargs() {
    args=$1
    case $args in
    start)
    start
    ;;
    stop)
    stop
    ;;
    restart)
    stop
    start
    ;;
    status)
    status
    ;;
}

main() {
    checkbackend
    setcommands
    processargs
}

main