import itertools

bukvi_blya = ['А', 'В', 'Е', 'Н', 'С']
c = 0


for i in itertools.product(bukvi_blya, repeat=4):
    c += 1
    w_str = "".join(i)

    
    print(c, w_str)
