1. plugin an ethernet cable 
2. Connect through SSH
	1. open a terminal and run
		```
		ssh pi@raspberrypi.local
		```
			Note: 	if this fails to resolve hostname, make sure that the LEDs of 
				ethernet flashes ( means the pi booted successfully), if not
				then wait until they start flashing, if they are flashing and
				you receive the error then use an android app called Fing to 
				perform a network scan to locate the raspberrypi IP address 
				and use that ip instead of 'raspberrypi.local'
		when it asks for password enter "raspberry" ( or the password you set )
	2. config wlan 
		1. 	Run `sudo raspi-config`
		2. 	choose first item in the menu
		3. 	choose wlan
		4. 	enter your wlan SSID then press enter
		5. 	enter your wlan password then press enter


3. make sure that the pi connected successfuly to Wlan
	when run `iwconfig` command
	you should see something like
		```
		lo        no wireless extensions.

		eth0      no wireless extensions.

		wlan0     IEEE 802.11  ESSID:"orange-Mou2" ***Note: your ssid name should be here instead***
			  Mode:Managed  Frequency:2.462 GHz  Access Point: ... 
		```
		