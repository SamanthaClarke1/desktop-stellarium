# Desktop-Stellarium

This app aims to provide a CLI interface, along with some Conky scripts and install scripts, in order to provide an observatory of sorts, right on your desktop!

If you've never heard of conky, you can find it [here](https://github.com/brndnmtthws/conky).
It's a great little tool to display things like clocks or system information on the desktop.

### How does it work?

Two parts.
1) A CLI interface (this application) and
2) Conky scripts that interface with aforementioned CLI interface

That CLI Interface can use local config files, along with command line options, to specify things like your timezone.
Behind the scenes, it utilises skyfield for python3. Maybe take a peek at notes.txt?

---------------------

 Samantha Clarke, Dec 2022
