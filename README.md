next
====

General
-------

next is a small tool that helps you manage your tv-show watching habits.
It keeps a local sqlite database holding information about shows you watch
and which season and ep you're currently at. It allows you to play an ep
of a show of your choice, or just starts up a random ep. next features a
fully functional TUI to manage your local database.

TL;DR
-----
git clone from github; install dependencies (python-tvrage, python-xdgapp
\<optional\>, pyreadline \<optional\>); run once ("next" if next.py is in your
PATH); change configuration found in ~/.config/next/next.conf; add some shows
using "next -a"; watch eps using "next \<partial show name\>"; make sure the
database is updated regularly either by watching with internet turned on or by
running "next -u" when you're online.

Requirements
------------

next itself uses basic python and should work in python 2.7 and above.

To be able to play video from the command line a command line video player
is required. I myself use mplayer but since you specify your own
command line to start video's with (see Configuration), you can use
whatever you want!

Because next uses the TVRage database to retrieve show information you need to
install the tvrage python module. The easiest way to install this module is
using the python-pip package:

    user@box$ sudo pip install python-tvrage

Other methods can be found on pypi:

    http://pypi.python.org/pypi/python-tvrage/0.1.4

For the configuration and database files next can use the XDG Base Directory
Specification (see http://bit.ly/tulYTA). This needs the package
python-xdgapp to be installed, you can probably find this in your distro's
repository somewhere. pip may also have python-xdgapp although this was not the
case when I checked it last time. You can try using:

    user@box$ sudo pip install python-xdgapp

If you run next under Windows installing python-xdgapp is quite useless, next
will default to ~/.next/next.conf for the configuration file and to the show dir
specified in the configuration file for the database.

To have tab-completion support in the TUI in Windows, the pyreadline library is needed. It can be installed using:

    user@box$ sudo pip install pyreadline

Installation
------------

First of all, make sure you've read the Requirements section above to make sure
you have all the right libraries.

Since next is just a small python script, installing it is really easy.
Just checkout the source somewhere (we'll use ~/src/ as an example) and
put next.py in your path:

    user@box$ git clone git://github.com/Sakartu/next.git src/next
    user@box$ sudo ln -s ~/src/next/next/next.py /usr/bin/next

After this next will be at your disposal from your terminal. That's all the
installation that's required :)

Updating
--------

To update next you can simply pull the latest version from github using:

    user@box$ cd src/next; git pull

Configuration
-------------

Out of the box next will use the XDG Base Directory specification (see
http://bit.ly/tulYTA) to find it's configuration file and database. If the XDG
Base Directory isn't available next will default to ~/.next/next.conf for the
configuration file. If no alternate path is specified in the configuration file
next will default to the specified show_path.

If you want you can put the configuration elsewhere, just use the -c flag to
specify another location. In the configuration file there are a few options that
we'll discuss below:

Option | Explanation | Optional? | Default
-------|-------------|-----------|--------
show_path | This is your series directory, something like ~/downloads/series/ | no | ~/downloads/series/
database_path | If you want your database to reside somewhere other than the default, you can specify it here | yes | ~/downloads/series
player_cmd | This is the command line that next will use to start an episode | no | totem
suppress_player_output | Set this option to True if you want next to suppress all (commandline) output from the player| yes | True
unstructured_mode | Set this option to True if you have all your eps (from every show) in a single download dir | yes | False
post_hook | A comma-separated list of scripts to call after an ep is watched. See the config file for possible parameters. | yes | /bin/rm {path}
length_detection | The number of minutes you have to watch an ep before next will ask you to update the database. | yes | 0
ask_another | Set this option to False if you don't want next to ask to play another ep | yes | True
check_new_version | Set this option to False if you don't want next to check for a new version while playing an episode | yes | True
auto_update_next | Set this option to False if you don't want next to auto update to a new version if a new version is available. Can be used in combination with the above check_new_version | yew | True
git_path | If you want to use a custom git installation (or if git isn't in your PATH), put the path to git here | yes | <empty>

There is a documented example configuration file in the repository in the config/
dir. A default configuration file will also be generated if no file can be
found.

TUI manual
----------

The TUI functions have their own documentation. If you start the TUI and type
help <command> you can learn some more about a command.

Completion
----------

next also features bash commandline completion. This will complete the names of your
shows when next is used directly from your terminal, without the TUI. For instance,
to play the next ep of the show "White Collar", just execute the following command:

    user@box$ next white

If you press <tab> just after typing "wh" it will complete to white for you.
The completion file found in ./completion/ can be put in /etc/bash_completion.d/
to provide tab completion for your shows.

If you want to enable the completion features right away, just use the following
commands:

    user@box$ sudo cp ~/src/next/completion/next /etc/bash_completion.d/
    user@box$ . /etc/bash_completion.d/next

The last command will "source" the completion file to enable it immediately.

next features fuzzy show name matching, meaning that if you have no other shows
that have the letters "wh" in them, in that order, typing

    user@box$ next wh

is enough to start the next "White Collar" ep; the completion is only a nice
addition, not a requirement.

XBMC
----

If you want to use next alongside XBMC you may run into the problem of the two
databases getting out of sync: if you watch something in XBMC then next doesn't
know about it and vice versa. The first part of this problem is solved by the
XBMC service addon found in ./xbmc/. If you put this directory in your XBMC
addons directory (http://wiki.xbmc.org/index.php?title=userdata), enable it in
XBMC and configure it correctly, each time you watched an ep in XBMC you will be
prompted on whether you want to update next as well. If you use this plugin with
Raspbmc (XBMC for the raspberry pi) you will need to make your next database
available locally somehow. As sqlite3 needs to be able to lock the database to
be able to write to it, using Samba may not work as it has not implemented the
locking mechanism properly, so I suggest using NFS.

Usage
-----

Some basic usage has already been discussed in the previous sections. Here follows
a more complete guide.

The first thing you need to do is add a show to the database. Adding a show looks
up the show by name in the (remote) TVRage database and adds all the
information it can find to the local database. The internal episode cache gets
updated as you watch but you can update the cache manually (if, for instance,
you almost always watch in an offline setting) using the -u flag. Make sure the
cache gets updated regularly, otherwise next won't know what to do with new eps
as they come out! Updating the database can be done manually (by running next
with the -u flag) or automatically if you play shows while an internet
connection is available. Playing a show has already been covered in the bash
completion part above; you just start next with some hints as to which show you
mean as parameters:

    user@box$ next white

will start the next ep of White Collar for you (provided you added it to the
database)

next will look for eps for your shows in the given location in the configuration
file. If, for some reason, you have the eps for a specific show in another location
you can add this manually by using the "--add_location" (CLI) or "add_location"
(TUI) commands.

A final feature worth mentioning is the scan option. The first time you start next,
after configuring it's options in the config file, you can use the "--scan" (CLI)
or "scan" (TUI) command to scan the specified show path for shows and add them
to the database. This will take you through a wizard to add shows and specify what
ep you are in what season.

Credits
-------

Credits go out to:

-	ewoud for helping me in the development and guiding me towards a more pythonesque next :)
-   atum for bèta-testing one of the earlier versions
-   akaIDIOT for providing me with nice feature requests
-   Emthigious for being the first one brave enough to give it a whirl
