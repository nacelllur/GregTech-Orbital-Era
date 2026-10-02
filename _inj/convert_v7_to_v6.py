# -*- coding: utf-8 -*-
"""Convert litematic v7 -> v6 (single Version-int patch) + integrity analysis."""
import gzip, struct, sys
import numpy as np

SRC = r'D:/GT-New/schematics/EARTH-STAR (完稿).litematic'
DST = r'D:/GT-New/schematics/EARTH-STAR (完稿)-v6.litematic'

data = gzip.open(SRC, 'rb').read()
print('decompressed size:', len(data))
pos = 0

def u1():
    global pos
    v = data[pos]; pos += 1; return v
def u2():
    global pos
    v = struct.unpack('>H', data[pos:pos+2])[0]; pos += 2; return v
def i4():
    global pos
    v = struct.unpack('>i', data[pos:pos+4])[0]; pos += 4; return v
def name_str():
    global pos
    n = u2()
    s = data[pos:pos+n].decode('utf-8'); pos += n
    return s

def read_payload(t):
    """Parse; for the root-level 'Version' int record its value offset."""
    global pos, cur_depth, cur_name, version_offset, longarrays
    if t == 0: return None
    if t == 1: v = data[pos]; pos += 1; return v
    if t == 2: v = struct.unpack('>h', data[pos:pos+2])[0]; pos += 2; return v
    if t == 3:
        off = pos; v = i4()
        if cur_name[0] == 'Version':
            version_offset[0] = off
        return v
    if t == 4: v = struct.unpack('>q', data[pos:pos+8])[0]; pos += 8; return v
    if t == 5: v = struct.unpack('>f', data[pos:pos+4])[0]; pos += 4; return v
    if t == 6: v = struct.unpack('>d', data[pos:pos+8])[0]; pos += 8; return v
    if t == 7:
        n = i4(); b = data[pos:pos+n]; pos += n
        longarrays.append((cur_name[0], pos - n, n))
        return b
    if t == 8: return name_str()
    if t == 9:
        et = u1(); n = i4()
        return [read_payload(et) for _ in range(n)]
    if t == 10:
        d = {}
        cur_depth[0] += 1
        while True:
            et = u1()
            if et == 0:
                cur_depth[0] -= 1
                return d
            nm = name_str()
            prev = cur_name[0]
            cur_name[0] = nm
            d[nm] = read_payload(et)
            cur_name[0] = prev
        cur_depth[0] -= 1
    if t == 11:
        n = i4(); pos += 4 * n; return None
    if t == 12:
        n = i4()
        longarrays.append((cur_name[0], pos, n * 8))
        pos += 8 * n
        return b'<%d longs>' % n
    raise ValueError(t)

version_offset = [-1]
longarrays = []
cur_name = ['']
cur_depth = [0]

t = u1(); rootname = name_str()
root = read_payload(t)
assert pos == len(data), 'parse incomplete: %d != %d' % (pos, len(data))
print('parsed OK; Version value at byte offset', version_offset[0])

ver = struct.unpack('>i', data[version_offset[0]:version_offset[0]+4])[0]
assert ver == 7, 'unexpected Version %d' % ver

# ---- patch: Version 7 -> 6 (in-place, same width) ----
patched = bytearray(data)
patched[version_offset[0]:version_offset[0]+4] = struct.pack('>i', 6)
with gzip.open(DST, 'wb', compresslevel=6) as f:
    f.write(bytes(patched))
print('written:', DST)

import os
print('src size', os.path.getsize(SRC), 'dst size', os.path.getsize(DST))

# ---- verify output parses & is v6 ----
import importlib.util
pos = 0; cur_name = ['']; cur_depth = [0]; longarrays = []
with gzip.open(DST, 'rb') as f:
    data2 = f.read()
data = data2
t2 = u1(); name_str()
root2 = read_payload(t2)
assert pos == len(data2)
print('re-parse OK: Version =', root2['Version'], 'SubVersion =', root2['SubVersion'],
      'MinecraftDataVersion =', root2['MinecraftDataVersion'])

# ---- block data integrity + unsupported block usage ----
region = root2['Regions']['Unnamed']
palette = region['BlockStatePalette']
longs_blob = None
for nm, off, ln in longarrays:
    if nm == 'BlockStates':
        longs_blob = data2[off:off+ln]
print('BlockStates bytes:', len(longs_blob), '=', len(longs_blob)//8, 'longs')

npal = len(palette)
bits = max(4, (npal - 1).bit_length())
total = region['Size']['x'] * region['Size']['y'] * region['Size']['z']
print('palette', npal, '-> bits', bits, '| total volume', total)

arr = np.frombuffer(longs_blob, dtype=np.uint8)
bitstream = np.unpackbits(arr)  # big-endian bit order per byte
n_entries = len(bitstream) // bits
print('bit stream:', len(bitstream), 'bits ->', n_entries, 'entries')
usable = n_entries * bits
idx = bitstream[:usable].reshape(-1, bits).astype(np.uint32)
weights = (1 << np.arange(bits - 1, -1, -1, dtype=np.uint32))
codes = idx @ weights
counts = np.bincount(codes, minlength=npal)

names = [e['Name'] for e in palette]
nonair = int(total - counts[0])
print('decoded non-air blocks:', nonair, '| metadata TotalBlocks:', root2['Metadata']['TotalBlocks'],
      '| MATCH' if nonair == root2['Metadata']['TotalBlocks'] else '| MISMATCH!')

print()
print('=== usage of blocks missing from 1.20.1 ===')
missing = {'minecraft:chiseled_tuff', 'minecraft:crafter', 'minecraft:polished_tuff',
           'minecraft:pale_oak_button', 'minecraft:pale_oak_trapdoor',
           'minecraft:pale_oak_wall_sign', 'minecraft:stripped_pale_oak_wood'}
total_missing = 0
for e, c in zip(palette, counts):
    if e['Name'] in missing:
        props = e.get('Properties', {})
        total_missing += int(c)
        print('  %-45s %10d  %s' % (e['Name'] + ' ' + str(props), int(c), ''))
print('TOTAL affected blocks:', total_missing, 'of', total, '(%.4f%%)' % (100.0*total_missing/total))

print()
print('top 10 used blocks:')
order = np.argsort(-counts)[:10]
for i in order:
    print('  %-45s %10d' % (names[int(i)], int(counts[int(i)])))
