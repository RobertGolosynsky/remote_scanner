#!/bin/bash

ask(){
	
	local ans=""
	c=1
	while : ; do
		if [[ "$c" -eq 1 ]]; then
	    	read -p "$1:" ans
	    else 
	    	read -p "$1 (try $c):" ans
		fi
		[[ $ans =~ $2 ]] && break
		((c++))
	done
	echo "$ans"
	return 0
}

enable_service(){
	sudo systemctl enable $1
}

#1. pull repo

sudo apt-get -y install git
sudo apt-get -y install python3-pip

git clone https://github.com/RobertGolosynsky/remote_scanner.git

cd remote_scanner

#2. setup config.py
email_regex="^[a-z0-9!#\$%&'*+/=?^_\`{|}~-]+(\.[a-z0-9!#$%&'*+/=?^_\`{|}~-]+)*@([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z0-9]([a-z0-9-]*[a-z0-9])?\$"
port_regex="^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
uart_port="/dev/serial0"


echo "REMOTE SCANNER SETUP"

recipient=$(ask "Reports email (reports@example.com)" $email_regex)
api_key=$(ask "SendGrid API key (from sendgrid console)" ".*")
apn=$(ask "APN of the GPRS provider (usually url)" ".*")

python_config_file=config.py

cp config.py.template $python_config_file 
sed -i -e "s|<RECIPIENT>|$recipient|g" $python_config_file
sed -i -e "s|<SENDGRID_APIKEY>|$api_key|g" $python_config_file

sed -i -e "s|<SERIAL_PORT>|$uart_port|g" $python_config_file
sed -i -e "s|<RAW_DATA_FILE>|raw_data|g" $python_config_file
sed -i -e "s|<FLAT_DATA_FILE>|flat_data|g" $python_config_file
sed -i -e "s|<IMAGE_FILE>|graph|g" $python_config_file


#3. install python3 requirements
pip3 install pipreqs
echo "export PATH=$PATH:~/.local/bin" > ~/.bash_rc
source /home/pi/.bash_rc
pipreqs --force .
pip3 install -r requirements.txt 

#4. install atp-get requirements

sudo apt-get install -y rtl-sdr
sudo apt-get install libatlas-base-dev
#5. enable serial
sudo raspi-config nonint do_serial 2


#6. setup ppp (apn required)

ppp_config="rnet"
uart_port_escaped="${uart_port//\//\\/}"

cp ppp.template $ppp_config 
sed -i -e "s/<APN>/$apn/g" $ppp_config
sed -i -e "s/<UART_PORT>/$uart_port_escaped/g" $ppp_config
sudo mv $ppp_config /etc/ppp/peers/$ppp_config

sudo usermod -a -G dip pi
sudo apt-get install -y ppp screen elinks



#7. setup service 
service_name="remote_scanner"
service_file="$service_name.service"
service_description="Remote scanner service"
working_dir=$(pwd)
working_dir="${working_dir//\//\\/}"

cp service.template $service_file 
sed -i -e "s/<SERVICE_DESCRIPTION>/$service_description/g" $service_file
sed -i -e "s/<MAIN_FILE>/main.py/g" $service_file
sed -i -e "s/<DIR>/$working_dir/g" $service_file
sudo mv $service_file /etc/systemd/system/$service_file


#8. Promt user for enabling the service
yes_no_regex="^[YyNn]$"
choice=$(ask "Should the service be started on boot?(y/n)" $yes_no_regex)
case "$choice" in 
  y|Y ) enable_service $service_name;;
  n|N ) echo ok.;;
  * ) cat picka.chu;;
esac

echo "Installation successful. 
Use 'sudo systemctl start|stop|restart $service_name' to control the service."

choice=$(ask "Reboot the device to finish instalation. Should reboot now?(y/n)" $yes_no_regex)
case "$choice" in 
  y|Y ) sudo reboot;;
  n|N ) echo ok.;;
  * ) cat picka.chu;;
esac

