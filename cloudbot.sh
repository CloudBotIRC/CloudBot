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

locatefiles() {
    botfile="/bot.py"
    botfile=$(pwd)$botfile
    logfile="/bot.log"
    logfile=$(pwd)$logfile
}

running() {
    if [[ $(ps aux|grep bot.py|grep -v grep|grep -v daemon|grep -v screen) != "" ]]; then
        true
    else
        false
    fi
}

checkbackend() {
        if dpkg -l| grep ^ii|grep daemon|grep 'turns other' > /dev/null; then
            backend="daemon"
        elif dpkg -l| grep ^ii|grep screen|grep 'terminal multi' > /dev/null; then
            backend="screen"
        else
            backend="manual"
        fi
    return 0
}

setcommands() {
    status() {
        if running; then
            echo "CloudBot is running!"
        else
            echo "CloudBot is not running!"
        fi
    }
    clear() {
        : > $logfile
    }
    if [ "$backend" == "daemon" ]; then
        start() {
            daemon -r -n cloudbot -O $logfile python $botfile
        }
        stop() {
            daemon -n cloudbot --stop
        }
    elif [ "$backend" == "screen" ]; then
        start() {
            screen -d -m -S cloudbot -t cloudbot python $botfile > $logfile 2>&1
        }
        stop() {
            proc=`ps ax|grep -v grep|grep screen|grep $botfile`
            pid=`top -n 1 -p ${proc:0:5} | grep ${proc:0:5}`
            kill $pid
        }
    elif [ "$backend" == "manual" ]; then
        start() {
            $botfile
        }
        stop() {
            proc=`ps ax|grep -v grep|grep python|grep $botfile`
            pid=`top -n 1 -p ${proc:0:5} | grep ${proc:0:5}`
            kill $pid
        }
    fi
}

processargs() {
    case $1 in
        start)
            if running; then
                echo "Cannot start! Bot is already running!"
            else
                echo "Starting... ($backend)"
                start
            fi
        ;;
        stop)
            if running; then
                echo "Stoppinging... ($backend)"
                stop
            else
                echo "Cannot stop! Bot is not already running!"
            fi
        ;;
        restart)
            if running; then
                echo "Restarting... ($backend)"
                stop
                start
            else
                echo "Cannot restart! Bot is not already running!"
            fi
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
    usage="./cloudbot {start|stop|restart|clear|status}"
    locatefiles
    checkbackend
    setcommands
    processargs $1
}

main $*