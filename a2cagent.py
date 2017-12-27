import melee
import numpy as np
import random
import gym
import pylab
from collections import deque
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Input, Add, Dropout
from keras.optimizers import Adam

"""
A2C (Advantage Actor-Critic) agent
"""
class A2CAgent():
    def __init__(self, dolphin, gamestate, smashbot_port, opponent_port):

        self.gamestate = gamestate
        self.controller = melee.controller.Controller(port=smashbot_port, dolphin=dolphin)
        self.smashbot_state = self.gamestate.player[smashbot_port]
        self.opponent_state = self.gamestate.player[opponent_port]
        self.framedata = melee.framedata.FrameData()
        self.logger = dolphin.logger

        self.batchsize = 10000
        self.temperature = 0.2

        #TODO change action to a one-hot encoded category eventually
        self.state_space = 18
        self.button_action_space = 4
        self.stick_action_space = 5

        # This is a queue of experience tuples
        self.experiences = deque(maxlen=self.batchsize)
        self.min_batches = 500

        # Usually called epsilon in acedemic circles
        self.discount = 0.99

        self.explorationchance = 0.95
        self.exploredelta = 0.999
        self.exploremin = 0.001

        self.actor_learning_rate = 0.001
        self.critic_learning_rate = 0.015

        self.dropout_rate = 0.1

        # Actor model
        input_layer = Input(shape=(self.state_space,), name='actor_input_layer')
        x = Dense(32, activation='relu', name='actor_hidden_layer_1')(input_layer)
        x = Dense(32, activation='relu', name='actor_hidden_layer_2')(x)
        x = Dropout(self.dropout_rate)(x)
        x = Dense(32, activation='relu', name='actor_hidden_layer_3')(x)
        button_output = Dense(self.button_action_space, activation='softmax', name='button_output')(x)
        stick_x_output = Dense(self.stick_action_space, activation='softmax', name='stick_x_output')(x)
        stick_y_output = Dense(self.stick_action_space, activation='softmax', name='stick_y_output')(x)
        self.actor_model = Model(inputs=input_layer, outputs=[button_output, stick_x_output, stick_y_output])
        self.actor_model.compile(optimizer=Adam(lr=self.actor_learning_rate), loss='mse')

        # Critic model
        input_layer_state = Input(shape=(self.state_space,), name='critic_input_layer_state')
        x = Dense(32, activation='relu', name='critic_hidden_layer_1')(input_layer_state)
        x = Dense(32, activation='relu', name='critic_hidden_layer_2')(x)
        x = Dropout(self.dropout_rate)(x)
        x = Dense(32, activation='relu', name='critic_hidden_layer_3')(x)
        critic_output = Dense(1, activation='linear', name='critic_output')(x)
        self.critic_model = Model(inputs=input_layer_state, outputs=critic_output)
        self.critic_model.compile(optimizer=Adam(lr=self.critic_learning_rate), loss='mse')

        print(self.actor_model.summary())
        print(self.critic_model.summary())


    def train(self):
        """
        Train the deep q-learning network.
        """
        # Don't train if we don't have enough data yet
        if len(self.experiences) < self.min_batches:
            return

        # Randomly sample from the memories to help prevent overfitting
        minibatch = random.sample(self.experiences, max(1, int(len(self.experiences) * 0.65)))

        state_inputs = np.zeros((self.batchsize, self.state_space))
        critic_outputs = np.zeros((self.batchsize, 1))

        button_outputs = np.zeros((self.batchsize, self.button_action_space))
        stick_x_outputs = np.zeros((self.batchsize, self.stick_action_space))
        stick_y_outputs = np.zeros((self.batchsize, self.stick_action_space))

        for i, (state, action, reward, newstate, done) in enumerate(minibatch):
            # Get a ditribution of actions that we would normally take
            button_target, stick_x_target, stick_y_target = self.actor_model.predict(state)
            button_target = button_target[0]
            stick_x_target = stick_x_target[0]
            stick_y_target = stick_y_target[0]

            current_value = self.critic_model.predict(state)
            current_value = current_value[0][0]

            future_value = self.critic_model.predict(newstate)
            future_value = future_value[0][0]

            value = 0

            # Calculate value
            if not done:
                value = reward + (self.discount * future_value)
                button_target[action[0]] = reward + (self.discount * future_value) - current_value
                stick_x_target[action[1]] = reward + (self.discount * future_value) - current_value
                stick_y_target[action[2]] = reward + (self.discount * future_value) - current_value
            else:
                value = reward
                button_target[action[0]] = reward - current_value
                stick_x_target[action[1]] = reward - current_value
                stick_y_target[action[2]] = reward - current_value

            # print("\n")
            # print("\treward", reward)
            # print("\tvalue", value)
            # print("\tadvantage", advantage)
            # print("\tfuture_value", future_value)
            # print("\tcurrent_value", current_value)
            # if done:
            #     print("got", reward)

            # Put the results into a batch for training on
            state_inputs[i] = state
            critic_outputs[i] = value
            button_outputs[i] = button_target
            stick_x_outputs[i] = stick_x_target
            stick_y_outputs[i] = stick_y_target

        self.critic_model.fit(state_inputs, critic_outputs, epochs=1, verbose=0)
        self.actor_model.fit(state_inputs, [button_outputs, stick_x_outputs, stick_y_outputs], epochs=1, verbose=0)

    def batchexperience(self, state, action, reward, newstate, done):
        state = self.statetoarray(state)
        newstate = self.statetoarray(newstate)
        experience = [state, action, reward, newstate, done]
        self.experiences.append(experience)

    def statetoarray(self, state):
        """
        Convert a libmelee gamestate list into a usable numpy array with the features we want
        """
        converted = np.zeros(self.state_space)
        converted[0] = state[2] # x
        converted[1] = state[3] # y
        converted[2] = state[4] # percent
        converted[3] = state[5] # stock
        converted[4] = state[6] # facing
        converted[5] = state[7] # action
        converted[6] = state[8] # action_frame
        converted[7] = state[13] # jumps_left
        converted[8] = state[14] # on_ground

        converted[9] = state[13+5] # x
        converted[10] = state[13+3] # y
        converted[11] = state[13+4] # percent
        converted[12] = state[13+5] # stock
        converted[13] = state[13+6] # facing
        converted[14] = state[13+7] # action
        converted[15] = state[13+8] # action_frame
        converted[16] = state[13+13] # jumps_left
        converted[17] = state[13+14] # on_ground

        return converted.reshape(1, self.state_space)

    def act(self):
        """
        Ask the next action from the agent
        """
        self.explorationchance *= self.exploredelta
        self.explorationchance = max(self.exploremin, self.explorationchance)

        #TODO Randomly force exploration some percent of the time
        # if random.random() < self.explorationchance:
        #     return env.action_space.sample()

        # Get actions from the actor model
        npstate = self.statetoarray(self.gamestate.tolist())
        button_output, stick_x_output, stick_y_output = self.actor_model.predict(npstate)

        button_index = np.argmax(button_output)
        button = None
        if button_index == 0:
            button = melee.enums.Button.BUTTON_A
        elif button_index == 1:
            button = melee.enums.Button.BUTTON_B
        elif button_index == 2:
            button = melee.enums.Button.BUTTON_Y
        else:
            button = melee.enums.Button.BUTTON_L

        x_index = np.argmax(stick_x_output)
        x = None
        if x_index == 0:
            x = 0
        elif x_index == 1:
            x = 0.25
        elif x_index == 2:
            x = 0.5
        elif x_index == 3:
            x = 0.75
        elif x_index == 4:
            x = 1.0

        y_index = np.argmax(stick_y_output)
        y = None
        if y_index == 0:
            y = 0
        elif y_index == 1:
            y = 0.25
        elif y_index == 2:
            y = 0.5
        elif y_index == 3:
            y = 0.75
        elif y_index == 4:
            y = 1.0

        # Press the buttons on the controller
        self.controller.simple_press(x, y, button)
        # Return the result
        return button_index, x_index, y_index

    def getstate(self):
        """
        From the current gamestate, get usable numpy arrays that represent it
        """
        state = np.zeros(8)
        state[0] = self.smashbot_state.x
        state[1] = self.smashbot_state.y
        state[2] = self.smashbot_state.percent
        state[3] = self.smashbot_state.stock
        state[4] = int(self.smashbot_state.facing)
        state[5] = int(self.smashbot_state.on_ground)
        state[6] = self.smashbot_state.jumps_left
        state[7] = self.smashbot_state.action_frame

        state2 = np.zeros(8)
        state2[0] = self.opponent_state.x
        state2[1] = self.opponent_state.y
        state2[2] = self.opponent_state.percent
        state2[3] = self.opponent_state.stock
        state2[4] = int(self.opponent_state.facing)
        state2[5] = int(self.opponent_state.on_ground)
        state2[6] = self.opponent_state.jumps_left
        state2[7] = self.opponent_state.action_frame

        return state, state2

    # Gets the current score
    def getscore(self):
        p1score = self.smashbot_state.stock - ((self.smashbot_state.percent)/999)**(1./3.)
        p2score = self.opponent_state.stock - ((self.opponent_state.percent)/999)**(1./3.)
        return p1score - p2score

    def save(self):
        self.actor_model.save('Logs/actor_model.h5')
        self.critic_model.save('Logs/critic_model.h5')

    def load(self):
        self.actor_model.load('Logs/actor_model.h5')
        self.critic_model.load('Logs/critic_model.h5')
