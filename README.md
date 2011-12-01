next
====

General
-------

next is a small tool that helps you manage your tv-show watching habits.
It keeps a local sqlite database holding information about shows you watch
and which season and ep you're currently at. It allows you to play an ep
of a show of your choice, or just starts up a random ep. next features a
fully functional TUI to manage your local database.

Requirements
------------

next itself uses basic python and should work in python 2.6 and above. 

To be able to play video from the commandline a commandline video player
is required. I myself use mplayer but since you specify your own 
commandline to start video's with (see Configuration), you can use
whatever you want!

Because next uses the TVRage database to retrieve show information you need to
install the tvrage python module. The easiest way to install this module is
using the python-setuptools package:

$ sudo easy_install python-tvrage

Other methods can be found on pypi:

http://pypi.python.org/pypi/python-tvrage/0.1.4

For the configuration files we use the XDG Base Directory Specification (see
http://bit.ly/tulYTA). This needs the package python-xdgapp to be installed, you
can probably find this in your distro's repository somewhere.

Installation
------------

First of all, make sure you've read the Requirements section above to make sure
you have all the right libraries.

Since next is just a small python script, installing it is really easy.
Just checkout the source somewhere (we'll use ~/src/ as an example) and
put next.py in your path:

user@box$ git clone git://github.com/Sakartu/next.git  
user@box$ sudo ln -s ~/src/next/next.py /usr/bin/next

After this next will be at your disposal from your terminal. That's the
installation that's required :)

Configuration
-------------

Out of the box next will look in ~/.config/next/ to find it's configurationfile.
You can put it elsewhere, if you want to, just use the -c flag to specify
the new location. In the configurationfile we have a few options that 
we'll discuss below:

Option | Explanation | Optional? | Default
-------|-------------|-----------|--------
player_cmd | This is the commandline that next will use to start an episode | no | totem
database_path | If you want your database to reside somewhere other than in show_path, you can specify it here | yes | ~/downloads/series
show_path | This is your series directory, something like ~/downloads/series/ | no | ~/downloads/series/
unstructured_mode | Set this option to True if you have all your eps (from every show) in a single download dir | yes | False

There is a documented example configuration file in the repository in the conf/
dir.

TUI manual
----------

The TUI functions have their own documentation. If you start the TUI and type
help <command> you can learn some more about a command.
