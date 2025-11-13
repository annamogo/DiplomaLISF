import numpy as np
from img_fringe.data_fringe import *

my_stack = DataFringeStack()
my_flatten = [[1,2,3,2,4],[1,2,3,4,5],[5,4,3,2,1]]

my_stack.from_flatten(my_flatten)

my_seq = [1,2,3,4,5]
my_obj = DataFringe(my_seq)

print(my_stack, my_obj.data, sep="\n")
