# -*- coding: utf-8 -*-
import gzip, struct

p = r'D:/GT-New/schematics/EARTH-STAR (完稿).litematic'
data = gzip.open(p, 'rb').read()
print('decompressed size:', len(data))

def tag_name(off):
    t = data[off]; off += 1
    n = struct.unpack('>H', data[off:off+2])[0]; off += 2
    return t, data[off:off+n].decode('utf-8', 'replace'), off + n

# root
t, name, off = tag_name(0)
print('root tag', t, repr(name))

def walk_compound(off, depth, maxdepth=3):
    while True:
        t, name, off = tag_name(off)
        pad = '  ' * depth
        if t == 0:
            print(pad + '<end>')
            return off
        print(pad + 'TAG%d %s' % (t, name), end=' ')
        if t == 10:
            print('{')
            off = walk_compound(off, depth + 1, maxdepth)
            if depth + 1 >= maxdepth:
                # skip rest quickly: scan forward skipping this compound fully
                off = skip_compound_body(off - 0, depth + 1)
                return off
            continue
        elif t == 3:
            v = struct.unpack('>i', data[off:off+4])[0]; off += 4
            print('=', v)
        elif t == 8:
            n = struct.unpack('>H', data[off:off+2])[0]
            print('=', data[off+2:off+2+n].decode('utf-8', 'replace')); off += 2 + n
        elif t == 9:
            et = data[off]; n = struct.unpack('>i', data[off+1:off+5])[0]; off += 5
            print('[len=%d et=%d] (skipped)' % (n, et))
            return off  # caller handles: stop here for now
        elif t == 7:
            n = struct.unpack('>i', data[off:off+4])[0]; off += 4 + n
            print('[%d bytes]' % n)
        elif t == 11:
            n = struct.unpack('>i', data[off:off+4])[0]; off += 4 + 4 * n
            print('[%d ints]' % n)
        elif t == 12:
            n = struct.unpack('>i', data[off:off+4])[0]; off += 4 + 8 * n
            print('[%d longs]' % n)
        else:
            print('!! unhandled tag', t)
            return off

def skip_compound_body(off, depth):
    # skip a whole compound body (we are positioned at first tag after '{' consumed... )
    while True:
        t, name, off2 = tag_name(off)
        if t == 0:
            return off2
        raise NotImplementedError

off = walk_compound(off, 0, maxdepth=2)
print('stopped at', off, 'remaining:', len(data) - off)
print('next 64 bytes:', data[off:off+64].hex())
