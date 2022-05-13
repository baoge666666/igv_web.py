from audioop import ratecv
from tkinter import N
from turtle import color
import pytest
from numpy.random import default_rng
from itertools import islice
from math import exp, floor, log
from random import random, randrange
from typing import Any, Iterable, Optional
import numpy as np
import matplotlib.pyplot as plt
import time


EOI = object

def algorithm_r(iterable: Iterable, n: int):
    iterable = iter(iterable)
    # Initialise reservoir with first n elements
    reservoir = list(islice(iterable, n))

    for t, x in enumerate(iterable, n + 1):
        m = randrange(t)
        if m < n:  # Make the next record a candidate, replacing one at random
            reservoir[m] = x

    return reservoir

def method_4(iterable: Iterable, n: int):
    iterable = iter(iterable)
    # Initialise reservoir with first n elements
    reservoir = np.array(list(islice(iterable, n)))
    # Assign random numbers to the first n elements
    u_array = np.array([random() for _ in range(n)])

    # Track the index of the largest u-value
    u_max_idx = u_array.argmax()
    for x in iterable:
        u = random()
        if u < u_array[u_max_idx]:
	    # Replace largest u-value
            u_array[u_max_idx] = u
	    # Replace corresponding reservoir element
            reservoir[u_max_idx] = x
	    # Update largest u-value
            u_max_idx = u_array.argmax()

    return reservoir

def algorithm_l(iterable: Iterable, n: int):
    iterable = iter(iterable)
    # Initialise reservoir with first n elements
    reservoir = list(islice(iterable, n))

    w = exp(log(random()) / n)

    while True:
        s = floor(log(random()) / log(1 - w))
        next_elem = nth(iterable, s + 1, default=EOI)

        if next_elem is EOI:
            return reservoir

        reservoir[randrange(0, n)] = next_elem
        w *= exp(log(random()) / n)

    return reservoir


def nth(iterable: Iterable, n: int, default: Optional[Any] = None):
    """Returns the ``n``th item in ``iterable`` or a default value.

    Credit: https://docs.python.org/3.7/library/itertools.html#itertools-recipes
    """
    return next(islice(iterable, n, None), default)

def test_sample_distribution():
    # Test parameters - adjust to affect the statistical significance of the test.
    n = 1000  # Sample size
    population_size = n * 1000  # Input size.
    rate = 0.1  # Exponential distribution rate parameter.
    tolerance = 0.1  # How close to the real rate the MLE needs to be.

    # Generate exponentially distributed data with known parameters
    rng = default_rng()
    population = rng.exponential(
        1 / rate,  # numpy uses the scale parameter which is the inverse of the rate
        population_size,
    )
    population.sort()


    N = 2000
    # Run Reservoir Sampling to generate a sample
    start = time.time()
    sample = algorithm_r(population, N)
    end = time.time()

    print(str(end-start))

    # Calculate the MLE for the rate parameter of the population distribution
    rate_mle = len(sample) / sum(sample)
    print(rate_mle)

    assert pytest.approx(rate_mle, tolerance) == rate

def test_sample():

    n = 1000  # Sample size
    population_size = n * 1000  # Input size.
    rate = 0.1  
    N = 2000

    time_1 = []
    time_2 = []
    time_3 = []
    population_size = [100000,500000,1000000,2000000,5000000,7000000,10000000,30000000,70000000,100000000]
    for i in population_size:
        rng = default_rng()
        population = rng.exponential(
            1 / rate,  
            i,
        )
        population.sort()
        start_1 = time.time()
        algorithm_r(population, N)
        end_1 = time.time()
        start_2 = time.time()
        method_4(population,N)
        end_2 = time.time()
        start_3 = time.time()
        algorithm_l(population,N)
        end_3 = time.time()
        time_1.append(end_1-start_1)
        time_2.append(end_2-start_2)
        time_3.append(end_3-start_3)
    
    plt.plot(population_size,time_1)
    plt.plot(population_size,time_2,color='yellow')
    plt.plot(population_size,time_3,color='green')
    plt.legend(['Reservoir','method_4','algorithm_l'])
    plt.show()

test_sample()