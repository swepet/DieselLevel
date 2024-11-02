# DieselLevel
-----------------
Python3 program for raspberry pi, takes a picture of a diesel heater fueal tank and publishes the percent remaining to a mqtt topic for home assistant.

A small project. I wrote for my diesel heater.
A Raspberry pi zero with a camera attached. Takes a picture of the fuel tank for my diesel heater.
It crops out a part of the image, turns it black and white and calculates the percent of black.
The black is the diesel, and it publishes the percent remaining to a mqtt topic for homeassistant.


2024-11-02
by Peter Lehnér (petleh82 @ gmail.com)
