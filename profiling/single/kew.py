import gym
import math
import numpy as np

# Q-learning class to train and test q table for given environment
class Kew:
    def __init__(self, dis, pol, log, verboseFlag):
        # Set poliy bools for control of Q-learning
        if pol == 'q_lrn':
            print('q')
            self.polQ = True
            self.polS = False
        elif pol == 'sarsa':
            print('s')
            self.polQ = False
            self.polS = True
        else: print('Not a valid control policy')

        # Set log flag for training
        if log:
            self.log = True
        else:
            self.log = False

        # Set discretisation factor and verbose flag
        self.dis = dis
        self.verbose = verboseFlag

    # Initialize environment and Q-table
    def init_env(self, initialisation, cont_os, cont_as, environment,
            resolution):

        # Create numpy array to store rewards for use in statistical tracking
        self.timestep_reward_res = np.zeros(resolution)
        self.resolution = resolution
        self.res = 0

        # Set variables to be used to flag specific behaviour in the learning
        self.environment = environment

        # Set pendulum envirnonent specific flag to avoid index errors
        if environment == 'Pendulum-v0':
            self.pendulum = True
        else:
            self.pendulum = False

        # Set bool toggles for continuous action and observation spaces
        self.cont_os = cont_os
        self.cont_as = cont_as

        # Initialize environment
        self.env = gym.make(environment).env
        self.env.reset()
        
        # If observation space is continuous do calculations to create
        #   corresponding bins for use with Q table
        if cont_os:
            self.os_high = self.env.observation_space.high
            self.os_low = self.env.observation_space.low

            # Set bounds for infinite observation spaces in 'CartPole-v1'
            if environment == 'CartPole-v1':
                self.os_high[1], self.os_high[3] = 5, 5
                self.os_low[1], self.os_low[3] = -5, -5

            # Discretize the observation space
            self.discrete_os_size = [self.dis] * len(self.os_high)
            self.discrete_os_win_size = (self.os_high\
                    - self.os_low) / self.discrete_os_size
        # Use number of observations if no discretization is required
        else: self.discrete_os_size = [self.env.observation_space.n]
        
        # The same for action space
        if cont_as:
            self.dis_centre = self.dis / 2

            self.as_high = self.env.action_space.high
            self.as_low = self.env.action_space.low

            self.discrete_as_size = [self.dis] * len(self.as_high)
            self.discrete_as_win_size = (self.as_high\
                    - self.as_low) / self.discrete_as_size
            self.action_n = self.dis
        else:
            self.discrete_as_size = [self.env.action_space.n]
            self.action_n = self.env.action_space.n
        
        # Initialise q-table with supplied type
        if initialisation == 'uniform':
            self.Q = np.random.uniform(low = -2, high = 0, size=(
                self.discrete_os_size + self.discrete_as_size))
        elif initialisation == 'random':
            self.Q = np.random.uniform((self.discrete_os_size,
                self.discrete_as_size))
        elif initialisation == 'zeros':
            self.Q = np.zeros((self.discrete_os_size,
                self.discrete_as_size))
        elif initialisation == 'ones':
            self.Q = np.ones((self.discrete_os_size,
                self.discrete_as_size))
        else: print('initialisation method not valid')

        return

    # Get the discrete state from the state supplied by the environment (modify
    #   values if the pendulum environment flag is set to avoid indexing errors
    #   of discretized states in the q table)
    def get_discrete_state(self, state):
        '''
        if not self.pendulum:
            discrete_state = ((state - self.os_low) / self.discrete_os_win_size)
        else:
        '''
        discrete_state = ((state - self.os_low) /\
                self.discrete_os_win_size) - 0.5
        
        return tuple(discrete_state.astype(np.int))

    # Get the continuous action from the discrete action supplied by e-greedy
    def get_continuous_action(self, discrete_action):
        
        continuous_action = (discrete_action - self.dis_centre) *\
                self.discrete_as_win_size
        
        return continuous_action

    # e-Greedy algorithm for action selection from the q table by state with
    #   flag to force greedy method for testing. Takes input for decaying
    #   epsilon value. Gets the continuous action if needed
    def e_greedy(self, epsilon, s, greedy=False):
        
        if greedy or np.random.rand() > epsilon: d_a = np.argmax(self.Q[s])
        else: d_a = np.random.randint(0, self.action_n)

        if self.cont_as: a = self.get_continuous_action(d_a)
        else: a = d_a

        return a, d_a

    # Perform training on the Q table for the given environment, called once per
    #   episode taking variables to control the training process
    def lrn(self, epsilon, episode, penalty, exponent, length,
            alpha, gamma, maxSteps, renderFlag):

        # Set vars used for checks in training
        steps = 0
        maxS = False
        done = False
        render = False
        
        # Reset environment for new episode and get initial discretized state
        if self.cont_os: d_s = self.get_discrete_state(self.env.reset())
        else:
            s = self.env.reset()
            d_s = s

        if self.log:
            modeL = True
            history_o = np.zeros((length, len(d_s)))
            history_a = np.zeros(length)
        else:
            modeL = False

        # Report episode and epsilon and set the episode to be rendered
        #   if the resolution is reached
        if episode % self.resolution == 0 and episode != 0:
            if self.verbose: print(episode, epsilon)
            if renderFlag: render = True

        # Create values for recording rewards and task completion
        total_reward = 0
        
        # Get initial action using e-Greedy method for SARSA policy
        if self.polS: a, d_a = self.e_greedy(epsilon, d_s)

        # Loop the task until task is completed or max steps are reached
        while not done:
            if render: self.env.render()
            
            # Get initial action using e-Greedy method for Q-Lrn policy
            if self.polQ: a, d_a = self.e_greedy(epsilon, d_s)

            # Get next state from the chosen action and record reward
            s_, reward, done, info = self.env.step(a)
            total_reward += reward

            # Discretise state if observation space is continuous
            if self.cont_os: d_s_ = self.get_discrete_state(s_)
            else: d_s_ = s_

            # If max steps have been exceeded set episode to complete
            if maxS: done = True

            # If the task is not completed update Q by max future Q-values
            if not done:
                max_future_q = np.max(self.Q[d_s_])

                # Select next action based on next discretized state using
                #   e-Greedy method for SARSA policy
                if self.polS:
                    a_, d_a_ = self.e_greedy(epsilon, d_s)
                
                # Perform Bellman equation to update Q-values
                self.Q[d_s + (d_a, )] = self.Q[d_s + (d_a,)]\
                        + alpha * (reward + gamma *\
                        max_future_q - self.Q[d_s + (d_a,)])
            
            # If task is completed set Q-value to zero so no penalty is applied
            if done:
                # If max steps have been reached do not apply penalty
                if maxS:
                    pass
                # If log penalties are used apply penalty respective to the
                #   exponent of the relative position 1 to 10
                elif modeL and steps > length and epsilon == 0:
                    for i in range(length):
                        self.Q[tuple(history_o[i].astype(np.int)) +\
                                (int(history_a[i]), )]\
                                += penalty * math.exp(exponent) ** i
                # Otherwise apply normal penalty to the current q value 
                else: self.Q[d_s + (d_a, )] = penalty
               
                # Iterate the resolution counter and record rewards
                if self.res == self.resolution: self.res = 0
                else:
                    self.timestep_reward_res[self.res] = total_reward
                    self.res += 1

                # Print resolution results if verbose flag is set
                if self.verbose and episode % self.resolution == 0\
                        and episode != 0:
                    print(np.average(self.timestep_reward_res),
                            np.min(self.timestep_reward_res),
                            np.max(self.timestep_reward_res))
                
                # Close the render of the episode if rendered
                if render: self.env.close()

            # Record states and actions into rolling numpy array for applying
            #   log panalties
            if modeL and epsilon == 0:
                history_o = np.roll(history_o, 1)
                history_a = np.roll(history_a, 1)
                history_o[0] = d_s
                history_a[0] = d_a

            # Set next state to current state (Q-Learning) control policy
            if self.polQ: d_s = d_s_

            # Set next state and action to current state and action (SARSA)
            if self.polS: d_s, d_a, a = d_s_, d_a_, a_
            
            # If max steps are reached complete episode and set max step flag
            if steps == maxSteps: maxS = True
            steps += 1
        
        return

    # Test function to test the Q-table
    def test_qtable(self, n_tests, maxSteps, renderFlag):
        # Create array to store total rewards and steps for each test
        rewards = np.zeros(n_tests)

        # Iterate through each test
        for test in range(n_tests):
            # Reset the environment and get the initial state
            d_s = self.get_discrete_state(self.env.reset())
            
            # Set step and reward counters to zero and done flag
            steps = 0
            total_reward = 0
            done = False
            
            # Set greedy flag sets greedy method to be used by e-Greedy
            epsilon = 0
            greedy = True
            
            # Loop until test conditions are met iterating the steps counter
            while not done:
                if renderFlag: self.env.render()
                steps += 1
                
                # Get action by e-greedy method
                a, d_a = self.e_greedy(epsilon, d_s, greedy)

                # Get state by applying the action to the environment and
                #   add reward
                s, reward, done, info = self.env.step(a)
                total_reward += reward
                d_s = self.get_discrete_state(s)

                if steps == maxSteps: done = True
            
            # Record total rewards and steps
            rewards[test] = total_reward

        if renderFlag: self.env.close()

        # Get averages of the steps and rewards and failure percentage for tests
        avg_rwd = np.average(rewards)
        std_rwd = np.std(rewards)

        return avg_rwd, std_rwd


