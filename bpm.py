#!/usr/bin/env python
DOC = ''' This program detects bpm for mp3 files. It relies on lame and soundstretch being
installed on your system. Note that the bpm detection algorithm in soundstretch and by 
extension this program, currently is significantly worse than in many dedicated bpm 
detection programs available on the win32 platform


Usage: 

    %s <filename>
    
-or pipe filenames to it.

Example:

    find . -name "*.mp3"| %s\n
    
You can also make it include the bpm rating in the file name:

     %s --rename afile.mp3
     
If a bpm of 178 bpm was generated, that file would be renamed to:

     afile 178bpm.mp3
     
     
''' % (__file__, __file__, __file__)

import os
import pipes
import select
import shutil
import subprocess
import sys
import tempfile
 
## Define the window for sane bpm values. This may depend on genre of music. ##
BPM_WINDOW_MAX = 240
# Do not change this one
BPM_WINDOW_MIN = BPM_WINDOW_MAX/2
###############################################################################

import argparse
parser = argparse.ArgumentParser(description=DOC)
parser.add_argument("--rename", action="store_true", dest="RENAME",help="bpm value will be added to file name")
parser.add_argument("--quiet", action="store_true", dest="QUIET",help="just output bpm in whole beats")
parser.add_argument('--infile', type = argparse.FileType('r'), default=sys.stdin)
parser.add_argument('file_names',nargs="*")


args = parser.parse_args()

def _get_bpm_from_soundstretch(output):
    """Gets bpm value from soundstretch output"""
    
    output = output.split("\n")
    for line in output:
        if 'Detected BPM rate ' in line:
            bpm = line[18:]
            return float(bpm)
    return None # Could not parse output

def fit_bpm_in_window(bpm_suggestion):
    """Double or halve a bpm suggestion until it fits inside the bpm window"""
    
    if bpm_suggestion is not None:
        while bpm_suggestion < (BPM_WINDOW_MIN):
            bpm_suggestion = bpm_suggestion * 2
        while bpm_suggestion > (BPM_WINDOW_MAX):
            bpm_suggestion = bpm_suggestion / 2
    return bpm_suggestion
    
def analyze_mp3(mp3filespec):
    """Uses lame and soundstretch to analyze an mp3 file for its bpm rate"""
    
    # Make a temporary working directory for storing the wav file
    # that soundstretch should analyze
    workingdir = tempfile.mkdtemp()
    wavfilespec = workingdir + "/tempwavfile.wav"
    
    # Use lame to make a wav representation of the mp3 file to be analyzed
    wav_command = 'lame --decode %s %s' % (mp3filespec, wavfilespec)
    subprocess.call([wav_command], shell=True, stderr=open(os.devnull, 'w'))
    
    # Call soundstretch to analyze the wav file
    bpm_command = 'soundstretch %s -bpm' % wavfilespec
    p = subprocess.Popen([bpm_command], shell=True,stdout=subprocess.PIPE)
    output = p.communicate()[0]
    
    # Delete temporary working directory and its contents
    shutil.rmtree(workingdir)

    bpm_suggestion =  _get_bpm_from_soundstretch(output)

    return fit_bpm_in_window(bpm_suggestion)

def process_input(mp3filespec):
    bpm_suggestion = analyze_mp3(pipes.quote(mp3filespec))
    if bpm_suggestion is None:
        print "Unable to detect bpm for file %s" % mp3filespec

    else:
        if args.QUIET:
                print str(int(round(bpm_suggestion)))
        else:
            print "BPM rate for %s is estimated to be %s " % (mp3filespec, bpm_suggestion)
        if args.RENAME:
            src = mp3filespec
            dst = os.path.splitext(mp3filespec)[0] + " %sbpm" + os.path.splitext(mp3filespec)[1]
            dst = dst % str(int(round(bpm_suggestion)))
            print "%s -> %s" % (src,dst)
            shutil.move(src,dst)
if args.file_names:
    pass
if __name__ == "__main__":
    if args.file_names:
        mp3filespecs = args.file_names
    #FIXME checking for piped input has changed, make it the other way instead
    # not sys.stdin.isatty():
    elif select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []): # input is piped to program
        print "input is piped"
        mp3filespecs = lines = args.infile.readlines()
    else: # No pipe and no input file, print help text and exit
        print DOC
        sys.exit()
    for mp3filespec in mp3filespecs:
        print "processing %s" % mp3filespec
        process_input(mp3filespec.rstrip('\n'))