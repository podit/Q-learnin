# Import numpy for array managment and timeit to time execution
import numpy as np
from timeit import default_timer as timer

# Import control script
import doExp as d
# Import plotting functions
import plotKew as plt
# Import single and double Q-Learning classes
from nuSinKew import SinKew
from dblKew import DblKew

# Set initialisation policy for Q-table
initialisation = 'uniform'      # uniform, ones, zeros, random

# Set on-policy (sarsa) or off-policy (q_lrn) control method for training
policy = 'q_lrn'                # q_lrn, sarsa

# Control flags for double Q-learning, epsilon decay and expontntial penalties
doubleFlag = False
eDecayFlag = False
logFlag = False

# Flags to report each run and each resolution step
# Report run number and average reward from test for each run
profileFlag = True
# Report episode and epsilon value as well as reward for each resolution step
verboseFlag = False

# Render flags for testing and training
renderTest = False
# Render training at each resolution step
renderTrain = False

# Set openai gym environment (CartPole and MountainCar have been tested)
environment = 'CartPole-v1'     # CartPole-v1, MountainCar-v0

# Flags for continuous observation and action spaces
contOS = True
contAS = False
# Discretisation factor to set number of bins for continuous
#   observation/action spaces depending on flags
discretisation = 8

# Set resolution for bins to record performance every <resolution> epsiodes
resolution = 5

# Set max steps in the environment
maxSteps = 500
# Set number of tests to be run (average is reported)
nTests = 100

# Set penalty to be applied at episode completion (positive acts as reward)
penalty = 0

# Used when logFlag is enabled
# Set exponent for exponential penalty and length of applied steps
exponent = -0.005
length = 5

# Set number of episodes and runs to be completed by the agent
episodes = 1000
# Episodes constitute run length before testing
runs = 1000

# Set hyper-parameters for use in bellman equation for updating Q table
# Discount factor
gamma = 0.99
# Learning rate
alpha = 0.5

# Set epsilon value for constant e-greedy method
epsilon = 0.1

# Used whrn eDecayFlag is enabled
# Set decay coefficient
decay = 1.5
# Set epsilon start value
epsilonDecay = 0.25
# Calculate the decay period
eDecayStart = 100
eDecayEnd = (episodes // decay) + eDecayStart
# Calculate decay rate
eDecayRate = epsilonDecay / eDecayEnd

# Create number of individual data points for run length
#dataPoints = episodes / resolution

# Start experiment timer
start = timer()

# Number of experimental parameters
experiments = 6

# List of experimental parameters to be tested
values = [100, 250, 500, 750, 1000, 1500]

# List of values to be revorded and compared in boxplot
aggr_rewards = [None] * experiments

# Iterate through each experimental value and run Q-learning
for e in range(experiments):

    # Chenge value to the correponding hyper-parameter
    episodes = values[e]

    dataPoints = episodes / resolution
    # Initialise double or single QL class with the doubleFlag value provided
    if doubleFlag: q = DblKew(initialisation, policy, environment, contOS,
                contAS, discretisation, maxSteps, nTests, logFlag, verboseFlag,
                renderTest, renderTrain)
    else: q = SinKew(initialisation, policy, environment, contOS, contAS,
                discretisation, maxSteps, nTests, logFlag, verboseFlag,
                renderTest, renderTrain)

    # Run experiment passing relevent variables to do script to run QL,
    #   recording performance of tests and training for plotting
    aggr_rewards[e], aggr_stds, aggr_ts_r, aggr_ts_r_min, aggr_ts_r_max,\
            aggr_ts_r_uq, aggr_ts_r_lq =\
            d.do(q, runs, episodes, resolution, dataPoints, profileFlag, eDecayFlag,
            gamma, alpha, epsilon, decay, epsilonDecay, eDecayStart, eDecayEnd,
            eDecayRate, penalty, exponent, length, renderTest)

    # Print the average reward and standard deviation of test results for
    #   all the runs over the experiment
    print('Total average reward:',
            np.average(aggr_rewards[e]),
            np.std(aggr_rewards[e]), 'Stds:',
            np.average(aggr_stds), np.std(aggr_stds))

    # Print experiment number to show progress
    print('Expreiment:', e, 'of:', experiments)
    # Print experiment parameters
    print('Episodes:', episodes, 'Gamma:', gamma, 'Alpha:',
            alpha, 'Penalty:', penalty)
    if eDecayFlag: print('Decaying Epsilon Start:', epsilonDecay, 'Decay:',
            decay, 'Rate:', eDecayRate)
    else: print('Epsilon:', epsilon)
    if logFlag: print('Exponential penalties exponent:', exponent, 'Length:',
            length)
    print('------------==========================------------')
    input('Show plots')
    plt.plot(np.mean(aggr_ts_r, axis=0), np.mean(aggr_ts_r_min, axis=0),
            np.mean(aggr_ts_r_max, axis=0), np.mean(aggr_ts_r_uq, axis=0),
            np.mean(aggr_ts_r_lq, axis=0))

# End timer and print time
end = timer()
print('Time:', end-start)
print('Discretisation Factor:', discretisation)
# Denote the method flag and environment upon completion
print('Method used:', policy)
print('Double?:', doubleFlag)
print('Environment:', environment)
# Wait for input to show plot


