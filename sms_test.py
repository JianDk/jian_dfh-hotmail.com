import json

mydict = dict()
mydict['email'] = 'kontakt@dimsum.dk'
mydict['host'] = "imap.gigahost.dk"
mydict['port'] = 993

mydict['Shopify_acc1'] = dict()
mydict['Shopify_acc1']['location'] = 'HK'
mydict['Shopify_acc1']['email'] = 'alexanderydesign@gmail.com'
mydict['Shopify_acc1']['password'] = 'ale0099Y'

mydict['Shopify_acc2'] = dict()
mydict['Shopify_acc2']['location'] = 'DK'
mydict['Shopify_acc2']['email'] = 'jian_dfh@hotmail.com'
mydict['Shopify_acc2']['password'] = 'PASSport1'

with open('credientials.txt', 'w') as outfile:
    json.dump(mydict, outfile)