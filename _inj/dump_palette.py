# -*- coding: utf-8 -*-
import gzip, struct, json

p = r'D:/GT-New/schematics/EARTH-STAR (完稿).litematic'
data = gzip.open(p, 'rb').read()
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
    global pos
    if t == 0: return None
    if t == 1: v = data[pos]; pos += 1; return v
    if t == 2: v = struct.unpack('>h', data[pos:pos+2])[0]; pos += 2; return v
    if t == 3: return i4()
    if t == 4: v = struct.unpack('>q', data[pos:pos+8])[0]; pos += 8; return v
    if t == 5: v = struct.unpack('>f', data[pos:pos+4])[0]; pos += 4; return v
    if t == 6: v = struct.unpack('>d', data[pos:pos+8])[0]; pos += 8; return v
    if t == 7:
        n = i4(); b = data[pos:pos+n]; pos += n; return b
    if t == 8: return name_str()
    if t == 9:
        et = u1(); n = i4()
        return [read_payload(et) for _ in range(n)]
    if t == 10:
        d = {}
        while True:
            et = u1()
            if et == 0: return d
            nm = name_str()
            d[nm] = read_payload(et)
        return d
    if t == 11:
        n = i4(); pos += 4*n; return None
    if t == 12:
        n = i4(); pos += 8*n; return None
    raise ValueError(t)

t = u1(); name_str()
root = read_payload(t)
palette = root['Regions']['Unnamed']['BlockStatePalette']
names = set()
for e in palette:
    names.add(e['Name'])
print('palette entries:', len(palette), 'unique block names:', len(names))
with open(r'D:/GT-New/_inj/palette_names.txt', 'w', encoding='utf-8') as f:
    for n in sorted(names):
        f.write(n + '\n')
print('written to palette_names.txt')
# print suspicious: everything after minecraft:z in ascii order? just print all, grouped
for n in sorted(names):
    print(n)
