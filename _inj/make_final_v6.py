# -*- coding: utf-8 -*-
"""Final converter: parse NBT tree -> set Version=6 + remap 1.21-only palette
entries to 1.20.1 equivalents -> serialize -> gzip. Verifies byte-exact
round-trip on the unmodified tree first."""
import gzip, struct, os
import numpy as np

SRC = r'D:/GT-New/schematics/EARTH-STAR (完稿).litematic'
DST = r'D:/GT-New/schematics/EARTH-STAR (完稿)_1.20.1.litematic'

REMAP = {
    'minecraft:chiseled_tuff':   ('minecraft:chiseled_deepslate', {}),
    'minecraft:polished_tuff':   ('minecraft:tuff', {}),
    'minecraft:crafter':         ('minecraft:dispenser', {'orientation': 'facing'}),
    'minecraft:pale_oak_trapdoor':   ('minecraft:birch_trapdoor', {}),
    'minecraft:pale_oak_button':     ('minecraft:birch_button', {}),
    'minecraft:pale_oak_wall_sign':  ('minecraft:birch_wall_sign', {}),
    'minecraft:stripped_pale_oak_wood': ('minecraft:stripped_birch_wood', {}),
}
KEEP_PROPS = {
    'minecraft:dispenser':       {'facing', 'triggered'},
    'minecraft:birch_trapdoor':  {'facing', 'half', 'open', 'powered', 'waterlogged'},
    'minecraft:birch_button':    {'facing', 'face', 'powered'},
    'minecraft:birch_wall_sign': {'facing', 'waterlogged'},
    'minecraft:stripped_birch_wood': {'axis'},
    'minecraft:chiseled_deepslate': set(),
    'minecraft:tuff': set(),
}

# ---------- parse into (type, value) tree ----------
data = gzip.open(SRC, 'rb').read()
pos = 0
def rp(t):
    global pos
    if t == 0: return None
    if t == 1: v = data[pos]; pos += 1; return v
    if t == 2: v = struct.unpack('>h', data[pos:pos+2])[0]; pos += 2; return v
    if t == 3: v = struct.unpack('>i', data[pos:pos+4])[0]; pos += 4; return v
    if t == 4: v = struct.unpack('>q', data[pos:pos+8])[0]; pos += 8; return v
    if t == 5: v = struct.unpack('>f', data[pos:pos+4])[0]; pos += 4; return v
    if t == 6: v = struct.unpack('>d', data[pos:pos+8])[0]; pos += 8; return v
    if t == 7:
        n = struct.unpack('>i', data[pos:pos+4])[0]; pos += 4
        v = bytes(data[pos:pos+n]); pos += n; return v
    if t == 8:
        n = struct.unpack('>H', data[pos:pos+2])[0]
        v = data[pos+2:pos+2+n].decode('utf-8'); pos += 2 + n; return v
    if t == 9:
        et = data[pos]; pos += 1
        n = struct.unpack('>i', data[pos:pos+4])[0]; pos += 4
        return (et, [rp(et) for _ in range(n)])
    if t == 10:
        d = {}
        while True:
            et = data[pos]; pos += 1
            if et == 0: return d
            n = struct.unpack('>H', data[pos:pos+2])[0]
            nm = data[pos+2:pos+2+n].decode('utf-8'); pos += 2 + n
            d[nm] = (et, rp(et))
    if t == 11:
        n = struct.unpack('>i', data[pos:pos+4])[0]; pos += 4
        v = np.frombuffer(data, dtype='>i4', count=n, offset=pos).tolist(); pos += 4*n; return v
    if t == 12:
        n = struct.unpack('>i', data[pos:pos+4])[0]; pos += 4
        v = bytes(data[pos:pos+8*n]); pos += 8*n; return ('rawlongs', v, n)
    raise ValueError(t)

tt = data[0]; pos = 1
nn = struct.unpack('>H', data[pos:pos+2])[0]
rootname = data[pos+2:pos+2+nn].decode('utf-8'); pos += 2 + nn
assert tt == 10
root = rp(tt)
assert pos == len(data), 'parse incomplete'
print('parse OK; long-array blobs kept raw')

# ---------- serialize ----------
out = bytearray()
def ser(t, v):
    global out
    if t == 1: out += struct.pack('>b', v)
    elif t == 2: out += struct.pack('>h', v)
    elif t == 3: out += struct.pack('>i', v)
    elif t == 4: out += struct.pack('>q', v)
    elif t == 5: out += struct.pack('>f', v)
    elif t == 6: out += struct.pack('>d', v)
    elif t == 7: out += struct.pack('>i', len(v)) + v
    elif t == 8:
        b = v.encode('utf-8'); out += struct.pack('>H', len(b)) + b
    elif t == 9:
        et, items = v
        out.append(et)
        out += struct.pack('>i', len(items))
        for e in items: ser(et, e)
    elif t == 10:
        for nm, (et2, val) in v.items():
            out.append(et2)
            b = nm.encode('utf-8'); out += struct.pack('>H', len(b)) + b
            ser(et2, val)
        out.append(0)
    elif t == 11:
        out += struct.pack('>i', len(v))
        out += np.array(v, dtype='>i4').tobytes()
    elif t == 12:
        _, blob, n = v
        out += struct.pack('>i', n) + blob
    else:
        raise ValueError(t)

def ser_root(tree):
    global out
    out = bytearray()
    out.append(10)
    b = b''; out += struct.pack('>H', 0)
    for nm, (et2, val) in tree.items():
        out.append(et2)
        b = nm.encode('utf-8'); out += struct.pack('>H', len(b)) + b
        ser(et2, val)
    out.append(0)
    return bytes(out)

# verify round-trip first
rt = ser_root(root)
if rt == data:
    print('round-trip: BYTE-EXACT')
else:
    # find first diff
    i = next((k for k in range(min(len(rt), len(data))) if rt[k] != data[k]), min(len(rt), len(data)))
    print('round-trip differs at byte %d (len %d vs %d)' % (i, len(rt), len(data)))
    print('orig:', data[max(0,i-16):i+16].hex())
    print('new :', rt[max(0,i-16):i+16].hex())
    raise SystemExit(1)

# ---------- modify ----------
root['Version'] = (3, 6)
palette = root['Regions'][1]['Unnamed'][1]['BlockStatePalette'][1][1]
remapped = 0
for e in palette:
    nm = e['Name'][1]
    if nm in REMAP:
        new_name, prop_map = REMAP[nm]
        keep = KEEP_PROPS[new_name]
        new_e = {'Name': (8, new_name)}
        props = e.get('Properties')
        if props:
            new_props = {}
            for k, (kt, kv) in props[1].items():
                k2 = prop_map.get(k, k)
                if k2 in keep:
                    new_props[k2] = (kt, kv)
            if new_props:
                new_e['Properties'] = (10, new_props)
        e.clear(); e.update(new_e)
        remapped += 1
print('remapped %d palette entries' % remapped)

final = ser_root(root)
with gzip.open(DST, 'wb', compresslevel=6) as f:
    f.write(final)
print('written:', DST, os.path.getsize(DST))
