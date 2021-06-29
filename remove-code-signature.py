#!/usr/bin/env python

# Copyright (c) Hin-Tak Leung

# script to remove a signature from a code-signed MAC OS X binary

# Roughly follows the advice in
# https://stackoverflow.com/questions/44872071/removing-the-code-signature-from-a-mac-app-executable/44873442
# but in slightly different order.

# See also accompanying "mono-codesign-fix.py" script

from macholib.MachO import MachO
from os import stat
from sys import argv

input_binary = argv[1]

file_size = stat(input_binary).st_size

exe_data = MachO(input_binary)

signed_binary = False

# The end of signature is expected to be at the end of file.
end_of_signature = 0
beginning_of_signature = file_size
end_of_SYMTAB = 0

multi_arch = False

# Development option to quickly disable modifying
# by putting this to True:
dev_not_modifying = False

if (len(exe_data.headers) > 1):
    raise ValueError("Fat Binary: %d archs" % len(exe_data.headers))

# Fat binary could contain multiple architectures.
for h in exe_data.headers:
    # Access Mach-O load commands
    for c in h.commands:
        # 'c' is a tuple (command_metadata, segment, [section1, section2])
        if (c[0].get_cmd_name() == 'LC_SYMTAB'):
            print("entry(LC_SYMTAB):\n\t", c[0].get_cmd_name(), c[1], c[2])
            print(file_size, c[1].stroff + c[1].strsize)
            end_of_SYMTAB = c[1].stroff + c[1].strsize
        if (c[0].get_cmd_name() == 'LC_CODE_SIGNATURE'):
            print("entry(LC_CODE_SIGNATURE):\n\t", c[0].get_cmd_name(), c[1], c[2])
            end_of_signature = c[1].dataoff + c[1].datasize
            beginning_of_signature = c[1].dataoff
            signed_binary = True

if (beginning_of_signature != file_size):
    print("Beginning of signature:", beginning_of_signature)
    #print(end_of_SYMTAB, beginning_of_signature, beginning_of_signature - end_of_SYMTAB)

if (exe_data.headers[-1].commands[-1][0].get_cmd_name() != 'LC_CODE_SIGNATURE'):
    raise SystemExit("last command not LC_CODE_SIGNATURE")
else:
    del exe_data.headers[-1].commands[-1]

exe_data.headers[-1].header.ncmds = exe_data.headers[-1].header.ncmds - 1

exe_data.headers[-1].header.sizeofcmds = exe_data.headers[-1].header.sizeofcmds - 0x10
    
# Truncate file to the end of SYMTAB table:
linkedit = [c for c in exe_data.headers[-1].commands if \
    hasattr(c[1], 'segname') and \
    str(c[1].segname).startswith("b'__LINKEDIT")][0]

linkedit[1].filesize = end_of_SYMTAB - linkedit[1].fileoff
linkedit[1].vmsize = linkedit[1].filesize
    
#
if (end_of_signature == file_size):
    signed_binary = True

if (not signed_binary or dev_not_modifying):
    print("The binary was not signed. Not modifying.")
else:
    # Change some header parameters.
    # Write changes back.
    file_object = open(exe_data.filename, 'rb+')
    # this only re-write the header, hence we used 'rb+' to re-write in-place:
    exe_data.write(file_object)
    file_object.truncate(end_of_SYMTAB)
    file_object.close()
