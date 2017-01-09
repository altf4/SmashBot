import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np

#clip adapted from https://gist.github.com/jkarnows/522c2d6000e519482b6deb825d17b34b
class Agent(object):

    def __init__(self, gamestate_dim, action_dim, network_layers):
        self._dim_state = gamestate_dim
        self._dim_action = action_dim
        self._batch_size = 200
        self._gamma = 0.90

        self._prev_state = None
        self._prev_action = None
        self._prev_reward = 0

        prev_states = tf.placeholder(tf.float32, [None, self._dim_state])
        net = slim.stack(prev_states, slim.fully_connected, network_layers,
            activation_fn=tf.nn.relu, scope='fc')
        prev_action_values = slim.fully_connected(net, self._dim_action,
            activation_fn=None, scope='qvalues')
        prev_action_masks = tf.placeholder(tf.float32, [None, self._dim_action])
        prev_values = tf.reduce_sum(tf.mul(prev_action_values, prev_action_masks), axis=1)

        prev_rewards = tf.placeholder(tf.float32, [None, ])
        next_states = tf.placeholder(tf.float32, [None, self._dim_state])
        net = slim.stack(next_states, slim.fully_connected,
            network_layers, activation_fn=tf.nn.relu, scope='fc', reuse=True)
        next_action_values = slim.fully_connected(net, self._dim_action,
            activation_fn=None, scope='qvalues', reuse=True)
        next_values = prev_rewards + self._gamma * tf.reduce_max(next_action_values,
            axis=1)

        loss = tf.reduce_mean(tf.square(prev_values - next_values))
        training = tf.train.AdamOptimizer(1e-4).minimize(loss)

        self._tf_action_value_predict = prev_action_values
        self._tf_prev_states = prev_states
        self._tf_prev_action_masks = prev_action_masks
        self._tf_prev_rewards = prev_rewards
        self._tf_next_states = next_states
        self._tf_training = training
        self._tf_loss = loss
        self._tf_session = tf.InteractiveSession()

        self._tf_session.run(tf.global_variables_initializer())

        # Build the D which keeps experiences.
        self._time = 0
        self._epsilon = 1.0
        self._epsilon_decay_time = 180
        self._epsilon_decay_rate = 0.99
        self._experiences_max = 1000
        self._experiences_num = 0
        self._experiences_prev_states = np.zeros((self._experiences_max, self._dim_state))
        self._experiences_next_states = np.zeros((self._experiences_max, self._dim_state))
        self._experiences_rewards = np.zeros((self._experiences_max))
        self._experiences_actions_mask = np.zeros((self._experiences_max, self._dim_action))

    def create_experience(self, prev_state, prev_action, reward, next_state):
        """
        keep an experience for later training.
        """
        if self._experiences_num >= self._experiences_max:
            idx = np.random.choice(self._experiences_max)
        else:
            idx = self._experiences_num
        self._experiences_num += 1
        self._experiences_prev_states[idx] = np.array(prev_state)
        self._experiences_next_states[idx] = np.array(next_state)
        self._experiences_rewards[idx] = reward
        self._experiences_actions_mask[idx] = np.zeros(self._dim_action)
        for action in prev_action:
            self._experiences_actions_mask[idx, action] = 1.0

    def train(self):
        """
        train the deep q-learning network.
        """
        # start training only when there are enough experiences.
        if self._experiences_num < self._experiences_max:
            return
        ixs = np.random.choice(self._experiences_max, self._batch_size, replace=True)
        fatches = [self._tf_loss, self._tf_training]
        feed = {
            self._tf_prev_states: self._experiences_prev_states[ixs],
            self._tf_prev_action_masks: self._experiences_actions_mask[ixs],
            self._tf_prev_rewards: self._experiences_rewards[ixs],
            self._tf_next_states: self._experiences_next_states[ixs]
        }
        loss, _ = self._tf_session.run(fatches, feed_dict=feed)

    def act(self, observation, reward):
        """
        ask the next action from the agent
        """
        self._time += 1
        if self._time % self._epsilon_decay_time == 0:
            self._epsilon *= self._epsilon_decay_rate

        if np.random.rand() > self._epsilon:
            states = np.array([observation])
            action_values = self._tf_action_value_predict.eval(
                feed_dict={self._tf_prev_states: states})
            #Split the action values up into 3 parts: buttons, stick x, stick y
            #TODO make this configurable
            action_values = action_values[0]
            button_values = action_values[0:6]
            stick_x_values = action_values[6:13]
            stick_y_values = action_values[13:]

            action_button = np.argmax(button_values)
            action_stick_x = np.argmax(stick_x_values)
            action_stick_y = np.argmax(stick_y_values)
            action = [action_button, action_stick_x, action_stick_y]
        else:
            #TODO Make configurable
            action = [np.random.randint(6), np.random.randint(7), np.random.randint(7)]

        self._prev_state = observation
        self._prev_action = action
        self._prev_reward = self._prev_reward + reward
        self.train()
        return action

    def reset(self):
        if self._prev_state is not None:
            zeros = np.zeros(self._dim_state)
            self.create_experience(
                self._prev_state, self._prev_action, 0, zeros)
            self._prev_state = None
            self._prev_action = None
            self._prev_reward = 0

    def save(self):
        saver = tf.train.Saver()
        saver = tf.train.Saver()
        sess = tf.Session()
        sess.run(tf.initialize_all_variables())
        saver.save(sess, 'my-model')

    def restore(self):
        sess = tf.Session()
        new_saver = tf.train.import_meta_graph('my-model')
        new_saver.restore(sess, tf.train.latest_checkpoint('./'))
        all_vars = tf.trainable_variables()
