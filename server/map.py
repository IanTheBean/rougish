import numpy
import random



def generate_map():
    integer_map = numpy.ones((100, 100))
    for i in range(500):
        tup = random_pos()
        integer_map[tup] = 2

        tup = random_pos()
        integer_map[tup] = 3

        tup = random_pos()
        integer_map[tup] = 4
    return integer_map

def random_pos():
    tup = random.randint(0, 99), random.randint(0, 99)
    return tup
