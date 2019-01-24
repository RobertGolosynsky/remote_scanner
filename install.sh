#!/bin/bash
set -e


email_regex="^[a-z0-9!#\$%&'*+/=?^_\`{|}~-]+(\.[a-z0-9!#$%&'*+/=?^_\`{|}~-]+)*@([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z0-9]([a-z0-9-]*[a-z0-9])?\$"
port_regex="^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
yes_no_regex="^[YyNn]$"

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



# Presetup

echo "export PATH=$PATH:~/.local/bin" > ~/.bash_rc
source /home/pi/.bash_rc

sudo apt-get -y update
sudo apt-get -y upgrade

# pull repo

sudo apt-get -y install git
sudo apt-get -y install python3-pip
sudo rm -rf remote_scanner
git clone https://github.com/RobertGolosynsky/remote_scanner.git



# Decoding SendGrid api key, recorging email for reports, APN
cd remote_scanner
cat banner.txt

echo "REMOTE SCANNER SETUP"

choice=$(ask "Do you posses the password for the included SendGrid API key?(y/n)" $yes_no_regex)
case "$choice" in 
  y|Y ) 
		git clone https://github.com/nodesocket/cryptr.git
		sudo rm /usr/local/bin/cryptr
		sudo ln -s "$PWD"/cryptr/cryptr.bash /usr/local/bin/cryptr
  		enc_key_name="sendgrid.key.aes"
		c=1
		quest="Enter password"
		while : ; do
			if [[ "$c" -eq 1 ]]; then
		    	read -p "$quest:" password
		    else 
		    	read -p "$quest (try $c):" password
			fi
			if echo $password | md5sum --status -c pass.md5; then
			    break
			fi
			((c++))
		done
		$("CRYPTR_PASSWORD=$password cryptr decrypt $enc_key_name")
		api_key=$(head -n 1 ${nc_key_name%.*})
		echo "Using decrypted Sendgrid api key: $api_key"
;;
  n|N ) 
		api_key=$(ask "Type in your SendGrid API key (from sendgrid console)" ".*")
;;
  * ) cat picka.chu;;
esac


recipient=$(ask "Reports email (reports@example.com)" $email_regex)
apn=$(ask "APN of the GPRS provider (usually url)" ".*")

# setup config.py

uart_port="/dev/serial0"

python_config_file=config.py

cp config.py.template $python_config_file 
sed -i -e "s|<RECIPIENT>|$recipient|g" $python_config_file
sed -i -e "s|<SENDGRID_APIKEY>|$api_key|g" $python_config_file

sed -i -e "s|<SERIAL_PORT>|$uart_port|g" $python_config_file
sed -i -e "s|<RAW_DATA_FILE>|raw_data|g" $python_config_file
sed -i -e "s|<FLAT_DATA_FILE>|flat_data|g" $python_config_file
sed -i -e "s|<IMAGE_FILE>|graph|g" $python_config_file


# install python3 requirements
pip3 install pipreqs
pipreqs --force .
pip3 install -r requirements.txt 

# install trl-sdr requirements

sudo apt-get -y install cmake
sudo apt-get -y install build-essential
sudo apt-get -y install libusb-1.0-0-dev

rm -rf rtl-sdr
git clone git@github.com:keenerd/rtl-sdr.git

cd rtl-sdr/
mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON
make
sudo make install

sudo ldconfig

sudo cp ../rtl-sdr.rules /etc/udev/rules.d/

blacklist="blacklist-rtl.conf"
echo 'blacklist dvb_usb_rtl28xxu' > $blacklist
echo 'blacklist rtl2832' >> $blacklist
echo 'blacklist rtl2830' >> $blacklist
sudo mv $blacklist /etc/modprobe.d

# enable serial
sudo raspi-config nonint do_serial 2


# setup ppp (apn required)
sudo apt-get -y install ppp screen elinks

ppp_config="rnet"
uart_port_escaped="${uart_port//\//\\/}"

cp ppp.template $ppp_config 
sed -i -e "s/<APN>/$apn/g" $ppp_config
sed -i -e "s/<UART_PORT>/$uart_port_escaped/g" $ppp_config
sudo mv $ppp_config /etc/ppp/peers/$ppp_config

sudo usermod -a -G dip pi




# setup service 
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


# Promt user for enabling the service

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

