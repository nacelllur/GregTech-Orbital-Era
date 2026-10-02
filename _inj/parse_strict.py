# -*- coding: utf-8 -*-
import gzip, struct, sys

p = r'D:/GT-New/schematics/EARTH-STAR (完稿).litematic'
data = gzip.open(p, 'rb').read()
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

def read_payload(t, depth):
    global pos
    if t == 0: return None
    if t == 1: v = data[pos]; pos += 1; return v
    if t == 2: v = struct.unpack('>h', data[pos:pos+2])[0]; pos += 2; return v
    if t == 3: return i4()
    if t == 4: v = struct.unpack('>q', data[pos:pos+8])[0]; pos += 8; return v
    if t == 5: v = struct.unpack('>f', data[pos:pos+4])[0]; pos += 4; return v
    if t == 6: v = struct.unpack('>d', data[pos:pos+8])[0]; pos += 8; return v
    if t == 7:
        n = i4()
        assert 0 <= n <= len(data), 'bytearray len %d at %d' % (n, pos)
        b = data[pos:pos+n]; pos += n; return b'<%d bytes>' % n
    if t == 8:
        return name_str()
    if t == 9:
        et = u1(); n = i4()
        assert 0 <= n <= len(data), 'list len %d at %d' % (n, pos)
        return [read_payload(et, depth+1) for _ in range(n)]
    if t == 10:
        d = {}
        while True:
            start = pos
            et = u1()
            if et == 0:
                return d
            nm = name_str()
            v = read_payload(et, depth+1)
            if depth <= 2:
                desc = v
                if isinstance(v, list): desc = 'list[%d]' % len(v)
                elif isinstance(v, dict): desc = 'dict%s' % (list(v.keys())[:12],)
                elif isinstance(v, bytes): desc = v
                print('%08d  TAG%-2d %-24s %s' % (start, et, nm[:24], desc))
            d[nm] = v
    if t == 11:
        n = i4()
        assert 0 <= n <= len(data) // 4, 'intarray len %d at %d' % (n, pos)
        pos += 4 * n; return b'<%d ints>' % n
    if t == 12:
        n = i4()
        assert 0 <= n <= len(data) // 8, 'longarray len %d at %d' % (n, pos)
        pos += 8 * n; return b'<%d longs>' % n
    raise ValueError('bad tag %d at %d' % (t, pos - 1))

t = u1()
rootname = name_str()
print('root tag type', t, 'name', repr(rootname))
root = read_payload(t, 0)
print()
print('=== fully parsed OK, trailing bytes:', len(data) - pos)
print('root keys:', list(root.keys()))
for k in ('Version', 'SubVersion', 'MinecraftDataVersion'):
    if k in root: print(k, '=', root[k])
if 'Metadata' in root:
    print('Metadata:', root['Metadata'])
regs = root['Regions']
print('Regions:', list(regs.keys()))
for rn, r in regs.items():
    print('region %r keys: %s' % (rn, list(r.keys()) if isinstance(r, dict) else r))
    if isinstance(r, dict):
        for k, v in r.items():
            if isinstance(v, list): v = 'list[%d]' % len(v)
            elif isinstance(v, dict): v = 'dict%s' % (list(v.keys()),)
            print('   ', k, '=', v)
