from re import T
import time
#import gymnasium as gym
#import gym 
import math
import random
import numpy
import pickle
import os
import matplotlib.pyplot as plt


def main():
   
   
    rewards = numpy.load('rewards.npy')
    Lista=numpy.zeros(100500)
        
    sum_rewards = numpy.zeros(100500)
    for t in range(100500):
        sum_rewards[t] = numpy.sum(rewards[max(0, t-100):(t+1)])
    plt.plot(sum_rewards)
    plt.savefig('refuerzo.png')

    

    print('se acabo')

if __name__ == '__main__':
    main()