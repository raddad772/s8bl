import re
import os
from typing import List

from s8bl.s8bl import S8BL_LibraryEntry, S8BL_Library, S8BL_System, S8BL_Mapper

MEKA_MAPPER_TO_OURS = {
    0: S8BL_Mapper['sega'],

}


def parse_new_fields(entry: S8BL_LibraryEntry, fields: List[str]):
    for field in fields:
        field = field.strip()
        if field[:8] == 'COUNTRY=':
            if entry.countries is None:
                entry.countries = []
            entry.countries.append(field[8:])
        elif field[:11] == 'EMU_MAPPER=':
            entry.mapper = MEKA_MAPPER_TO_OURS[int(field[11:])]
        else:
            print('INVALID FIELD?', field)


# Parse Meka new format
def parse_new(lib: S8BL_Library, kind: int, line: str):
    #print(line)
    crc = line[4:12].strip()
    if len(crc) < 8:
        print('BAD CRC?', line)
        return
    crc = int(crc, 16)
    mekacrc = line[13:29]
    rol = line[32:]
    fields = rol.split('/')
    entry = S8BL_LibraryEntry()
    entry.CRC32 = crc
    entry.MekaCRC = mekacrc
    entry.system = kind
    entry.names = [fields[0]]
    if len(fields) > 1:
        parse_new_fields(entry, fields[1:])

def parse_old(lib: S8BL_Library, line: str):
    pass

def main():
    lib = S8BL_Library()
    if os.path.isfile('s8bl.json'):
        lib.load('s8bl.json')
    with open('meka.nam', 'r') as infile:
        lines = infile.readlines()
    for line in lines:
        kind = None
        line = line.strip()
        if len(line) < 1:
            continue
        if line[:1] == ';':
            continue
        if line[:2] == '--':
            continue
        if line[:2] == 'GG':
            kind = S8BL_System['gg']
        elif line[:3] == 'SG1':
            kind = S8BL_System['sg1000']
        elif line[:3] == 'SC3':
            kind = S8BL_System['sc3000']
        elif line[:3] == 'OMV':
            kind = S8BL_System['omv']
        elif line[:3] == 'SMS':
            kind = S8BL_System['sms']
        elif line[:3] == 'SF7':
            kind = S8BL_System['sf7000']

        if kind is not None:
            parse_new(lib, kind, line)
            return
        else:
            parse_old(lib, line)

        #print(line)

if __name__ == '__main__':
    main()

#Meka license
'''
 #1 This source code comes free, without any warantee given.
 
 #2 Any modification of this software must have this license preserved,
    and source code made available under the same condition.

 #3 Reuse of program source code and data authorized for any purpose.

Apply to everything else:

  Unlicensed. Gray area. Kernel Panic. Ahah!

Please contact us for any question.
'''