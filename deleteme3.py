import csv
import json

f = open('products_export_1.csv')
read_obj = csv.reader(f)
titledict = dict()

for item in read_obj:
    #title is in second column
    titledict[item[1]] = ''

titledict.pop('Title')
with open('Shopify_item2print.txt', 'w') as outfile:
    json.dump(titledict, outfile, indent=4, sort_keys=True)

print(titledict)