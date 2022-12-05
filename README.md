# tinkerBoard_simpleFanControl for Rev1.2

I'm late to the party.
Got an used tinker board rev1.2 recently and had a bit of issues to start with.

1. Downloaded tinker os from https://tinker-board.asus.com/download.html and loaded the os image on to a sd card (16gb) using https://www.balena.io/etcher/ .
1. Got a bit greedy with hp printer drivers, update linux on tinkerboard, but burnt the sdcard.
1. Learnt that power supply is an issue after so much reading (https://forum.armbian.com/topic/5211-solved-asus-tinkerboard-i-need-to-upgrade-psu/).  Be careful supplying power via gpio pins, it can fuse the board if done improperly.
1. With a 5v 3a QC3.0 adapter, the system is better, however the micro usb cable length was culprit further (https://goughlui.com/2014/10/01/usb-cable-resistance-why-your-phonetablet-might-be-charging-slow/).
1. With a shorter cable, the system is stable, with usb keyboard, mouse, hdmi@1080.
1. Ran youtube at 720, the temperatures shot beyond 65C and crashed (may be beyond), had to remove the top cover to cool.
1. Had to buy an tiny fan https://www.pbtech.co.nz/product/SEVRBP0298/Raspberry-Pi-4-Model-B-Official-Case-Fan--Heatsink?qr=GShopping&gclid=EAIaIQobChMIt-fs-a3V-wIVSp1LBR2clQicEAQYASABEgLAH_D_BwE
1. Fixed it to the case, Plugged as per instructions, fan wont turn on.
1. Removed blue (control) cable, fan at full speed, total noise and defeats the purpose of SBC.
1. searched for some code to control fan with PWM, found https://gist.github.com/adamotte/ac272d9facc8097c43144b668587df5f
1. the code is too complex, simplified it to https://github.com/karunakar2/tinkerBoard_simpleFanControl/blob/main/simpleFanControl.py
1. the above is necessary as the fan doesn't have a tacho
1. connected the fan pwm control to gpio pin 32, between two blacks
1. realised python needed an update to version 3 and also ASUS.GPIO module is required (asus tinkerboard download).
1. Not sure what pin to pin number to use in the code, ran 'sudo gpio readall' on terminal (serverbiz.co.kr/product-info/?vid=55)
1. realised cpu pin 239 corresponds to pin 32 and plugged it in the code.
1. updated the code for the variable c_FAN to above pin number, presto, fan runs only when required.
1. sudo python3 /path/to/simpleFanControl.py
1. check if it works and kill it after a while.
1. wanted to load it at startup, so had to create a cron job, so ran following on shell/terminal
1. sudo cp -i /path/to/simpleFanControl.py /bin
1. sudo crontab -e
1. Above command might tell that it doesn't exist for root and will create one, go for it, add following line at the end of the file.
1. @reboot python3 /bin/your_script.py &
1. go for a reboot, check if it works in background.
1. Fork and update, but send me a pull, happy to merge.
1. Log issues so that others get to know if any problems exist and debug accordingly.


# Debug
1. see simpleFan.txt file in temp
1. use the pid to grab std info
1. hint: Linux-specific /proc/<pid>/fd/N
1. N is file descriptors 0, 1 and 2 to whatever they point to (normaly stdin, stdout and stderr)
1. Thanks
