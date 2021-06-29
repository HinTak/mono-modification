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

# The end of signature is expected to be at the end of file,
# while beginning of bundle is after the main mono binary
# and definitely not the end.
end_of_signature = 0
beginning_of_bundle = file_size

multi_arch = False

# Development option to quickly disable modifying
# by putting this to True:
dev_not_modifying = False

if (len(exe_data.headers) > 1):
    print("Fat Binary:", len(exe_data.headers))
    multi_arch = True

# Fat binary could contain multiple architectures.
for h in exe_data.headers:
    # Access Mach-O load commands
    for c in h.commands:
        # 'c' is a tuple (command_metadata, segment, [section1, section2])
        #c[0].get_cmd_name()
        if (c[0].get_cmd_name() == 'LC_SYMTAB'):
            print("entry(LC_SYMTAB):\n\t", c[0].get_cmd_name(), c[1], c[2])
            print(file_size, c[1].stroff + c[1].strsize)
            if ((file_size != c[1].stroff + c[1].strsize) and (not multi_arch)):
                c[1].strsize = file_size - c[1].stroff
        if (c[0].get_cmd_name() == 'LC_CODE_SIGNATURE'):
            print("entry(LC_CODE_SIGNATURE):\n\t", c[0].get_cmd_name(), c[1], c[2])
            end_of_signature = c[1].dataoff + c[1].datasize
    # The 4th (last) 'LC_SEGMENT_64' is the __LINKEDIT segment.
    linkedit = [c for c in h.commands if \
        hasattr(c[1], 'segname') and \
        str(c[1].segname).startswith("b'__LINKEDIT")][0]
    print("4th(LC_SEGMENT_64/__LINKEDIT):\n\t", linkedit[0].get_cmd_name(), linkedit[1], linkedit[2])
    # check that it is an executable, instead of e.g. dylib
    if (linkedit[0].get_cmd_name() == 'LC_SEGMENT_64'):
        print(file_size, linkedit[1].fileoff + linkedit[1].filesize, ((linkedit[1].vmsize - linkedit[1].filesize) == 0))
        if (file_size != linkedit[1].fileoff + linkedit[1].filesize and (not multi_arch)):
            beginning_of_bundle = linkedit[1].fileoff + linkedit[1].filesize
            print("Beginning of bundle", beginning_of_bundle)
            linkedit[1].filesize = file_size - linkedit[1].fileoff
            linkedit[1].vmsize = linkedit[1].filesize

if (end_of_signature != 0):
    if (end_of_signature != file_size):
        print("End of Signature not at end of file:", end_of_signature)
    if (beginning_of_bundle != file_size):
        if (beginning_of_bundle == end_of_signature):
            print("mkbundle with Native Mac OS X/Signed default runtime detected. Aborting.")
            dev_not_modifying = True

if (end_of_signature == file_size):
    signed_binary = True

if (signed_binary or multi_arch or dev_not_modifying):
    print("The binary was signed or multi_arch. Not modifying.")
else:
    # Change some header parameters.
    # Write changes back.
    file_object = open(exe_data.filename, 'rb+')
    # this only re-write the header, hence we used 'rb+' to re-write in-place:
    exe_data.write(file_object)
    file_object.close()
