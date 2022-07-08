import re
from collections import Counter, OrderedDict
import json
import os

class OrderedCounter(Counter, OrderedDict):
    'Counter that remembers the order elements are first encountered'

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, OrderedDict(self))

    def __reduce__(self):
        return self.__class__, (OrderedDict(self),)

#string = "\n**kahfdl sjd,sadjflskj \n*HELLO YOU    , sljfdls, \n**sifdsoijfsl       \n*RAVI MASAL , asklhdasl, asjdslajfd, \n\n\n*kdjsfklajfa \n*KEY"

# Get the list of all files in directory tree at given path
listOfFiles = list()
for (dirpath, dirnames, filenames) in os.walk(r'D:\HMC_translation\BMT_Analysis_model'):
    listOfFiles += [os.path.join(dirpath, file) for file in filenames if file.endswith('.inp')]
# print(len(listOfFiles))
# print('\n'.join(listOfFiles))
all_keys = []
for file_name in listOfFiles:
    f_name = file_name.split('\\')[-1]
    file = open(file_name, 'r')
    x = re.findall(r"\n[*]{1}[A-Za-z]+[ ]?[A-Za-z]+", file.read())
    file.close()
    x = [i.replace('\n','') for i in x]
    all_keys.extend(x)
    y = OrderedCounter(x)
    file_out = open('keyword_info_'+f_name+'.txt', 'w')
    file_out.write(json.dumps(y, indent=4))
    file_out.close()

Total_keywords_all_inputs = OrderedCounter(all_keys)
print(json.dumps(Total_keywords_all_inputs, indent=4))
