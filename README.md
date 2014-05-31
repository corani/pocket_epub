Pocket_epub
===========

Python utility to transform a Pocket reading list to individual ePub files

Dependencies
============
 * CherryPy3
 * Jinja2
 * ConfigParser
 * GNU Wget
 * Pandoc
 * Python2.7
 * Git

Installation
============
If you're on Ubuntu (and likely any other Debian derivative) you can install the dependencies by use the following

    $ sudo apt-get install python-cherrypy3 python-jinja2 python-configparser wget pandoc python2.7

Then clone this project somewhere convenient:

    $ git clone git@github.com:corani/pocket_epub.git

Verifying
=========

To verify non of the files have been modified, make sure you have sha1sum and gpg installed and do the following *before* editing any of the files, or running the script. If your gpg isn't configured to automatically fetch public keys, you may have to import my public key with the information below under "Contact".

    $ ./verify

This will calculate a SHA1 hash over each file in the project and verify that those correspond to the hashes signed by me. If you want to hash and sign the project again, run:

    $ ./sign

This will sign the project with *your* gpg key.

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

Contact
=======
Contact me through email at: corani@gmail.com

PGP signed/encrypted email gets priority!

> My public key: http://goo.gl/gms497 (4096 bit RSA, id EF2D5D91)
>
> Fingerprint  : D8D0 9FBE F075 F709 7B52  2F73 326C 2123 EF2D 5D91

