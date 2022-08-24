
from multiprocessing.dummy import Pool




def f(x):
    return x*x

with Pool(8) as p:
    res = p.map(f, [1,2,3,4])

    print(res)

xxx    
