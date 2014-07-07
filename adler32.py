import random
import zlib

def generaterandombuffer(seed, size):
    random.seed(seed)
    return [random.randint(0, 255) for x in xrange(size)]

buf = generaterandombuffer(2, 100000);

random.seed();

window = random.randint(0, len(buf) - 1)
offset = random.randint(0, len(buf)-window-1)

print window, offset
match = zlib.adler32(buffer(bytearray(buf), offset, window)) & 0xffffffff

print hex(match)

class adler32:
    def __init__(self):
        self.A = 1
        self.B = 0
        self.count = 0
    def value(self):
        return ((self.B << 16) | self.A) & 0xffffffff
    def add(self, x):
        self.A = (self.A + x) % 65521
        self.B = (self.A + self.B) % 65521
        self.count += 1
    def rotate(self, x1, xn):
        self.A = (self.A - x1 + xn) % 65521
        self.B = (self.B - self.count * x1 + self.A - 1) % 65521

a = adler32()

for x in buf[0:window]:
    a.add(x)

i = 0
while a.value() != match:
    a.rotate(buf[i], buf[window+i])
    i += 1

print i
print hex(a.value())
