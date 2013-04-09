bpm-counter
===========

A script that wraps soundstretch and lame into a command that takes an mp3 file as input and outputs the bpm.

It needs soundtretch and lame to be installed.

Soundstretch can do bpm analysis on soundfiles on Linux. However:

    x It needs wav rather than mp3 files.
    x For my music it sometimes report half the correct bpm


Internally, it converts the mp3 into temporary wav file with lame, runs soundstretch on the file, gets the bpm guess from soundstretch and fits that into a window of bpms.
