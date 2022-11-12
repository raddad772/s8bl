import re
import os
from typing import List

from s8bl.s8bl import S8BL_LibraryEntry, S8BL_Library, S8BL_System, S8BL_Mapper

MEKA_MAPPER_TO_OURS = {
    0: S8BL_Mapper['sega'],
    1: S8BL_Mapper['sega_32k_RAM'],
    2: S8BL_Mapper['colecovision'],
    3: S8BL_Mapper['codemasters'],
    4: S8BL_Mapper['93c46'],
    5: S8BL_Mapper['sg1000'],
    6: S8BL_Mapper['sms_actionreplay'],
    7: S8BL_Mapper['tv_oekaki'],
    8: S8BL_Mapper['sf7000'],
    9: S8BL_Mapper['korean_a000'],
    10: S8BL_Mapper['sms_display_unit'],
    11: S8BL_Mapper['dahjee_b'],
    12: S8BL_Mapper['korean_msx_8kb_0003'],
    13: S8BL_Mapper['sms_korean_janggun'],
    14: S8BL_Mapper['sms_4PakAllAction'],
    15: S8BL_Mapper['dahjee_a'],
    16: S8BL_Mapper['sms_korean_FFFF_HiCom'],
    17: S8BL_Mapper['sc3000_survivors_multicart'],
    18: S8BL_Mapper['sms_korean_MSX_8KB_0300'],
    19: S8BL_Mapper['sms_korean_2000_XOR_1F'],
    20: S8BL_Mapper['sms_korean_BFFC']
}

def parse_old_fields(entry: S8BL_LibraryEntry, fields: List[str]):
    for field in fields:
        if field == 'BAD':
            entry.flags.bad = True
        elif field == 'HACK':
            entry.flags.hacks = True
        elif field[:8] == 'AUTHORS=':
            if entry.misc is None:
                entry.misc = {}
            entry.misc['authors'] = field[8:]
        elif field[:8] == 'COMMENT=':
            entry.comments = [field[8:]]
        elif field[:6] == 'TRANS=':
            entry.translation = field[6:]
        elif field[:4] == 'VER=':
            entry.version = field[4:]
        elif field == 'PROTO':
            entry.flags.prototype = True
        elif field == 'TVTYPE=PAL/SECAM':
            entry.requires_pal = True
        elif 'ID=' in field:
            entry.identifier = field[3:]
        elif 'DATE=' in field:
            entry.date = field[:5]
        elif 'JAPNAME=' in field:
            if entry.alt_names is None:
                entry.alt_names = []
            entry.alt_names.append(field[8:])
        elif 'Mapper=' in field or 'MAPPER=' in field:
            entry.mapper = MEKA_MAPPER_TO_OURS[int(field[7:])]
        elif field == 'FLICKER':
            entry.flags.sprite_flicker = True
        else:
            print('UNKNOWN FIELD?', field)

def parse_new_fields(entry: S8BL_LibraryEntry, fields: List[str]):
    for field in fields:
        field = field.strip()
        if ';' in field:
            pp = field.index(';')
            field = field[:pp].strip()
        if field[:8] == 'COUNTRY=':
            if entry.countries is None:
                entry.countries = []
            entry.countries.append(field[8:])
        elif field[:11] == 'EMU_MAPPER=':
            entry.mapper = MEKA_MAPPER_TO_OURS[int(field[11:])]
        elif field[:11] == 'PRODUCT_NO=':
            entry.product_number = field[11:]
        elif field[:8] == 'COMMENT=':
            entry.comments = [field[8:]]
        elif field[:8] == 'VERSION=':
            entry.version = field[8:]
        elif field[:6] == 'FLAGS=':
            entry.flags.parse_meka(field[6:])
        elif field[:18] == 'EMU_SPRITE_FLICKER':
            entry.flags.sprite_flicker = True
        elif field[:6] == 'TRANS=':
            entry.translation = field[6:]
        elif field[:8] == 'AUTHORS=':
            if entry.misc is None:
                entry.misc = {}
            entry.misc['authors'] = field[8:]
        elif field[:5] == 'NAME_':
            if entry.alt_names is None:
                entry.alt_names = []
            entry.alt_names.append(field[5:])
        elif field == 'EMU_3D':
            entry.flags.is_3d = True
        elif field == 'EMU_TVTYPE=PAL':
            entry.requires_pal = True
        elif field == 'EMU_TVTYPE=NTSC':
            entry.requires_ntsc = True
        elif field == 'EMU_VDP=315-5124':
            entry.flags.needs_vdp1 = True
        elif 'EMU_COUNTRY=' in field:
            pass
        elif field[:12] == 'EMU_IPERIOD=':
            pass
        elif field[:11] == 'EMU_INPUTS=':
            if entry.inputs is None:
                entry.inputs = []
            entry.inputs.append(field[11:22].lower())
        elif field[:12] == 'EMU_LP_FUNC=':
            if entry.misc is None:
                entry.misc = {}
            a = int(field[12:])
            if a == 1:
                entry.misc['lp_func'] = 'missile_defense_3d'
            elif a == 2:
                entry.misc['lp_func'] = '3dgunner'
            else:
                entry.misc['lp_func'] = field[12:]
        else:
            if 'B based on the fact that' in field:
                continue
            print('INVALID FIELD?', field, fields)
            pass


# Parse Meka new format
def parse_new(lib: S8BL_Library, kind: int, line: str):
    # print(line)
    crc = line[4:12].strip()
    if len(crc) < 8:
        print('BAD CRC?', line)
        return
    crc = int(crc, 16)
    mekacrc = line[13:29]
    rol = line[32:]
    rol = rol.replace('\\/', '|')
    fields = rol.split('/')
    fields[0].replace('|', '/')
    entry = S8BL_LibraryEntry()
    entry.CRC32 = crc
    entry.MekaCRC = mekacrc
    entry.system = kind
    entry.names = [fields[0]]
    if len(fields) > 1:
        parse_new_fields(entry, fields[1:])


def parse_old(lib: S8BL_Library, line: str):
    entry = S8BL_LibraryEntry()
    entry.MekaCRC = line[:16]
    rol = line[18:]
    rol = rol.replace('\\,', '|')
    fields = rol.split(',')
    for i in range(0, len(fields)):
        fields[i] = fields[i].replace('|', ',')
    entry.names = [fields[0]]
    if len(fields) > 1:
        parse_old_fields(entry, fields[1:])
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
        else:
            parse_old(lib, line)

        # print(line)


if __name__ == '__main__':
    main()

# Meka license
'''
 #1 This source code comes free, without any warantee given.
 
 #2 Any modification of this software must have this license preserved,
    and source code made available under the same condition.

 #3 Reuse of program source code and data authorized for any purpose.

Apply to everything else:

  Unlicensed. Gray area. Kernel Panic. Ahah!

Please contact us for any question.
'''
