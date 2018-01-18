#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from numpy import *
from optparse import OptionParser

###########################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###########################
#
# Todo: 
# - Check for whitespace (option ws) does not work properly
# - Add tab check

###########################

__author__ = 'M. Lofverstrom'
__email__  = 'marcusl-at-ucar.edu'
__status__ = 'Development'


class fileServer(object):

    def __init__(self,
                 src_dir,
                 test,
                 max_length,
                 extension,
                 comment,
                 silent):


        self.src_dir = src_dir
        self.max_length = max_length
        self.extension = extension
        self.comment = comment
        self.silent = silent


        if test in ['f','full']: 
            self.description = 'any lines exceeding character limit'
            self.long_name = 'full'
            self.test = 'full'

        elif test in ['r','rc','regular-code']: 
            self.description = 'regular code lines (w/o comments) exeeding character limit'
            self.long_name = 'regular code line w/o comments'
            self.test = 'regular'


        elif test in ['c','cc','comment']:
            self.description = 'pure comment lines exceeding character limit'
            self.long_name = 'pure comment lines'
            self.test = 'comment'


        elif test in ['t','tc','trailing-comment']:
            self.description = 'lines with trailing comments exceeding character limit'
            self.long_name = 'lines with trailing comments'
            self.test = 'trailing comment'


        elif test in ['w','ws','whitespace']:
            self.description = 'lines with trailing whitespace exceeding character limit'
            self.long_name = 'lines with trailing whitespace'
            self.test = 'whitespace'


        else: 
            print 'Test %s is not a valid option!'%(test)
            print 'Use flag -h [--help] to see instructions'
            self.exit_script()
            

        self.success = True


    def exit_script(self):
        sys.exit()


    def write_settings(self,kill=False):

        pad = 17
        newline()
        print 'Settings:'
        print 'src_dir: '.ljust(pad),self.src_dir
        print 'test: '.ljust(pad),self.test
        print 'description: '.ljust(pad),self.description 
        print 'character limit: '.ljust(pad),self.max_length
        print 'extension: '.ljust(pad),self.extension
        print 'comment: '.ljust(pad),self.comment
        print 'silent:  '.ljust(pad),self.silent
        newline()

        if kill is True:
            print 'Exiting script (turn off options --write_settings to continue)\n\n'
            self.exit_script()


###########################


def tree(dir, padding, print_files=False, isLast=False, isFirst=False):

    """
    Tree structure of path specified on command line
    Based on code written by Doug Dahms
    """

    code = 'utf8'

    if isFirst:
        print padding.decode(code)[:-1].encode(code) + dir
    else:
        if isLast:
            print padding.decode(code)[:-1].encode(code) + '└── ' + \
                os.path.basename(os.path.abspath(dir))
        else:
            print padding.decode(code)[:-1].encode(code) + '├── ' + \
                os.path.basename(os.path.abspath(dir))

    files = []
    if print_files:
        files = os.listdir(dir)
    else:
        files = [x for x in os.listdir(dir) if os.path.isdir(dir + os.sep + x)]
    if not isFirst:
        padding = padding + '   '
    files = sorted(files, key=lambda s: s.lower())
    count = 0
    last = len(files) - 1
    for i, file in enumerate(files):
        count += 1
        path = dir + os.sep + file
        isLast = i == last
        if os.path.isdir(path):
            if count == len(files):
                if isFirst:
                    tree(path, padding, print_files, isLast, False)
                else:
                    tree(path, padding + ' ', print_files, isLast, False)
            else:
                tree(path, padding + '│', print_files, isLast, False)
        else:
            if isLast:
                print padding + '└── ' + file
            else:
                print padding + '├── ' + file



def write_tree(fs,write_files=False):

    """
    Tree structure of path specified on command line
    Based on code written by Doug Dahms
    """

    path = fs.src_dir

    if write_files is False:
        # print directories
        if os.path.isdir(path):
            tree(path, '', False, False, True)

    else:
        # print directories and files
        if os.path.isdir(path):
            tree(path, '', True, False, True)



###########################


def newline():
    print ''


def print_line(dataFile,line,length,ii):
    print dataFile,'(line %s, columns %s):'%(ii+1,length)
    print line+'\n'


def count_columns(fs,dataFile):

    with open(dataFile, 'rb') as fin:

        ii = 0
        for line in fin:
            if fs.test == 'full':
                ## Check all lines exceeding character limit

                if len(line) >= fs.max_length:
                    fs.success = False
                    print_line(dataFile,line,len(line),ii)


            if fs.test == 'regular':
                ## Check length of regular code lines (w/o comments)

                if len(line.split(fs.comment)) == 1 and len(line) > fs.max_length:
                    fs.success = False
                    print_line(dataFile,line,len(line),ii)


            if fs.test == 'comment':
                ## Check length of comments, including indented comments

                if len(line) > fs.max_length:
                    splits = line.split()
                    if len(splits) >= 1 and splits[0][0] == fs.comment: 
                        fs.success = False
                        print_line(dataFile,line,len(line),ii)


            if fs.test == 'trailing comment':
                ## Lines with trailing comments 
                
                line_split = line.split(fs.comment)
                
                if len(line_split) > 1 and \
                        len(line_split[0].strip('')) > fs.max_length:

                    fs.success = False
                    print_line(dataFile,line,len(line_split[0]),ii)


            if fs.test == 'whitespace':
                ## Check for whitespace
                ## Note: currently broken

                if len(" ".join(line.split()))+1 < len(line) > fs.max_length:

                    fs.success = False
                    print_line(dataFile,line,len(line),ii)
                

            ii += 1


###########################


def raise_warning(fs):
    print '\nOBS, TEST "%s" (%s) is not working properly!\n'%(fs.test,fs.long_name)


def analyze_files(fs):

    for root, dirs, files in os.walk(fs.src_dir):
        for file in files:
            if file.endswith(fs.extension):
                dataFile = os.path.join(root,file)
                count_columns(fs,dataFile)


    if fs.silent is False:
        if fs.success is True: 
            newline()
            print 'Test PASSED!'
            print 'No file exceding %s character limit'%(fs.max_length)
            fs.write_settings(kill=False)

        else:
            newline()
            print 'Test FAILED!'
            print 'Found at least one file exceding %s character limit'%(fs.max_length)
            fs.write_settings(kill=False)


    if fs.test in ['whitespace']:
        raise_warning(fs)


            
###########################

if __name__ == "__main__":

    parser = OptionParser()

    parser.add_option("-d","--d", "--dir","--src_dir", 
                      dest="src_dir",default=os.getcwd(),type='str',
                      help="provide directory, set with -d <dir>; " 
                           "defaults to current directory (.)")


    parser.add_option("-t","--t","--test", 
                      dest="test",default='full',type='str',
                      help="specify test, set with: -t <test>; "
                           "default: 'full'; "
                           "valid options: "
                           "'f' ['full'] (check all line types); "
                           "'r' ['rc','regular-code'] (regular code lines); "
                           "'c' ['cc','comment'] (pure comment lines); "
                           "'t' ['tc','trailing-comment'] (code lines with trailing comments); "
                           "'w' ['ws','whitespace']  (white space)")


    parser.add_option("-l","--l","--length","--linelength","--max_length", 
                      dest="max_length",default=132,type="int",
                      help="maximum column count: -l N; "
                           "default N=132")


    parser.add_option("-c","--c","--comment", 
                      dest="comment",default='!',type='str',
                      help="comment, set with: -c <comment>; "
                           "default fortran (!)")


    parser.add_option("-e","--e","--extension","--file_extension", 
                      dest="extension",default='F90',type='str',
                      help="file extension, set with: -e <ext>; "
                           "default ext=F90")


    parser.add_option("--settings","--write_settings","--print_settings",
                      action="store_true", dest="write_settings", default=False,
                      help="print settings")


    parser.add_option("--dir_tree","--directory_tree","--directory_structure",
                      action="store_true", dest="dir_tree", default=False,
                      help="print directory tree of all subdirectories")


    parser.add_option("--file_tree","--file_structure",
                      action="store_true", dest="file_tree", default=False,
                      help="print file tree of all subdirectories")


    parser.add_option("-s","--s", "--silent",
                      action="store_true",dest="silent", default=False,
                      help="don't print status messages to stdout")



    (options, args) = parser.parse_args()


    ### ### ### ### ### ###


    ### Instantiate class fileServer
    fs = fileServer(src_dir=options.src_dir,
                    test=options.test,
                    max_length=options.max_length,
                    comment=options.comment,
                    extension=options.extension,
                    silent=options.silent)



    if options.write_settings is True: 
        fs.write_settings(kill=True)


    if options.dir_tree is True or options.file_tree is True:
        if options.dir_tree is True:
            write_tree(fs,write_files=False)
            newline()

        if options.file_tree is True:
            write_tree(fs,write_files=True)
            newline()

    else:
        analyze_files(fs)



###########################
## === end of script === ##
###########################
