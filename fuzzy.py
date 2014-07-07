import random
import zlib
import hashlib
import math

base64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
S = 64

def md5hex(arr):
    m = hashlib.md5()
    m.update(str(bytearray(arr)))
    return m.hexdigest()

def sha1hex(arr):
    m = hashlib.sha1()
    m.update(str(bytearray(arr)))
    return m.hexdigest()

def stronghash(arr):
    return int(sha1hex(arr), 16)

def tobase64(num):
    return base64[num % 64]

def tochar(arr):
    return tobase64(stronghash(arr))

def generaterandombuffer(size):
    return [random.randint(0, 255) for x in xrange(size)]

def dld(s1, s2, c):
    """damerau-levenshtein distance"""
    inf = len(s1) + len(s2)

    da = [0] * c
    h = [[0 for x in xrange(len(s2) + 2)] for x in xrange(len(s1) + 2)]
    h[0][0] = inf
    for i in xrange(len(s1) + 1):
        h[i+1][0] = inf
        h[i+1][1] = i
    for i in xrange(len(s2) + 1):
        h[0][i+1] = inf
        h[1][i+1] = i

    for i in xrange(1, len(s1) + 1):
        db = 0
        for j in xrange(1, len(s2) + 1):
            i1 = da[base64.index(s2[j-1])]
            j1 = db
            if s1[i-1] == s2[j-1]:
                d = 0
            else:
                d = 1
            if d == 0:
                db = j
            m = min([(h[i  ][j  ] + d, d * 2), # subsitution
                     (h[i+1][j  ] + 1, 0    ), # insertion
                     (h[i  ][j+1] + 1, 0    ), # deletion
                     (h[i1 ][j1 ] + (i - i1 - 1) + 1 + (j - j1 - 1), 4)])
            h[i+1][j+1] = m[0] + m[1]
        da[base64.index(s1[i-1])] = i;
    e = min([h[len(s1) + 1][len(s2) + 1], (len(s1) + len(s2))])
    return 100 - ((100 * e) / (len(s1) + len(s2)))

class ssadler:
    def __init__(self, size):
        self.x = 0;
        self.y = 0;
        self.z = 0;
        self.c = 0;
        self.window = [0] * size
        self.size = size
    def value(self):
        return (self.x + self.y + self.z) & 0xffffffff
    def update(self, d):
        self.y = self.y - self.x
        self.y = self.y + self.size * d
        self.x = self.x + d
        self.x = self.x - self.window[self.c % self.size]
        self.window[self.c % self.size] = d
        self.c = self.c + 1
        self.z = self.z << 5 & 0xffffffff
        self.z = self.z ^ d

def getblocksize(n):
    bmin = 3
    return int(bmin * 2**math.floor(math.log((n/(S*bmin)),2)))

def fuzzyhash(arr):
    a = ssadler(7)

    s1 = ''
    s2 = ''
    blocksize = getblocksize(len(arr))

    for x in arr:
        a.update(x)
        if a.value() % blocksize == (blocksize - 1):
            s1 += tochar(a.window)
        if a.value() % (blocksize * 2) == ((blocksize * 2) - 1):
            s2 += tochar(a.window)

    return blocksize, s1, s2

bufsize = random.randint(50000, 150000)

buf = generaterandombuffer(bufsize)

b1, v1, _ = fuzzyhash(buf)

def mutate(arr, num):
    for x in xrange(num):
        arr[random.randint(0, len(arr) - 1)] = random.randint(0, 255)
    return arr

for y in [10**z for z in range(2, int(round(math.log(bufsize, 10))))]:
    bm, vm, _ = fuzzyhash(mutate(buf[:], y))
    print "%d changes %s- diff: %s/100" % (y, (4 - int(round(math.log(y, 10)))) * ' ', dld(v1, vm, S))

midbuf = generaterandombuffer(40000);

bufdiff = buf[:3 * bufsize / 10]
bufdiff.extend(midbuf)
bufdiff.extend(buf[-3 * bufsize / 10:])

bd, vd, _ = fuzzyhash(bufdiff)

print "new middle    - diff: %s/100" % (dld(v1, vd, S))

ba, va, _ = fuzzyhash(generaterandombuffer(bufsize))

print "all new       - diff: %s/100" % (dld(v1, va, S))
