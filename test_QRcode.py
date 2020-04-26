from PIL import Image
import qrcode
latitude = 55.6514303
longitude = 12.555401
qr_code = qrcode.make(f'http://www.google.com/maps/place/{latitude},{longitude}')
qr_code.save('qr_location.png')