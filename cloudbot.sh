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

args=$*
usage="./cloudbot {start|stop|restart|clear|status}"

locatefiles() {
    botfile="/bot.py"
    botfile=$(pwd)$botfile
    logfile="/botlog"
    logfile=$(pwd)$logfile
}

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

running() {
    ps ax|grep bot|grep -v grep|grep -v ./cloudbot
    return $?
}

setcommands() {
    if [ "$backend" == "daemon" ]; then
        start() {
            daemon -r -n cloudbot -O $logfile python $botfile
        }
        stop() {
            daemon -n cloudbot --stop
        }
        pid() {
            pidof /usr/bin/daemon
        }
    elif [ "$backend" == "screen" ]; then
        start() {
            screen -d -m -S cloudbot -t cloudbot python $botfile > $logfile 2>&1
        }
        stop() {
            kill $(pidof /usr/bin/screen)
        }
        pid() {
            pidof /usr/bin/screen
        }
    elif [ "$backend" == "manual" ]; then
        start() {
            $botfile
        }
        stop() {
            kill $(pidof $botfile)
        }
        pid() {
            pidof $botfile
        }
    fi
    status() {
        if running; then
            echo "CloudBot is running!"
            pid
        else
            echo "CloudBot is not running!"
        fi
    }
    clear() {
        : > $logfile
    }
}

processargs() {
    case $1 in
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
        clear)
            clear
        ;;
        status)
            status
        ;;
        *)
            echo $usage
        ;;
    esac
}

main() {
    locatefiles
    checkbackend
    setcommands
    processargs $1
}

main $*