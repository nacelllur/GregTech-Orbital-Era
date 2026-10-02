# -*- coding: utf-8 -*-
import gzip, struct
import numpy as np

DST = r'D:/GT-New/schematics/EARTH-STAR (完稿)-v6.litematic'
data = gzip.open(DST, 'rb').read()
pos = 0
def u1():
    global pos; v = data[pos]; pos += 1; return v
def u2():
    global pos; v = struct.unpack('>H', data[pos:pos+2])[0]; pos += 2; return v
def i4():
    global pos; v = struct.unpack('>i', data[pos:pos+4])[0]; pos += 4; return v
def name_str():
    global pos; n = u2(); s = data[pos:pos+n].decode('utf-8'); pos += n; return s

longarrays = []
cur_name = ['']
def read_payload(t):
    global pos
    if t == 0: return None
    if t == 1: v = data[pos]; pos += 1; return v
    if t == 2: v = struct.unpack('>h', data[pos:pos+2])[0]; pos += 2; return v
    if t == 3: return i4()
    if t == 4: v = struct.unpack('>q', data[pos:pos+8])[0]; pos += 8; return v
    if t == 5: v = struct.unpack('>f', data[pos:pos+4])[0]; pos += 4; return v
    if t == 6: v = struct.unpack('>d', data[pos:pos+8])[0]; pos += 8; return v
    if t == 7:
        n = i4(); longarrays.append((cur_name[0], pos, n)); pos += n; return b'<bytes>'
    if t == 8: return name_str()
    if t == 9:
        et = u1(); n = i4()
        return [read_payload(et) for _ in range(n)]
    if t == 10:
        d = {}
        while True:
            et = u1()
            if et == 0: return d
            nm = name_str(); prev = cur_name[0]; cur_name[0] = nm
            d[nm] = read_payload(et); cur_name[0] = prev
    if t == 11:
        n = i4(); pos += 4*n; return None
    if t == 12:
        n = i4(); longarrays.append((cur_name[0], pos, n*8)); pos += 8*n; return b'<longs>'
    raise ValueError(t)

t = u1(); name_str()
root = read_payload(t)
assert pos == len(data)
region = root['Regions']['Unnamed']
sz = region['Size']
vol = abs(sz['x']) * abs(sz['y']) * abs(sz['z'])
palette = region['BlockStatePalette']
npal = len(palette)
bits = max(4, (npal - 1).bit_length())
blob = None
for nm, off, ln in longarrays:
    if nm == 'BlockStates':
        blob = data[off:off+ln]
print('volume(abs) =', vol, '| palette', npal, '| bits', bits, '| longs', len(blob)//8)

bitstream = np.unpackbits(np.frombuffer(blob, dtype=np.uint8))
n = vol
codes = bitstream[:n*bits].reshape(-1, bits).astype(np.uint32) @ (1 << np.arange(bits-1, -1, -1, dtype=np.uint32))
counts = np.bincount(codes, minlength=npal)
print('air:', int(counts[0]))
print('non-air:', n - int(counts[0]), '| metadata TotalBlocks:', root['Metadata']['TotalBlocks'])
names = [e['Name'] for e in palette]
from collections import Counter
agg = Counter()
for e, c in zip(palette, counts):
    agg[e['Name']] += int(c)
print('water =', agg.get('minecraft:water'), ' lava =', agg.get('minecraft:lava'),
      ' lava_cauldron =', agg.get('minecraft:lava_cauldron'))
inv = counts[npal:] if len(counts) > npal else None
print('codes >= palette size:', int(inv.sum()) if inv is not None else 0)
top = agg.most_common(15)
for nm, c in top:
    print('  %-45s %10d' % (nm, c))
