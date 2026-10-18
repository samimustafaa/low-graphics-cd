"""Verify packaged icon sizes without requiring Pillow at runtime."""
from pathlib import Path
import struct
import unittest
ROOT=Path(__file__).resolve().parents[1]
class IconTests(unittest.TestCase):
    def test_native_sizes_are_in_ico_and_tk_png_assets(self):
        data=(ROOT/'app.ico').read_bytes();reserved,kind,count=struct.unpack_from('<HHH',data)
        self.assertEqual((reserved,kind),(0,1));sizes=set()
        for i in range(count):
            width,height,_,_,_,bits,size,offset=struct.unpack_from('<BBBBHHII',data,6+16*i)
            width=width or 256;height=height or 256
            self.assertEqual(width,height);self.assertEqual(bits,32)
            self.assertLessEqual(offset+size,len(data));sizes.add(width)
            png=(ROOT/'icons'/f'icon-{width}.png').read_bytes()
            self.assertEqual(png[:8],b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack_from('>II',png,16),(width,width))
        self.assertEqual(sizes,{16,20,24,28,32,40,48,64,96,128,256})
        self.assertEqual(struct.unpack_from('>II',(ROOT/'app-mark.png').read_bytes(),16),(1024,1024))
