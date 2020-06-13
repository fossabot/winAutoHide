# winAutoHide
Automatically hide files/folders that match a regular expression

## Introduction

winAutoHide can hide files automatically on a given time interval.
It uses regular expressions to allow you to specify exactly which files you want to hide.
Once configured it can run in the background and hide files either just when you want it to or automatically at a regular interval after the system startup.

The program was originally developed to mirror the behaviour of Linux to hide files that begin with a dot.
This behaviour is enabled by default.

## How to use
![Image of the application](https://image.ibb.co/fgyN1z/win_Auto_Hide.png)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fjarikmarwede%2FwinAutoHide.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fjarikmarwede%2FwinAutoHide?ref=badge_shield)

### First time setup
1. Download the latest version on the [release page](https://github.com/jarikmarwede/winAutoHide/releases)
2. Move the executable to a folder that only contains that file (for example "C:/Users/username/Documents/winautohide")
3. Start the program
4. Adjust the settings and select the directories you want the hiding to apply to
5. Click "Start"

### Features
The Pattern option lets you define the [Regular Expression](https://en.wikipedia.org/wiki/Regular_expression#Patterns) that is used to find files/folders that should be hidden.

The Frequency option specifies the interval at which the program should scan the folders for the pattern.
It is specified in seconds with -1 meaning starting the program only once, 0 meaning no timeout and everything greater than that being the time between scans.

The "Start" button starts the scanning process and closes the window.
It also saves the current settings.

The system startup buttons add or remove the program from the startup folder of the current user.
This option currently only works when you have [Python](https://www.python.org/downloads/) installed globally.

## Development
The program is built solely with the Python standard library which means that it does not have any requirements except for Python.
To work on it just clone it with git and install [Python 3](https://www.python.org/downloads/) if you haven't already.

To compile the program into an executable (.exe file) [pyinstaller](https://www.pyinstaller.org/) is used.
After you have installed it you can run `pyinstaller -F -w "winautohide.pyw"` which will output the exe file in the dist directory.

## License
This repository uses the MIT License. A copy of it can be found in [LICENSE](https://github.com/jarikmarwede/winAutoHide/blob/master/LICENSE).


[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fjarikmarwede%2FwinAutoHide.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fjarikmarwede%2FwinAutoHide?ref=badge_large)