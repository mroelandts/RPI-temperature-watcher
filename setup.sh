#!/usr/bin/env bash

# fail on error
set -e

# check if update
DEV=0
if [ $1 = "update" ]; then
    DEV=1
    echo "Only updating files."
fi

if [ ${DEV} -eq 0 ]; then
    # install dep
    sudo apt install python3 virtualenv lighttpd

    # create virtualenv
    if [ ! -d "venv" ]; then
         virtualenv -p python3 venv
    fi
    source venv/bin/activate
    pip3 install -r requirements.txt
fi

# create folder and place files
sudo mkdir -p /var/www/temp_app
if [ ${DEV} -eq 0 ]; then
    sudo cp -r ./venv /var/www/temp_app/
fi
sudo cp ./*.py /var/www/temp_app/
sudo cp ./*.sh /var/www/temp_app/
sudo cp ./*.fcgi /var/www/temp_app/
sudo rm /var/www/temp_app/setup.sh
sudo cp -r ./static/ /var/www/temp_app/
sudo cp -r ./templates/ /var/www/temp_app/
sudo chmod 775 /var/www/temp_app/
sudo chown -R www-data:www-data /var/www/temp_app

# user groups
if [ ${DEV} -eq 0 ]; then
    # pi should be in www-data group
    sudo gpasswd -a pi www-data

    # www-date need to access i2c
    sudo usermod -a -G i2c www-data
fi

# slow_poweroff
sudo cp slow_poweroff.sh /usr/local/bin/slow_poweroff.sh

# www-data needs to run sudo for slow_poweroff
sudo cp 010_www-data-poweroff /etc/sudoers.d/010_www-data-poweroff
sudo chmod 440 /etc/sudoers.d/010_www-data-poweroff
sudo chown root:root /etc/sudoers.d/010_www-data-poweroff

# setup cron (root)
if [ ${DEV} -eq 0 ]; then
    # if you setup cron as user pi, the database will struggle with permissions
    sudo crontab -l | grep -v /var/www/temp_app/cron_trigger.sh > /tmp/cron-jobs.txt
    echo "*/5 * * * * /var/www/temp_app/cron_trigger.sh" >> /tmp/cron-jobs.txt
    sudo cron /tmp/cron-jobs.txt
fi

# configure lighttpd
if [ ${DEV} -eq 0 ]; then
    sudo cp 98-temperature-fastcgi.conf /etc/lighttpd/conf-available/
    sudo lighty-enable-mod rewrite
    sudo lighty-enable-mod temperature-fastcgi
    lighttpd -t -f /etc/lighttpd/lighttpd.conf
fi
sudo systemctl restart lighttpd.service

exit 0
