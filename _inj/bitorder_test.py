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

longs = np.frombuffer(blob, dtype='>u8')
assert len(longs) * 64 // bits >= vol
print('longs', len(longs), 'bits', bits, 'vol', vol, 'TotalBlocks(meta)', root['Metadata']['TotalBlocks'])
shifts = np.arange(64, dtype=np.uint64)

def decode(mode):
    counts = np.zeros(npal + (1 << bits), dtype=np.int64)
    CH = 5_000_000  # multiple of 5 longs -> 32 entries per 5 longs, clean 10-bit boundary
    for s in range(0, len(longs), CH):
        chunk = longs[s:s+CH]
        if mode == 'lsb':
            b = ((chunk[:, None] >> shifts[None, :]) & np.uint64(1)).astype(np.uint8).reshape(-1)
        else:  # msb
            b = ((chunk[:, None] >> (np.uint64(63) - shifts[None, :])) & np.uint64(1)).astype(np.uint8).reshape(-1)
        m = (len(b) // bits) * bits
        codes = b[:m].reshape(-1, bits).astype(np.uint32)
        if mode == 'lsb':
            w = (1 << np.arange(bits, dtype=np.uint32))
        else:
            w = (1 << np.arange(bits - 1, -1, -1, dtype=np.uint32))
        vals = codes @ w
        c = np.bincount(vals, minlength=1 << bits)
        counts[:len(c)] += c
    return counts

for mode in ('lsb', 'msb'):
    counts = decode(mode)
    air = int(counts[0])
    invalid = int(counts[npal:].sum())
    nonair = vol - air
    print('%s: air=%d nonair=%d invalid=%d  (meta=%d) %s' % (
        mode, air, nonair, invalid, root['Metadata']['TotalBlocks'],
        '<<< MATCH' if nonair == root['Metadata']['TotalBlocks'] and invalid == 0 else ''))
