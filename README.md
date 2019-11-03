# Intro
This program was crated as a consequence of Google removable of free Original Storage for the Pixel 4 lineup.
The program copies files from the Android phone's DCIM directory, to a temperary location on the PC
and afterwards transfer them to the second Android device. See the post on the subreddit [r/GooglePixel](https://www.reddit.com/r/GooglePixel/comments/dr1nyh/work_around_to_no_original_quality_backup/).

# Requirements
* Windows 10
* ADB installed and added to path version 1.0.41 ([Guide](https://www.xda-developers.com/install-adb-windows-macos-linux/))
* USB-debugging enabled on both phones ([Guide](https://www.embarcadero.com/starthere/xe5/mobdevsetup/android/en/enabling_usb_debugging_on_an_android_device.html))
* USB-C cable for connection between PC and phone

## Software
 * Python 3.5, 3.6, 3.7, 3.8 (only tested on 3.8)
 * PySimpleGUI
 * PyInstaller (If you wish to create you own exe file)

# Preliminary setup
* Make sure ADB works for both devices (You should see the attached device's serial number with command adb devices in the command prompt)
* Disable Automatic backup in Google Photos on Pixel 4
    * Settings -> Backup and Synchronisation -> disable Backup and Synchronisation

* Download Google Photos HTML5 on Pixel 4
    * Go to photos.google.com in Chrome
    * Press three dots menu in Chrome, click Add to Home screen

* Initial Test: Run the program first with a few pictures and videos to test if the program works correct, before using it normally.

# Basic usage
1. Start android_file_transfer.exe (or launch python script)
2. Attach the source device (e.i. pixel 4)
3. Choose the correct settings on the buttons
4. Press Start
5. When completed, Detach pixel 4 and attach destination device (pixel 2/3)
6. Press Start
7. When finished, close the program.

# NOTES and WARNINGS
* I have only tested this on Nexus 6P and Pixel 2 XL (Do not have a pixel 4 yet)
* I am not in any way responsible for loss of data or damage of the device
* Make sure ADB is at version 1.0.41 (command: adb --version to see version number), I have at frozen operations with version 1.0.40.
* This program was created rather quickly and failed to use the program in the correct way, can resolve in undefined behaviour of the program.
* The copied files are copied to C:\afcTemp, Here you can find the copied files if the operations fail after step 4 and if delete files setting was not chosen.
* If you have any problems or question, feel free to ask, and I will do my best to answer them or resolve the issue.
* The python script has only been tested with Python 3.8, and it is not compatible with Python 2.7 without some tweaking.
