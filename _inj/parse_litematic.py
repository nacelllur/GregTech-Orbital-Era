# -*- coding: utf-8 -*-
import gzip, struct, sys, os

def read_payload(t, f):
    if t == 0: return None
    if t == 1: return struct.unpack('>b', f.read(1))[0]
    if t == 2: return struct.unpack('>h', f.read(2))[0]
    if t == 3: return struct.unpack('>i', f.read(4))[0]
    if t == 4: return struct.unpack('>q', f.read(8))[0]
    if t == 5: return struct.unpack('>f', f.read(4))[0]
    if t == 6: return struct.unpack('>d', f.read(8))[0]
    if t == 7:
        n = struct.unpack('>i', f.read(4))[0]
        b = f.read(n)
        assert len(b) == n, 'short byte array'
        return b'<%d bytes>' % n
    if t == 8:
        n = struct.unpack('>H', f.read(2))[0]
        return f.read(n).decode('utf-8', 'replace')
    if t == 9:
        et = f.read(1)[0]
        n = struct.unpack('>i', f.read(4))[0]
        assert 0 <= n < 10**8
        return [read_payload(et, f) for _ in range(n)]
    if t == 10:
        d = {}
        while True:
            et = f.read(1)[0]
            if et == 0: break
            n = struct.unpack('>H', f.read(2))[0]
            name = f.read(n).decode('utf-8', 'replace')
            d[name] = read_payload(et, f)
        return d
    if t == 11:
        n = struct.unpack('>i', f.read(4))[0]
        return b'<%d ints>' % n
    if t == 12:
        n = struct.unpack('>i', f.read(4))[0]
        return b'<%d longs>' % n
    raise ValueError('bad tag %d' % t)

paths = [
    r'D:/GT-New/schematics/EARTH-STAR (完稿).litematic',
    r'D:/GT-New/schematics/EARTH-STAR/EARTH-STAR (完稿).litematic',
]
for p in paths:
    print('=' * 20, repr(p), os.path.getsize(p))
    with gzip.open(p, 'rb') as f:
        t = f.read(1)[0]
        n = struct.unpack('>H', f.read(2))[0]
        rootname = f.read(n).decode('utf-8', 'replace')
        root = read_payload(t, f)
        rest = f.read()
    print('rootname:', rootname, 'trailing bytes:', len(rest))
    for k, v in root.items():
        if isinstance(v, dict):
            print(' ', k, '-> dict, keys:', list(v.keys())[:10])
        else:
            print(' ', k, '=', v)
    regs = root.get('Regions', {})
    for rn, r in regs.items():
        print('  region %r keys:' % rn, list(r.keys()) if isinstance(r, dict) else r)
        if isinstance(r, dict):
            for k, v in r.items():
                print('    ', k, '=', v if not isinstance(v, bytes) else v)
