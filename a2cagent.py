import melee
import numpy as np
import random
import gym
import pylab
from PIL import Image
from collections import deque
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Input, Add, Dropout, Conv2D, Concatenate, Flatten, MaxPooling2D
from keras.optimizers import Adam
from keras.callbacks import TensorBoard

import time

stage_sprite = np.array(Image.open("sprites/final_destination.png")).reshape((328,500,1))
character_sprite = np.array(Image.open("sprites/character.png")).reshape((14,8,1))

"""
Helpful wrapper class for actions taken by the A2C agent
    Each object represents a single action (button presses)
    Actions are abstracted into being able to press ONE button of:
        A, B, Y, L, None
    Also, the control stick's x and y coordinates can be in one of 5 positions
        0, .25, .50, .75, 1.0
"""
class Action():
    # The args to this the indices of the chosen actions (np.argmax of the model's outputs)
    def __init__(self, button_output, stick_x_output, stick_y_output):
        self.x_index = stick_x_output
        self.y_index = stick_y_output
        self.button_index = button_output

    # Pretty string version of the action for debugging
    def __str__(self):
        button = None
        if self.button_index == 0:
            button = "A"
        elif self.button_index == 1:
            button = "B"
        elif self.button_index == 2:
            button = "Y"
        elif self.button_index == 2:
            button = "L"
        else:
            button = ""

        x = None
        if self.x_index == 0:
            x = 0
        elif self.x_index == 1:
            x = 0.25
        elif self.x_index == 2:
            x = 0.5
        elif self.x_index == 3:
            x = 0.75
        elif self.x_index == 4:
            x = 1.0

        y = None
        if self.y_index == 0:
            y = 0
        elif self.y_index == 1:
            y = 0.25
        elif self.y_index == 2:
            y = 0.5
        elif self.y_index == 3:
            y = 0.75
        elif self.y_index == 4:
            y = 1.0

        return str(x) + ", " + str(y) + " " + button

    # Turn this action into a randomized action
    def randomize(self, stick_categories, button_count):
        self.x_index = random.randint(0, stick_categories-1)
        self.y_index = random.randint(0, stick_categories-1)
        self.button_index = random.randint(0, button_count-1)

    # Get a tuple of button press values that you can stick right into libmelee's simple_press
    def getpresses(self):
        button = None
        if self.button_index == 0:
            button = melee.enums.Button.BUTTON_A
        elif self.button_index == 1:
            button = melee.enums.Button.BUTTON_B
        elif self.button_index == 2:
            button = melee.enums.Button.BUTTON_Y
        elif self.button_index == 2:
            button = melee.enums.Button.BUTTON_L
        else:
            button = None

        x = None
        if self.x_index == 0:
            x = 0
        elif self.x_index == 1:
            x = 0.25
        elif self.x_index == 2:
            x = 0.5
        elif self.x_index == 3:
            x = 0.75
        elif self.x_index == 4:
            x = 1.0

        y = None
        if self.y_index == 0:
            y = 0
        elif self.y_index == 1:
            y = 0.25
        elif self.y_index == 2:
            y = 0.5
        elif self.y_index == 3:
            y = 0.75
        elif self.y_index == 4:
            y = 1.0

        return x, y, button

"""
Helpful wrapper class for observations taken
    Represents a snapshot of the relevant bits of the gamestate
"""
class Observation():
    # gamestate_array = The serialized list version of a libmelee gamestate
    def __init__(self, gamestate_array):
        # TODO: this assumes FD for the time-being

        # Each pixel is about 1 unit
        self.height = 328
        self.width = 500
        self.gamestate_array = gamestate_array

        self.screen = np.zeros((self.height, self.width, 1), dtype=np.uint8)

        global stage_sprite
        global character_sprite

        # Next, draw on the stage
        # stage = np.zeros((self.height, self.width, 1), dtype=np.uint8)
        # for y, column in enumerate(stage):
        #     for x, row in enumerate(column):
        #         # Upper lip
        #         if (168 < y < 188) and (165 < x < 335):
        #             stage[y][x] = 255
        #         # Lower area
        #         if (138 < y < 169) and (185 < x < 315):
        #             stage[y][x] = 255
        #
        # stage = np.flip(stage, 0)
        #
        # # Next, draw on the characters
        smashbot_x = gamestate_array[2] + 246 # x
        smashbot_y = self.height - (gamestate_array[3] + 188 + 4) # y
        opponent_x = gamestate_array[16+2] + 246 # x
        opponent_y = self.height - (gamestate_array[16+3] + 188 + 4) # y
        #
        # n = [3]
        # character_sprite = [ [n,n,n,n,n,[0],[0],[0]],
        #                     [n,n,n,n,n,[0],[0],[0]],
        #                     [[0],n,n,n,n,n,[0],[0]],
        #                     [[0],n,n,n,n,n,[0],[0]],
        #                     [[0],[0],n,n,n,n,n,[0]],
        #                     [[0],[0],n,n,n,n,n,[0]],
        #                     [[0],[0],[0],n,n,n,n,n],
        #                     [[0],[0],[0],n,n,n,n,n],
        #                     [[0],[0],n,n,n,n,n,[0]],
        #                     [[0],[0],n,n,n,n,n,[0]],
        #                     [[0],n,n,n,n,n,[0],[0]],
        #                     [[0],n,n,n,n,n,[0],[0]],
        #                     [n,n,n,n,n,[0],[0],[0]],
        #                     [n,n,n,n,n,[0],[0],[0]]]
        smashbot_sprite = np.array(character_sprite, dtype=np.uint8)
        opponent_sprite = np.array(character_sprite, dtype=np.uint8)
        if not bool(gamestate_array[6]): # facing
            smashbot_sprite = np.flip(character_sprite, 1)
        if not bool(gamestate_array[13+6]): # facing
            opponent_sprite = np.flip(character_sprite, 1)

        # Draw on the sprites
        x = int(smashbot_x)
        y = int(smashbot_y)
        self.screen[y:y+smashbot_sprite.shape[0], x:x+smashbot_sprite.shape[1]] = smashbot_sprite
        x = int(opponent_x)
        y = int(opponent_y)
        self.screen[y:y+opponent_sprite.shape[0], x:x+opponent_sprite.shape[1]] = opponent_sprite

        # Add them all togethers
        self.screen = np.sum([self.screen, stage_sprite], axis=0, dtype=np.uint8)
        # img = Image.fromarray(self.screen)
        # img.show()

    def getfeatures(self):
        """
        Get the agent's features from this observation
            Returns a tuple of Screen, Action, Misc
        """

        # TODO some feature engineering would help here
        #   to group together similar action
        actions = np.zeros((1, 2, 0x178))
        smashbot_action = self.gamestate_array[7] # action
        opponent_action = self.gamestate_array[16+7] # action
        if smashbot_action == 0xfff:
            smashbot_action = 0x177
        if opponent_action == 0xfff:
            opponent_action = 0x177
        actions[0][0][smashbot_action] = 1
        actions[0][1][opponent_action] = 1

        features = np.zeros((1, 8))
        # features[0][0] = self.gamestate_array[2] # x
        # features[0][1] = self.gamestate_array[3] # y
        # features[0][2] = self.gamestate_array[6] # facing
        features[0][0] = self.gamestate_array[4] # percent
        features[0][1] = self.gamestate_array[5] # stock
        features[0][2] = self.gamestate_array[8] # action_frame
        features[0][3] = self.gamestate_array[13] # jumps_left

        # features[0][7] = self.gamestate_array[16+2] # x
        # features[0][8] = self.gamestate_array[16+3] # y
        # features[0][9] = self.gamestate_array[16+6] # facing
        features[0][4] = self.gamestate_array[16+4] # percent
        features[0][5] = self.gamestate_array[16+5] # stock
        features[0][6] = self.gamestate_array[16+8] # action_frame
        features[0][7] = self.gamestate_array[16+13] # jumps_left

        screen = np.zeros((1, self.height, self.width, 1))
        screen[0] = self.screen
        return screen, actions, features
"""
A2C (Advantage Actor-Critic) agent
"""
class A2CAgent():
    def __init__(self, dolphin, gamestate, smashbot_port, opponent_port, tensorboard=True):
        self.gamestate = gamestate
        self.controller = melee.controller.Controller(port=smashbot_port, dolphin=dolphin)
        self.smashbot_state = self.gamestate.player[smashbot_port]
        self.opponent_state = self.gamestate.player[opponent_port]
        self.framedata = melee.framedata.FrameData()
        self.logger = dolphin.logger
        self.tensorboard = tensorboard

        self.batchsize = 1000
        self.temperature = 0.2

        #TODO change action to a one-hot encoded category eventually
        self.state_space = 18
        self.button_action_space = 5
        self.stick_action_space = 5
        self.screen_height = 328
        self.screen_width = 500
        self.action_depth = 0x178
        self.misc_features_count = 8

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
        screen_input = Input(shape=(self.screen_height, self.screen_width, 1), name='actor_screen_input')
        actions_input = Input(shape=(2,self.action_depth), name='actor_actions_input')
        misc_input = Input(shape=(self.misc_features_count,), name='actor_misc_input')
        #   First layer
        conv_layer = Conv2D(16, kernel_size=(4, 4), activation='relu', name='actor_conv_layer_1')(screen_input)
        pooling_1 = MaxPooling2D(pool_size=(8, 8))(conv_layer)
        conv_layer = Conv2D(8, kernel_size=(4, 4), activation='relu', name='actor_conv_layer_2')(pooling_1)
        pooling_2 = MaxPooling2D(pool_size=(6, 6))(conv_layer)
        conv_flattened = Flatten()(pooling_2)

        actions_hidden_1 = Dense(24, activation='relu', name='actor_actions_dense')(actions_input)
        actions_flattened = Flatten()(actions_hidden_1)
        misc_hidden_1 = Dense(24, activation='relu', name='actor_misc_dense')(misc_input)
        #   Merge the inputs
        x = Concatenate(name='actor_concat_layer')([conv_flattened, actions_flattened, misc_hidden_1])
        #   Hidden layers
        x = Dense(24, activation='relu', name='actor_hidden_layer_2')(x)
        x = Dropout(self.dropout_rate)(x)
        #x = Dense(32, activation='relu', name='actor_hidden_layer_3')(x)
        button_output = Dense(self.button_action_space, activation='softmax', name='button_output')(x)
        stick_x_output = Dense(self.stick_action_space, activation='softmax', name='stick_x_output')(x)
        stick_y_output = Dense(self.stick_action_space, activation='softmax', name='stick_y_output')(x)
        self.actor_model = Model(inputs=[screen_input, actions_input, misc_input], outputs=[button_output, stick_x_output, stick_y_output])
        self.actor_model.compile(optimizer=Adam(lr=self.actor_learning_rate), loss='mse')
        print(self.actor_model.summary())

        # Critic model
        screen_input_critic = Input(shape=(self.screen_height, self.screen_width, 1), name='critic_screen_input')
        actions_input_critic = Input(shape=(2,self.action_depth), name='critic_actions_input')
        misc_input_critic = Input(shape=(self.misc_features_count,), name='critic_misc_input')
        #   Conv layer
        conv_layer = Conv2D(16, kernel_size=(4, 4), activation='relu', name='critic_conv_layer_1')(screen_input_critic)
        pooling_1 = MaxPooling2D(pool_size=(8, 8))(conv_layer)
        conv_layer = Conv2D(8, kernel_size=(4, 4), activation='relu', name='critic_conv_layer_2')(pooling_1)
        pooling_2 = MaxPooling2D(pool_size=(6, 6))(conv_layer)
        conv_flattened = Flatten()(pooling_2)
        actions_hidden_1 = Dense(24, activation='relu', name='critic_actions_dense')(actions_input)
        actions_flattened = Flatten()(actions_input_critic)
        misc_hidden_1 = Dense(24, activation='relu', name='critic_misc_dense')(misc_input_critic)
        #   Merge the inputs
        x = Concatenate(name='critic_concat_layer')([conv_flattened, actions_flattened, misc_hidden_1])
        #   Hidden layers
        x = Dense(24, activation='relu', name='critic_hidden_layer_2')(x)
        x = Dropout(self.dropout_rate)(x)
        #x = Dense(32, activation='relu', name='critic_hidden_layer_3')(x)
        critic_output = Dense(1, activation='linear', name='critic_output')(x)
        self.critic_model = Model(inputs=[screen_input_critic, actions_input_critic, misc_input_critic], outputs=critic_output)
        self.critic_model.compile(optimizer=Adam(lr=self.critic_learning_rate), loss='mse')
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

        screen_inputs = np.zeros((self.batchsize, self.screen_height, self.screen_width, 1))
        action_inputs = np.zeros((self.batchsize, 2, self.action_depth))
        misc_inputs = np.zeros((self.batchsize, self.misc_features_count))

        critic_outputs = np.zeros((self.batchsize, 1))
        button_outputs = np.zeros((self.batchsize, self.button_action_space))
        stick_x_outputs = np.zeros((self.batchsize, self.stick_action_space))
        stick_y_outputs = np.zeros((self.batchsize, self.stick_action_space))

        for i, (state, action, reward, newstate, done) in enumerate(minibatch):
            # Get a ditribution of actions that we would normally take
            state_feature1, state_feature2, state_feature3 = state.getfeatures()
            newstate_feature1, newstate_feature2, newstate_feature3 = newstate.getfeatures()

            button_target, stick_x_target, stick_y_target = self.actor_model.predict([state_feature1, state_feature2, state_feature3])
            button_target = button_target[0]
            stick_x_target = stick_x_target[0]
            stick_y_target = stick_y_target[0]

            current_value = self.critic_model.predict([state_feature1, state_feature2, state_feature3])
            current_value = current_value[0][0]

            future_value = self.critic_model.predict([newstate_feature1, newstate_feature2, newstate_feature3])
            future_value = future_value[0][0]

            value = 0

            # Calculate value
            if not done:
                value = reward + (self.discount * future_value)
                button_target[action.button_index] = reward + (self.discount * future_value) - current_value
                stick_x_target[action.x_index] = reward + (self.discount * future_value) - current_value
                stick_y_target[action.y_index] = reward + (self.discount * future_value) - current_value
            else:
                value = reward
                button_target[action.button_index] = reward - current_value
                stick_x_target[action.x_index] = reward - current_value
                stick_y_target[action.y_index] = reward - current_value

            # print("\n")
            # print("\treward", reward)
            # print("\tvalue", value)
            # print("\tadvantage", advantage)
            # print("\tfuture_value", future_value)
            # print("\tcurrent_value", current_value)
            # if done:
            #     print("got", reward)

            # Put the results into a batch for training on
            screen_inputs[i] = state_feature1[0]
            action_inputs[i] = state_feature2[0]
            misc_inputs[i] = state_feature3[0]

            critic_outputs[i] = value
            button_outputs[i] = button_target
            stick_x_outputs[i] = stick_x_target
            stick_y_outputs[i] = stick_y_target

        callbacks = []
        if self.tensorboard:
            callbacks.append(TensorBoard(log_dir='./Logs/tboard/', histogram_freq=0, write_graph=True, write_images=True))

        self.critic_model.fit([screen_inputs, action_inputs, misc_inputs], critic_outputs, epochs=1, callbacks=callbacks, verbose=1)
        self.actor_model.fit([screen_inputs, action_inputs, misc_inputs], [button_outputs,  stick_x_outputs, stick_y_outputs], epochs=1, callbacks=callbacks, verbose=1)

    def batchexperience(self, state, action, reward, newstate, done):
        experience = [state, action, reward, newstate, done]
        self.experiences.append(experience)

    def act(self):
        """
        Ask the next action from the agent
        """
        # Get actions from the actor model
        npstate = Observation(self.gamestate.tolist())
        screen, action, misc = npstate.getfeatures()
        button_output, stick_x_output, stick_y_output = self.actor_model.predict([screen, action, misc])

        action = Action(np.argmax(button_output),
                        np.argmax(stick_x_output),
                        np.argmax(stick_y_output))

        self.explorationchance *= self.exploredelta
        self.explorationchance = max(self.exploremin, self.explorationchance)

        # Randomly force exploration some percent of the time
        if random.random() < self.explorationchance:
            action.randomize(self.stick_action_space, self.button_action_space)

        # Press the buttons on the controller
        x, y, button = action.getpresses()
        self.controller.simple_press(x, y, button)

        # Return the result
        return action

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
