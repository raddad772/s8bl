import json
import os
from shlex import shlex
from typing import List, Dict, Optional

S8BL_System = {
    'unknown': 0,  # No associated system
    'sg1000': 1,  # SG-1000
    'sms': 2,  # Sega Master System
    'gg': 3,  # Sega GameGear
    'sc3000': 4,  # Sega Computer 3000
    'omv': 5,  # Othello Multi-Vision
    'sf7000': 6,  # Sega Super Control Station 7000
    'colecovision': 7
}
S8BL_System_R = {v: k for k, v in S8BL_System.items()}
S8BL_Mapper = {
    'none': 0,
    'sega': 1,
    'sega_32k_RAM': 2,
    'codemasters': 3,
    'dahjee_a': 4,  # AKA 'SG1000_Taiwan_MSX_TypeA': 19, # AKA Dahjee A
    'dahjee_b': 5,  # AKA NoMapper for Meka!?!?!
    'unique_castle': 6,
    'unique_othello': 7,
    'colecovision': 8,
    '93c46': 9,
    'sg1000': 10,
    'sms_actionreplay': 11,
    'tv_oekaki': 12,
    'sf7000': 13,
    'korean_a000': 14,
    'sms_display_unit': 15,
    'korean_msx_8kb_0003': 17,
    'sms_4PakAllAction': 18,
    'sms_korean_FFFF_HiCom': 19,
    'sc3000_survivors_multicart': 20,
    'sms_korean_MSX_8KB_0300': 21,
    'sms_korean_2000_XOR_1F': 22,
    'sms_korean_BFFC': 23,
    'sms_korean_janggun': 24
}
S8BL_Mapper_R = {v: k for k, v in S8BL_Mapper.items()}

S8BL_Country = {
    'US': 0,
    'JP': 1,
    'EU': 2,
    'BR': 3,  # Brazil
    'KR': 4,
    'HK': 5,
    'AU': 6,
    'NZ': 7,
    'FR': 8,
    'PT': 9,
    'DE': 10,
    'IT': 11,
    'SW': 12,
    'CH': 13,
    'UK': 14,
    'CA': 15,
    'TW': 16
}
S8BL_Country_R = {v: k for k, v in S8BL_Country.items()}


class S8BL_LibraryEntry_Flags:
    def __init__(self):
        # None/null refers to unknown
        self.bad = None
        self.prototype = None
        self.gg_sms_mode = None
        self.needs_vdp1 = None
        self.translation = None
        self.bios = None
        self.hacks = None
        self.homebrew = None
        self.is_3d = None
        self.sprite_flicker = None  # ???

    def toPyDict(self):
        return self.toSaveObject()

    def merge(self, mfrom):
        def dif(nm):
            if getattr(mfrom, nm) is not None:
                setattr(self, nm, getattr(mfrom, nm))
        dif('bad')
        dif('prototype')
        dif('gg_sms_mode')
        dif('needs_vdp1')
        dif('translation')
        dif('bios')
        dif('hacks')
        dif('homebrew')
        dif('is_3d')
        dif('sprite_flicker')

    def parse_meka(self, instr: str):
        istr = instr
        if 'BAD' in istr:
            self.bad = True
            istr = istr.replace('BAD', '')
        if 'HOMEBREW' in istr:
            self.homebrew = True
            istr = istr.replace('HOMEBREW', '')
        if 'PROTO' in istr:
            self.prototype = True
            istr = istr.replace('PROTO', '')
        if 'BIOS' in istr:
            self.bios = True
            istr = istr.replace('BIOS', '')
        if 'HACKS' in istr:
            self.hacks = True
            istr = istr.replace('HACKS', '')
        if 'HACK' in istr:
            self.hacks = True
            istr = istr.replace('HACK', '')
        if 'TRANS' in istr:
            self.translation = True
            istr = istr.replace('TRANS', '')
        if 'SMSGG_MODE' in istr:
            self.gg_sms_mode = True
            istr = istr.replace('SMSGG_MODE', '')
        if len(istr.replace(',', '')) > 1:
            print('MISSING FIELDS', istr, instr)

    def toSaveObject(self):
        o = []
        if self.bad is not None: o.append('bad')
        if self.prototype is not None: o.append('prototype')
        if self.gg_sms_mode is not None: o.append('gg_sms_mode')
        if self.needs_vdp1 is not None: o.append('needs_vdp1')
        if self.translation is not None: o.append('translation')
        if self.bios is not None: o.append('bios')
        if self.hacks is not None: o.append('hacks')
        if self.homebrew is not None: o.append('homebrew')
        if self.is_3d is not None: o.append('is_3d')
        if self.sprite_flicker is not None: o.append('sprite_flicker')
        return o


class S8BL_LibraryEntry:
    def __init__(self):
        self.names: List[str] = []  #
        self.CRC32: int = 0  #
        self.MekaCRC: Optional[str] = None  #
        self.mapper: Optional[int] = None  #
        self.system: Optional[int] = None  #
        self.ROM_size: Optional[int] = None  #
        self.RAM_size: Optional[int] = None  #
        self.comments: Optional[List[str]] = None  #

        self.flags: Optional[List[str]] = None  #
        self.product_number: Optional[str] = None  #
        self.version: Optional[str] = None  #
        self.countries: Optional[List[str]] = None  #
        self.identifier: Optional[str] = None  #
        self.translation: Optional[str] = None  #
        self.date: Optional[str] = None  #
        self.misc: Optional[dict] = None
        self.alt_names: Optional[List[str]] = None
        self.requires_ntsc: Optional[bool] = None
        self.requires_pal: Optional[bool] = None
        self.inputs: Optional[List[str]] = None
        self.flags: S8BL_LibraryEntry_Flags = S8BL_LibraryEntry_Flags()

    def toPyDict(self):
        o = {}
        for member in self.members:
            mm = getattr(self, member)
            if member == 'flags':
                o[member] = self.flags.toPyDict()
                continue
            if member == 'mapper':
                if mm is None:
                    mm = 0
                o[member] = S8BL_Mapper_R[mm]
                continue
            if member == 'system':
                if mm is None:
                    mm = 0
                o[member] = S8BL_System_R[mm]
                continue
            if getattr(self, member) is not None:
                o[member] = getattr(self, member)
        return o

    def merge_flags(self, mfrom: S8BL_LibraryEntry_Flags):
        self.flags.merge(mfrom)

    def toSaveObject(self):
        def ainn(obj, what):
            r = getattr(self, what)
            if r is not None:
                obj[what] = r

        o = {'names': self.names,
             'CRC32': self.CRC32,
             'mapper': self.mapper,
             'system': self.system,
             'flags': self.flags.toSaveObject()
             }
        ainn(o, 'product_number')
        ainn(o, 'MekaCRC')
        ainn(o, 'ROM_size')
        ainn(o, 'RAM_size')
        ainn(o, 'comment')
        ainn(o, 'version')
        ainn(o, 'countries')
        ainn(o, 'intentifier')
        ainn(o, 'translation')
        ainn(o, 'misc')
        ainn(o, 'date')
        ainn(o, 'alt_names')
        ainn(o, 'requires_ntsc')
        ainn(o, 'requires_pal')
        ainn(o, 'inputs')

    @property
    def members(self) -> List[str]:
        return [attr for attr in dir(self) if
                attr != 'members' and not callable(getattr(self, attr)) and not attr.startswith("__")]

    def replace(self, mwith: 'S8BL_LibraryEntry') -> None:
        # Overwrite all our attributes
        self.__init__()
        for m in self.members:
            setattr(self, m, getattr(mwith, m))

    def fromPyObjectTotal(self, what):
        self.names = what['names']
        self.CRC32 = what['CRC32']
        self.ROM_size = what['ROM_size']
        self.RAM_size = what['RAM_size']
        self.mapper = S8BL_Mapper[what['mapper']]
        self.system = S8BL_System[what['system']]


class S8BL_Library:
    def __init__(self):
        self.valid: bool = False
        self.db: List[S8BL_LibraryEntry] = []
        self.CRC_to_db: Dict[int, S8BL_LibraryEntry] = {}

    def addFromTotal(self, names=None, CRC32: int = 0, ROM_size: Optional[int] = None, RAM_size: Optional[int] = None,
                     mapper: Optional[int] = None, system: Optional[int] = None):
        if names is None:
            names = []
        if CRC32 in self.CRC_to_db:
            obj = self.CRC_to_db[CRC32]
        else:
            obj = S8BL_LibraryEntry()
        obj.names = names
        obj.CRC32 = CRC32
        obj.ROM_size = ROM_size
        obj.RAM_size = RAM_size
        obj.mapper = mapper
        obj.system = system
        self.db.append(obj)

    def merge_in(self, to: S8BL_LibraryEntry) -> None:
        found = None
        # Deal with MekaCRC-only ones
        if to.CRC32 == 0:
            # print('WEIRD ENTRY', to.names)
            for entry in self.db:
                if (entry.MekaCRC is not None and entry.MekaCRC == to.MekaCRC) or (entry.names[0] == to.names[0]):
                    entry.replace(to)
                    return
            self.db.append(to)
            return

        # Scan for CRC and update
        if to.CRC32 in self.CRC_to_db:
            entry = self.CRC_to_db[to.CRC32]
            if entry.mapper != to.mapper:
                if to.mapper == 2 and entry.mapper == 1:
                    entry.mapper = 2
                elif to.mapper == 0:
                    entry.mapper = to.mapper
                elif entry.mapper == 0:
                    entry.mapper = to.mapper
                elif entry.mapper == 1:
                    entry.mapper = to.mapper
                elif entry.mapper in [6, 7]:
                    pass
            for nm in to.names:
                if nm not in entry.names:
                    entry.names.append(nm)
            members = entry.members
            for member in members:
                if member == 'names' or member == 'mapper':
                    continue
                entry_m = getattr(entry, member)
                to_m = getattr(to, member)
                if member == 'flags':
                    entry.merge_flags(to.flags)
                    continue
                if to_m is None and entry_m is None:
                    continue
                if entry_m is None and to_m is not None:
                    setattr(entry, member, to_m)
                    continue
                if entry_m == to_m:
                    continue
                if member == 'system' and entry_m == 2 and to_m == 4:
                    setattr(entry, member, to_m)
                    continue
                if member == 'system' and entry_m == 1 and to_m != 1:
                    continue
                if entry_m == 2 and to_m == 1:
                    setattr(entry, member, to_m)
                    continue
                if member == "ROM_size" or member == 'RAM_size':
                    continue
                if member == 'system' and entry_m == 3 and to_m == 2:
                    continue
                print('GOT HERE...', member, entry_m, to_m, entry.names)
            return
        # Replace!
        self.CRC_to_db[to.CRC32] = to
        self.db.append(to)

    def load(self, path: str) -> None:
        if not os.path.isfile(path):
            raise FileNotFoundError
        with open(path, 'r') as infile:
            indata = json.load(infile)
        self.fromPyDictTotal(indata)

    def fromPyDictTotal(self, indata: List) -> None:
        self.db = []
        for entry in indata:
            dbitem = S8BL_LibraryEntry()
            dbitem.fromPyObjectTotal(entry)
            self.CRC_to_db[dbitem.CRC32] = dbitem
            self.db.append(dbitem)
        self.valid = True

    def toPyDict(self):
        out = []
        for item in self.db:
            out.append(item.toPyDict())
        return out

    def save(self, path: str) -> None:
        tpath = path + '.tmp'
        if os.path.isfile(tpath):
            os.unlink(tpath)
        mydata = self.toPyDict()
        with open(tpath, 'w') as outfile:
            json.dump(mydata, outfile, indent=2)
        if os.path.isfile(path):
            os.unlink(path)
        os.rename(tpath, path)
