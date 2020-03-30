from PIL import Image, ImageOps
import six

class escpos:
    def __init__(self):
        self.raw = self.initiate()

    def initiate(self):
        '''
        ESC @

        Clears the data in the print buffer and resets the printer modes to the modes that were in effect when the power was turned on.
        Any macro definitions are not cleared.
        Offline response selection is not cleared.
        Contents of user NV memory are not cleared.
        NV graphics (NV bit image) and NV user memory are not cleared.
        The maintenance counter value is not affected by this command.
        Software setting values are not cleared. 
        '''
        return b'\x1b\x40'

    def charSize(self, sizeWidth, sizeHeight):
        '''
        GS !
        Select character size
        ''' 
        if sizeWidth > 8:
            sizeWidth = 8
        
        if sizeHeight < 1:
            sizeWidth = 1
        
        if sizeHeight < 1:
            sizeHeight = 1
        
        if sizeHeight > 8:
            sizeHeight = 8
        
        self.raw = self.raw + bytes([0x1d, 0x21, 16*(sizeWidth-1) + (sizeHeight-1)])

    def align(self, alignment):
        '''
        ESC a
        Justification. alignment is a string and can either be:
        left
        center
        right
        
        When Standard mode is selected, this command is enabled only when processed at the beginning of the line in Standard mode.
        The justification has no effect in Page mode.
        This command executes justification in the print area set by GS L and GS W.
        This command justifies printing data (such as characters, all graphics, barcodes, and two-dimensional code) and space area set by HT, ESC $, and ESC 
        Settings of this command are effective until ESC @ is executed, the printer is reset, or the power is turned off.
        '''

        constant = b'\x1b' + b'\x61'
        if alignment == 'left':
            self.raw = self.raw + constant + b'\x00'
        
        if alignment == 'center':
            self.raw = self.raw + constant + b'\x01'
        
        if alignment == 'right':
            self.raw = self.raw + constant + b'\x02'
        
    def underline(self, n):
        '''
        ESC -
        Turn underline mode on/off
        n = 0: no underline
        n = 1: underline one dot thick
        n = 2: underline two dots thick
        '''
        constant = b'\x1b' + b'\x2d'
        if n ==0:
            self.raw = self.raw + constant + b'\x00'

        if n == 1:
            self.raw = self.raw + constant + b'\x01'
        
        if n == 2:
            self.raw = self.raw + constant + b'\x02'

    def bold(self, switch):
        '''
        ESC E
        Turn emphasized mode on/off
        if switch = 'on', the characters followed will be bold. If switch = 'off', the characters following will have bold switched 
        off.
        '''
        constant = b'\x1b' + b'\x45'
        if switch == 'on':
            self.raw = self.raw + constant + b'\x01'
        
        if switch == 'off':
            self.raw = self.raw + constant + b'\x00'

    def text(self, textstr):
        '''
        Creates a binary from the text string
        '''
        self.raw = self.raw + bytes(textstr, 'utf-8') + b'\n'

    def newline(self, n):
        '''
        newline(n) corresponds to b'\n' + b'\n' ... + b'\n' n times
        '''
        self.raw = self.raw + b'\n' * n

    def cut(self):
        '''
        GS V
        Implement a partial cutting method
        '''
        self.raw = self.raw + b'\x1d' + b'\x56' + six.int2byte(66) + b'\x00'

    def _int_low_high(self, inp_number, out_bytes):
        """ Generate multiple bytes for a number: In lower and higher parts, or more parts as needed.
        :param inp_number: Input number
        :param out_bytes: The number of bytes to output (1 - 4).
        """
        max_input = (256 << (out_bytes * 8) - 1)
        if not 1 <= out_bytes <= 4:
            raise ValueError("Can only output 1-4 bytes")
        if not 0 <= inp_number <= max_input:
            raise ValueError("Number too large. Can only output up to {0} in {1} bytes".format(max_input, out_bytes))
        
        outp = b''
        for _ in range(0, out_bytes):
            outp += six.int2byte(inp_number % 256)
            inp_number //= 256
        
        return outp

    def image(self, img_path, alignment = 'center'):
        '''
        Given the path to the image and align that either can be left, center or right the print code for image printing is returned. 
        Note the img_path is given as a UNIX path with separator as '/'
        '''
        #Import the image from the path
        #Read in the image
        img = Image.open(img_path)
        imgdub = img
        #convert the image from 8-bit to (4x8-bit pixels, true color with transparency mask)
        img = img.convert('RGBA')
        #Construct a new image with white background
        im = Image.new('RGB', img.size, (255, 255, 255,))
        im.paste(img, mask=img.split()[3])
        # Convert down to greyscale
        im = im.convert("L")
        # Invert: Only works on 'L' images
        im = ImageOps.invert(im)
        #Pure black and white
        imbw = im.convert("1")

        #Printer language
        #GS v0

        #Image width bytes
        im_width_bytes = (imbw.width + 7) >> 3
        _, height = imbw.size

        if alignment == 'left':
            self.align('left')

        if alignment == 'center':
            self.align(alignment = 'center')
        
        if alignment == 'right':
            self.align('right')

        self.raw = self.raw + b'\x1d' + b"\x76" + b"\x30" + six.int2byte(0) + self._int_low_high(im_width_bytes, 2) +\
            self._int_low_high(height,2) + imbw.tobytes()
        
        self.raw = self.raw + b'\n'
