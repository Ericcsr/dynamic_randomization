import gym
import tensorflow as tf
import numpy as np

from actor import Actor
from critic import Critic

MAX_STEPS = 100
TAU = 1e-3
LEARNING_RATE = 5e-4

class Agent:
    def __init__(self, experiment, batch_size):
        self._dummy_env = gym.make(experiment)
        self._sess = tf.Session()
        
        # Hardcoded for now
        self._dim_state = 10
        self._dim_goal = 3
        self._dim_action = self._dummy_env.action_space.shape[0]
        self._dim_env = 1
        self._batch_size = batch_size
       
        self._actor = Actor(self._sess,
            self._dim_state, self._dim_goal, self._dim_action, self._dummy_env, TAU, LEARNING_RATE, self._batch_size)

        self._critic = Critic(self._sess,
            self._dim_state, self._dim_goal, self._dim_action, self._dim_env, self._dummy_env, TAU, LEARNING_RATE, self._actor.get_num_trainable_vars())

        self._sess.run(tf.global_variables_initializer())

        self._actor.update_target_network()
        self._critic.update_target_network()

        #loss_summary = tf.summary.scalar('loss', self._critic._loss)
        #writer = tf.summary.FileWriter('logs/')
        #writer.add_summary(
        #writer.add_graph(tf.get_default_graph())
        #writer.flush()

    def evaluate_actor(self, actor_predict, obs, goal, history):

        assert (history.shape[0] == MAX_STEPS), "history must be of size MAX_STEPS"

        obs = obs.reshape(1, self._dim_state)
        goal = goal.reshape(1, self._dim_goal)
        history = history.reshape(1, history.shape[0], history.shape[1])

        return actor_predict(obs, goal, history)

    def evaluate_actor_batch(self, actor_predict, obs, goal, history):

        return actor_predict(obs, goal, history)

    def evaluate_critic(self, critic_predict, obs, action, goal, history, env):
        obs = obs.reshape(1, self._dim_state)
        goal = goal.reshape(1, self._dim_goal)
        action = action.reshape(1, self._dim_action)
        history = history.reshape(1, history.shape[0], history.shape[1])
        env = env.reshape(1, self._dim_env)

        return critic_predict(env, obs, goal, action, history)

    def evaluate_critic_batch(self, critic_predict, obs, action, goal, history, env):
        return critic_predict(env, obs, goal, action, history)

    def train_critic(self, obs, action, goal, history, env, predicted_q_value):
        return self._critic.train(env, obs, goal, action, history, predicted_q_value)

    def train_actor(self, obs, goal, history, a_gradient):
        return self._actor.train(obs, goal, history, a_gradient)

    def action_gradients_critic(self, obs, action, goal, history, env):
        return self._critic.action_gradients(env, obs, goal, action, history)

    def update_target_actor(self):
        self._actor.update_target_network()

    def update_target_critic(self):
        self._critic.update_target_network()