#!/usr/bin/env bash

# fail on error
set -e

# install dep
sudo apt install python3 virtualenv lighttpd

# create virtualenv
if [ ! -d "venv" ]; then
  virtualenv -p python3 venv
fi
source venv/bin/activate
pip3 install -r requirements.txt

# create folder and place files
sudo mkdir -p /var/www/temp_app
sudo cp -r ./venv /var/www/temp_app/
sudo cp ./*.py /var/www/temp_app/
sudo cp ./*.sh /var/www/temp_app/
sudo rm /var/www/temp_app/setup.sh
sudo cp -r ./static/ /var/www/temp_app/
sudo cp -r ./templates/ /var/www/temp_app/
sudo chmod 775 /var/www/temp_app/
sudo chown -R www-data:www-data /var/www/temp_app

# pi should be in www-data group
sudo gpasswd -a pi www-data

# www-date need to access i2c
sudo usermod -a -G i2c www-data

# setup cron (root)
sudo crontab -l | grep -v /var/www/temp_app/cron_trigger.sh > /tmp/cron-jobs.txt
echo "*/5 * * * * /var/www/temp_app/cron_trigger.sh" >> /tmp/cron-jobs.txt
sudo cron /tmp/cron-jobs.txt
# if you setup cron as user pi, the database will struggle with permissions

exit 0
