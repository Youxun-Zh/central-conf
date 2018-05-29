#!/bin/sh

current=`pwd`
echo $current

recover_file=$current"/bin/recover_db.py"
server_file=$current"/runserver.py"

python3 $recover_file

python3 $server_file --port=8080
