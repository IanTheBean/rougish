import numpy
import random


def generate_map():
    integer_map = numpy.ones((100, 100))
    # generate the ground patterns
    for i in range(500):
        tup = random_pos()
        integer_map[tup] = 2

        tup = random_pos()
        integer_map[tup] = 3

        tup = random_pos()
        integer_map[tup] = 4

    # generate the trees
    for i in range(1000):
        tup = random_pos()
        tree_type = random.randint(5, 10)
        integer_map[tup] = tree_type

    # create the barriers around the map
    for i in range(100):
        tree_type = random.randint(5, 10)
        integer_map[0, i] = tree_type
        integer_map[99, i] = tree_type

    for i in range(100):
        tree_type = random.randint(5, 10)
        integer_map[i, 0] = tree_type
        integer_map[i, 99] = tree_type

    return integer_map


def random_pos():
    tup = random.randint(0, 99), random.randint(0, 99)
    return tup
