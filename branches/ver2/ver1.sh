#!/bin/bash
# runs MyBot against Ezhebot(version1) bot
# pass map # as a parameter, for instance ver1.sh 1
rm MyBot.log
java -jar tools/PlayGame.jar maps/map$1.txt 1000 200 log.txt "python ezhebot-ver1.py" "python MyBot.py --log MyBot.log" | python visualizer/visualize_localy.py
