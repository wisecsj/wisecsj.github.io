f_name = 'a.txt'

i = 0;
f = open(f_name);

w = open('b.txt','w')
for line in f:
    line = line.split(' ')
    line = line[0]+line[1]+line[4]
    w.write(line+'\n')
