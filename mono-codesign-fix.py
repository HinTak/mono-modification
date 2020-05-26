#!/usr/bin/env python

# Copyright (c) Hin-Tak Leung

# script to adjust mono mkbundle-generated binaries for Mac OS X code signing,
# based on ideas from
# https://github.com/pyinstaller/pyinstaller/wiki/Recipe-OSX-Code-Signing

# discussed in https://github.com/mono/mono/issues/17881

from macholib.MachO import MachO
from os import stat
from sys import argv

if not argv[1:]:
    input_binary = 'MacUI/FontValidator/FontValidator/FontValidator'
else:
    input_binary = argv[1]

file_size = stat(input_binary).st_size

exe_data = MachO(input_binary)

signed_binary = False

multi_arch = False

if (len(exe_data.headers) > 1):
    print("Fat Binary:", len(exe_data.headers))
    multi_arch = True

# Fat binary could contain multiple architectures.
for h in exe_data.headers:
    # Access Mach-O load commands
    for c in h.commands:
        # 'c' is a tupple (command_metadata, segment, [section1, section2])
        #c[0].get_cmd_name()
        if (c[0].get_cmd_name() == 'LC_SYMTAB'):
            print("entry(LC_SYMTAB):\n\t", c[0].get_cmd_name(), c[1], c[2])
            print(file_size, c[1].stroff + c[1].strsize)
            if ((file_size != c[1].stroff + c[1].strsize) and (not multi_arch)):
                c[1].strsize = file_size - c[1].stroff
        if (c[0].get_cmd_name() == 'LC_CODE_SIGNATURE'):
            print("entry(LC_CODE_SIGNATURE):\n\t", c[0].get_cmd_name(), c[1], c[2])
            signed_binary = True
    # The 4th (last) 'LC_SEGMENT_64' is the __LINKEDIT segment.
    linkedit = h.commands[3]
    print("4th(LC_SEGMENT_64/__LINKEDIT):\n\t", linkedit[0].get_cmd_name(), linkedit[1], linkedit[2])
    print(file_size, linkedit[1].fileoff + linkedit[1].filesize, ((linkedit[1].vmsize - linkedit[1].filesize) == 0))
    if (file_size != linkedit[1].fileoff + linkedit[1].filesize and (not multi_arch)):
        linkedit[1].filesize = file_size - linkedit[1].fileoff
        linkedit[1].vmsize = linkedit[1].filesize

if (signed_binary or multi_arch):
    print("The binary was signed or multi_arch. Not modifying.")
else:
    # Change some header parameters.
    # Write changes back.
    file_object = open(exe_data.filename, 'rb+')
    # this only re-write the header, hence we used 'rb+' to re-write in-place:
    exe_data.write(file_object)
    file_object.close()
