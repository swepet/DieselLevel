# DieselLevel
-----------------
Python3 program for raspberry pi, takes a picture of a diesel heater fueal tank and publishes the percent remaining to a mqtt topic for home assistant.

A small project. I wrote for my diesel heater.
A Raspberry pi zero with a camera attached. Takes a picture of the fuel tank for my diesel heater.
It crops out a part of the image, turns it black and white and calculates the percent of black.
The black is the diesel, and it publishes the percent remaining to a mqtt topic for homeassistant.

diesel_heater_setup.png <-- Picture of my setup with the raspberry pi, there is led lights behind the fuel tank.

diesel_tank.jpg <-- Picture taken by the raspberry pi camera

diesel_crop.jpg <-- Program crops a strip of the fuel tank

diesel_bw.jpg <-- Program turns the strip to BW, and counts the percent black wich is the diesel

Fun fact, i also use the raspberry pi to turn on and off the heater. 
The 433mhz control signals from the remote i have recorded and plays back using the rpitx project.

2024-11-02
by Peter Lehnér (petleh82 @ gmail.com)
