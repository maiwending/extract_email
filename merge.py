
import os
from PyPDF2 import PdfFileMerger

x = [a for a in os.listdir() if a.endswith(".pdf")]

list=[elem[:-4] for elem in x ]

for file in sorted(list):
    list.sort(key=int)
# x.sort()

#list

# for file in sorted(x):
#     print(file)

merger = PdfFileMerger()

for pdf in list:
    merger.append(open(pdf+'.pdf', 'rb'))

with open("result.pdf", "wb") as fout:
    merger.write(fout)