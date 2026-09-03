import os
import re
'''
path = 'D:\Eli\smarteye2.1\\少数据.txt'
def read_datas(path):
    datas=[]
    with open(path,'r',encoding='utf-8') as f:
        while True:
            data = f.readline().rstrip()
            if data:
                data1 = re.sub(r'[, ]',',',data).split(",")
                datas.append(data1)
            else:
                break
    return datas
datas=read_datas(path)
for i in range(0,len(datas)):
    print(type(datas[i][1][0:5]))



c=[]
a=[['11:00',10],['11:00',11],['11:02',12],['11:02',13],['11:03',14],['11:04',4],['11:06',6]]
for i in range(0,len(a)):
    b=a[i][0].split(':')
    b.append(a[i][1])
    for j in range (0,len(b)):
        b[j]=int(b[j])
    c.append(b)
print(c)

e=[]
n=0
for i in range(0,len(c)):
    for j in range(i+1,len(c)):
        if i==0:
            e.append(c[i])

        if c[j][1] in e[len(e)-1] and c[j][0] in e[len(e)-1]:
            break
        else:
            d1 = c[i][1] + 2 #4
            d0 = c[i][0]
            if d1 > 60:
                d1=d1-60
                d0=c[i][0]+1
            if c[j][0]==d0 and c[j][1]==d1:
                n=j
                e.append(c[j])
                break
            else:
                continue


print(e)


'''


