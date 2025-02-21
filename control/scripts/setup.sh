#!/bin/bash
set -e

echo "Installing docker"
if [ -x "$(command -v docker)" ]; then
    	echo "Skip, already installed"
else
    	curl -fsSL https://get.docker.com -o get-docker.sh
	sudo sh ./get-docker.sh
	rm get-docker.sh
	sudo groupadd docker
	sudo usermod -aG docker $USER
	newgrp docker
	sudo systemctl enable docker.service
	sudo systemctl enable containerd.service
fi
echo "Installing pip"
if [ -x "$(command -v pip)" ]; then
    	echo "Skip, already installed"
else
 	sudo apt-get -y install python3-distutils
 	sudo apt-get -y install python3-apt
	curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    	python get-pip.py
    	rm get-pip.py
   
fi

echo "Installing python packages requirements"

pip install -r requirements.txt

cd ~/
if [ ! -d "app" ]
then
	mkdir app
fi



# create project directory
