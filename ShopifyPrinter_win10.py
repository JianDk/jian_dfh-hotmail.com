import socket
from escposCommands import escpos
from datetime import datetime
import win32print
import qrcode

class Printer:
    def __init__(self, printerParam):
        self.printerParam = printerParam
        self.connectToPrinter(printerParam)

    def connectToPrinter(self, printerParam):
        #determine first if it is a usb or network printer
        if printerParam['connectionMethod'] == 'network':
            self.printer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.printer.settimeout(60)
            try:
                self.printer.connect((printerParam['host'], printerParam['port'],))
            except:
                self.connectionStatus = False
                self.connectionDiagnostic = "The printer did not respond on {0} and port {1}".format(printerParam['host'], printerParam['port'])
                return

            self.connectionStatus = True
            self.connectionDiagnostic = 'Successfully connected'
        
        if printerParam['connectionMethod'] == 'usb':
            self.printer = win32print.OpenPrinter(printerParam['printerDriverName'])
            self.connectionDiagnostic = 'Success'
            self.connectionStatus = True

    
    def _printout(self, rawdata):
        if self.printerParam['connectionMethod'] == 'network':
            self.printer.sendall(rawdata)
            self._closeNetworkPrinter()
        
        if self.printerParam['connectionMethod'] == 'usb':
            hJob = win32print.StartDocPrinter(self.printer, 1, ("Test print", None, "RAW"))
            win32print.WritePrinter(self.printer, rawdata)
            win32print.EndPagePrinter(self.printer)
            win32print.ClosePrinter(self.printer)
    
    def _closeNetworkPrinter(self):
        self.printer.shutdown(socket.SHUT_RDWR)
        self.printer.close()

    def printTest(self):
        escpos1 = escpos()
        escpos1.align('left')
        escpos1.charSize(2,2)
        escpos1.text('Successful!')
        escpos1.newline(3)
        escpos1.cut()
        self._printout(escpos1.raw)
    
    def printDriver(self, customer_info, order_execution):
        escpos1 = escpos()
        escpos1.charSize(2,2)
        escpos1.text('Driver slip')
        escpos1.text(str(customer_info[0])) #order no
        escpos1.text(customer_info[1]) #Customer name
        escpos1.text(order_execution[4]) #delivery date
        escpos1.text(order_execution[5]) #delivery time
        escpos1.align('left')
        escpos1.charSize(1,1)
        escpos1.text(order_execution[10]) #note
        escpos1.charSize(2,2)
        escpos1.text(customer_info[2]) #Address
        escpos1.text(customer_info[3]) #phone
        #Generate QR code and print out
        latitude = customer_info[5]
        longitude = customer_info[6]
        qr_code = qrcode.make(f'http://www.google.com/maps/place/{latitude},{longitude}')
        qr_code.save('qr_location.png')
        escpos1.image('qr_location.png')
        escpos1.newline(3)
        escpos1.cut()
        self._printout(escpos1.raw)

    def printOrder_packer(self, orderexecution, customer, order_items, print_translation):
        escpos1 = escpos()
        escpos1.charSize(2,2)
        escpos1.align('center')
        escpos1.text(orderexecution[3]) #order type delivery or pickup
        escpos1.text(str(orderexecution[0])) #order no
        escpos1.text(orderexecution[4]) #Date for delivery
        escpos1.text(orderexecution[5]) #Time frame for delivery
        escpos1.newline(1)
        escpos1.text(orderexecution[2]) #Customer name
        escpos1.newline(1)
        #We will need a delay warning here

        escpos1.align('left')
        escpos1.charSize(1,1)
        escpos1.text('Customer note ')
        escpos1.text(orderexecution[-1]) #customer note
        escpos1.newline(2)
        #Print the items
        escpos1.charSize(2,2)
        for item in order_items:
            #try to see if a translation exists
            if item[0] in print_translation:
                dish = print_translation[item[0]]
            else:
                dish = item[0]

            if item[1] == 1:
                    escpos1.text(dish)
            else:
                escpos1.text(dish + ' ' + 'X' + ' ' + str(item[1]))

        escpos1.newline(3)
        escpos1.cut()
        self._printout(escpos1.raw)
    
    def printOrder_kitchen(self, orderexecution, customer, order_items, print_translation):
        escpos1 = escpos()
        escpos1.charSize(2,2)
        escpos1.align('center')
        escpos1.text(orderexecution[3]) #order type or delivery or pickup
        escpos1.text(str(orderexecution[0])) #order no
        escpos1.text(orderexecution[4]) #Date for delivery
        escpos1.text(orderexecution[5]) #Time frame for delivery
        escpos1.newline(1)
        escpos1.text(orderexecution[2]) #Customer name
        escpos1.newline(2)
        #We will need a delay warning here

        #Print the items
        escpos1.charSize(2,2)
        for item in order_items:
            #try to see if a translation exists
            if item[0] in print_translation:
                dish = print_translation[item[0]]
            else:
                dish = item[0]

            if item[1] == 1:
                    escpos1.text(dish)
            else:
                escpos1.text(dish + ' ' + 'X' + ' ' + str(item[1]))

        escpos1.newline(3)
        escpos1.cut()
        self._printout(escpos1.raw)
    
    def printDelivery(self, printdict, translation):
        escpos1 = escpos()
        escpos1.align('center')
        escpos1.bold('on')
        escpos1.charSize(2,2)
        escpos1.text(printdict['deliveryType'])
        escpos1.newline(1)
        escpos1.text(printdict['executionTime'])
        escpos1.newline(1)
        escpos1.text(printdict['name'])
        escpos1.newline(1)
        escpos1.text('Shopify Order No ' + str(printdict['orderno']))
        escpos1.newline(3)
        #Print out items
        for item in printdict['items']:
            #Check translation 
            if item[0] in translation:
                itemstr = translation[item[0]]
            else:
                itemstr = item[0]

            escpos1.text(itemstr + ' x ' + str(item[1]))
            escpos1.newline(1)
        escpos1.cut()
        self._printout(escpos1.raw)
    
    def left_right_alightPrinterstr(self, totalspace, leftstr, rightstr):
        '''
            Given the totalspace which is an int containing total number of characters that can be on the line, and the leftstr and rightstr, 
            the function will generate the printer string so that the left and right string can all be printed in one line
        '''
        whitespace = totalspace - len(leftstr) - len(rightstr)
        if whitespace < 1:
            printerstr = leftstr + '\n' + rightstr
            return printerstr
        else:
            leftstr = leftstr.ljust(len(leftstr) + whitespace)
            printerstr = leftstr + rightstr
            return printerstr

        