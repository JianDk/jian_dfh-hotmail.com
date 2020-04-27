import win32print
printer = win32print.OpenPrinter("EPSON TM-T20II Receipt")
hJob = win32print.StartDocPrinter(printer, 1, ("Test print", None, "RAW"))
rawdata = b'\x1b\x40' + bytes("hello world, æ, ø, å", 'cp865') + b'\n'*5
win32print.WritePrinter(printer, rawdata)
win32print.EndPagePrinter(printer)
win32print.ClosePrinter(printer)