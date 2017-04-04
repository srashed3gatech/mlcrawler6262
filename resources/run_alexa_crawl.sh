#!/bin/bash
# Sleep for 5 seconds. If you are starting more than one tmux session
#   "at the same time", then make sure they all sleep for different periods
#   or you can experience problems
/bin/sleep 5
# Ensure the environment is available
source /home/USERNAME/.bashrc
# There has to be tmux session named alexa
# if not (first time) create one: /usr/bin/tmux new-session -d -s alexa
# to check tmux open session: tmux ls
/usr/bin/tmux a -t alexa
# ...and control the tmux session (initially ensure the environment
#   is available, then run commands)
/usr/bin/tmux send-keys -t alexa ". ~/.venv/main/bin/activate" C-m
/usr/bin/tmux send-keys -t alexa "cd ~/mlcrawler6262/crawler/crawler-scrapy/alexatop/" C-m
/usr/bin/tmux send-keys -t alexa "python run_alexa.py > ./run_log.log 2>&1 & echo $! > run.pid" C-m

#. ~/.venv/main/bin/activate
#cd ~/mlcrawler6262/crawler/crawler-scrapy/alexatop/
#python -V
#python ~/test_me.py
#scrapy crawl alexa
