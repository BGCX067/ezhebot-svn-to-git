#!/bin/bash
# runs MyBot against RageBot sample bot
# pass map # as a parameter, for instance rage.sh 1
java -jar tools/PlayGame.jar maps/map$1.txt 1000 200 log.txt "java -jar example_bots/RageBot.jar" "python2.5 MyBot.py --log MyBot.log" | python visualizer/visualize_localy.py
