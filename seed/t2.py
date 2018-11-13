# 筛选出符合条件的seed并保存
read_name = 'a.txt'
write_name = 'b.txt'

f = open(read_name);

w = open(write_name,'w')
for line in f:
    line = line.split(' ')
    line = line[0]+line[1]+line[4]
    w.write(line+'\n')