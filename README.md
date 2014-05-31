Pocket_epub
===========

Python utility to transform a Pocket reading list to individual ePub files

Dependencies
============
- CherryPy3
- Jinja2
- ConfigParser
- GNU Wget
- Pandoc
- Python2.7
- Git

Installation
============
If you're on Ubuntu (and likely any other Debian derivative) you can install the dependencies by use the following

$ sudo apt-get install python-cherrypy3 python-jinja2 python-configparser wget pandoc python2.7

Then clone this project somewhere convenient:

$ git clone git@github.com:corani/pocket_epub.git

Setup
=====

1. Get an API key for Pocket (http://getpocket.com/developer/apps/new)
2. Get a PARSER API key for Readability (https://www.readability.com/settings/account)
3. Enter both in settings.dat

Running
=======

Run with ./start

The script will get all articles marked 'unread' from Pocket since the last run. The first time it will get *all* unread articles, which can take a long time (hours)

If you wish to reset the timer, remove the "since" field from settings.dat (it's a UNIX timestamp)

The final ePub files are in the "epub" folder. I share this folder through BitTorrent-Sync (http://www.bittorrent.com/sync/) so the epubs are automatically delivered to all my devices (including a backup on my NAS)
