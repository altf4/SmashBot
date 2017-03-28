import numpy as np
import random
from collections import deque

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

"""An 'experience' consists of a grouping of the previous state we WERE in,
one frame ago, what action we took there, what new state we got to from that
action, and what reward we received in the transition"""
class Experience():
    def __init__(self, state, action, prev_state, reward):
        self.state = state
        self.prev_state = prev_state
        self.action = action
        self.reward = reward

class Agent():
    def __init__(self, gamestate_dim, action_dim):
        # Build the model
        self.model = Sequential()
        self.model.add(Dense(output_dim=128, input_dim=gamestate_dim))
        self.model.add(Activation('relu'))
        self.model.add(Dense(128))
        self.model.add(Activation('relu'))
        self.model.add(Dense(128))
        self.model.add(Activation('relu'))
        self.model.add(Dense(action_dim))
        self.model.add(Activation('softmax'))

        #"Compile" the model
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.epsilon = 0.00833
        self.epsilon_decay = .9999
        self.epsilon_min = 0.00833
        self.gamma = .99
        self.action_dim = action_dim
        self.gamestate_dim = gamestate_dim
        #180 experiences means 3 seconds worth of memory
        self.memory_size = 180
        self.batchsize = 100

        self.memory = deque(maxlen=self.memory_size)

    #Given the current state, choose an action and return it
    #Stochastic! (ie: we choose an action at random, using each state as a probability)
    def act(self, state):
        #Will we do a random action?
        action = []
        if np.random.rand() > self.epsilon:
            #No idea why the reshape is necessary here... but it is
            action = self.model.predict_on_batch(np.array(state).reshape((1, self.gamestate_dim)))
            #Roll a number between 0 and 1
            roll = np.random.rand()
            #Find where it "lands" in the distribution
            index = 0
            #It's a nested array that it returns, so unnest it
            action = action[0]
            while roll > 0:
                if roll < action[index]:
                    return index
                roll -= action[index]
                index += 1
        else:
            action = np.random.randint(self.action_dim)

        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon, self.epsilon_min)
        return action

    def train(self, state, action, prev_state, reward):
        new_experience = Experience(state, action, prev_state, reward)
        self.memory.append(new_experience)
        #Only train if we have the minimum amount of experiences saved
        if len(self.memory) < self.batchsize:
            return

        #Our batched training arrays (arrays of arrays)
        training_in = []
        training_out = []

        #Do a randomized sample here in order to avoid 'catastrophic forgetting'
        minibatch = random.sample(self.memory, self.batchsize)

        for index, experience in enumerate(minibatch):
            #Make a prediction for our state, taking the highest probability action
            #IE: Not stochasitc
            maxQ = np.max(self.model.predict_on_batch(
                np.array(experience.state).reshape((1, self.gamestate_dim))))
            #make a one-hot array of our output choices, with the "hot" option
            #   equal to our discounted reward
            reward_array = np.zeros(self.action_dim)
            #If this is the last iteration, just use the reward
            if index == len(self.memory) - 1:
                update = experience.reward
            else:
                update = (experience.reward + (self.gamma * maxQ))
            #target output
            reward_array[experience.action] = update
            training_in.append(experience.prev_state)
            training_out.append(np.array(reward_array))

        #I think it's faster to train in batches like this, so let's do that
        self.model.fit(np.array(training_in), np.array(training_out),
            batch_size=len(self.memory), nb_epoch=1, verbose=0)

    def save(self, path):
        self.model.save_weights(path)

    def load(self, path):
        self.model.load_weights(path)
