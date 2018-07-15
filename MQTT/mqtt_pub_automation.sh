#!/bin/sh

echo "Process started at `date`"

#
DATA_DIR=/home/ubuntu/MQTT/sent_files
Backup_DIR=$DATA_DIR/processed/

user_name=iot_mqtt
pwd=Team2Work
topic=solrpnl_01

# Create a file
#python /home/thiagu/Project/MQTT/mqtt_client_pub.py


for entry in "$DATA_DIR"/*.json
do
  # broadcasting the file
  mosquitto_pub -d -u $user_name -P $pwd -t $topic -f $entry

  # Backup the file
  cur_DATE=$(date +%Y%m%d%s)
  fname=`basename $entry`
  bk_file=$Backup_DIR/Bk_"$cur_DATE"_"$fname"
  echo $bk_file
  mv $entry $bk_file
  echo "move file to  :" "$Backup_DIR"
done

echo "Process finished at `date`"
 

