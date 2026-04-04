import struct, zlib

def create_png(filename, size):
    """Create a simple colored square PNG icon."""
    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    # Shield blue color
    r, g, b = 29, 155, 240

    # Build raw pixel data
    raw = b''
    for y in range(size):
        raw += b'\x00'  # filter byte
        for x in range(size):
            # Simple shield shape
            cx, cy = size / 2, size / 2
            in_shield = (abs(x - cx) / (size * 0.4) + max(0, (y - cy)) / (size * 0.5)) < 1 and y > size * 0.1
            if in_shield:
                raw += struct.pack('BBBB', r, g, b, 255)
            else:
                raw += struct.pack('BBBB', 0, 0, 0, 0)

    # Write PNG
    with open(filename, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)))
        f.write(chunk(b'IDAT', zlib.compress(raw)))
        f.write(chunk(b'IEND', b''))

for s in [16, 48, 128]:
    create_png(f'extension/icons/icon{s}.png', s)
    print(f'Created icon{s}.png')
