import gym, random
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.models import model_from_json
import numpy as np
from collections import deque
import time
import tensorflow as tf


class DQLAgent:
    def __init__(self, env):
        self.state_size = env.observation_space.shape[0]
        self.action_size = env.action_space.n
        self.epsilon = 0.01
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.99
        self.gamma = 0.99
        self.learning_rate = 0.0001
        self.memory = deque(maxlen=4000)
        self.model = self.build_model()
        self.target_model = self.build_model()

    def build_model(self):
        model = Sequential()
        model.add(Dense(64, input_dim=self.state_size, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def save_model(self):
        model_json = self.model.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights("model.h5")
        print("Saved model to disk")

    def load_model(self):
        # load json and create model
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights("model.h5")
        print("Loaded model from disk")
        self.model = loaded_model

    def act(self, s):
        if np.random.rand() <= self.epsilon:
            return np.random.choice(self.action_size)
        act_values = self.model.predict(s)
        return np.argmax(act_values[0])

    def replay(self, batch_size):
        "vectorized replay method"
        if len(self.memory) < batch_size:
            return
        # Vectorized method for experience replay
        minibatch = random.sample(self.memory, batch_size)
        minibatch = np.array(minibatch)
        not_done_indices = np.where(minibatch[:, 4] == False)
        y = np.copy(minibatch[:, 2])

        # If minibatch contains any non-terminal states, use separate update rule for those states
        if len(not_done_indices[0]) > 0:
            predict_sprime = self.model.predict(np.vstack(minibatch[:, 3]))
            predict_sprime_target = self.target_model.predict(np.vstack(minibatch[:, 3]))

            # Non-terminal update rule
            y[not_done_indices] += np.multiply(self.gamma, predict_sprime_target[
                not_done_indices, np.argmax(predict_sprime[not_done_indices, :][0], axis=1)][0])

        actions = np.array(minibatch[:, 1], dtype=int)
        y_target = self.model.predict(np.vstack(minibatch[:, 0]))
        y_target[range(batch_size), actions] = y
        self.model.fit(np.vstack(minibatch[:, 0]), y_target, epochs=1, verbose=0)

    #    def replay(self, batch_size):
    #        # training
    #        if len(self.memory) < batch_size:
    #            return
    #        minibatch = random.sample(self.memory,batch_size)
    #        for state, action, reward, next_state, done in minibatch:
    #            if done:
    #                target = reward
    #            else:
    #                target = reward + self.gamma*np.amax(self.model.predict(next_state)[0])
    #            train_target = self.model.predict(state)
    #            train_target[0][action] = target
    #            self.model.fit(state,train_target, verbose = 0)

    def adaptiveEGreedy(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def targetModelUpdate(self):
        self.target_model.set_weights(self.model.get_weights())


def train_the_model(agent, episodess):
    if __name__ == "__main__":

        state_number = env.observation_space.shape[0]

        batch_size = 32
        episodes = episodess
        for e in range(episodes):

            state = env.reset()
            state = np.reshape(state, [1, state_number])

            total_reward = 0
            for time in range(1000):

                # env.render()

                # act

                action = agent.act(state)

                # step
                next_state, reward, done, _ = env.step(action)
                next_state = np.reshape(next_state, [1, state_number])

                # remember / storage
                agent.remember(state, action, reward, next_state, done)

                # update state
                state = next_state

                # Perform experience replay if memory length is greater than minibatch length
                agent.replay(batch_size)

                total_reward += reward

                if done:
                    agent.targetModelUpdate()
                    break

            # epsilon decay
            agent.adaptiveEGreedy()

            # Running average of past 100 episodes
            print('Episode: {}, Reward: {}'.format(e, total_reward))
            if e % 50 == 0:
                agent.save_model()
    
# %% test
def test_DQL(agent):

    state = env.reset()
    state = np.reshape(state, [1, env.observation_space.shape[0]])

    while True:
        env.render()
        action = agent.act(state)
        next_state, reward, done, _ = env.step(action)
        next_state = np.reshape(next_state, [1, env.observation_space.shape[0]])
        state = next_state

        time.sleep(0.05)
        if done:
            break
    print("Done")

env = gym.make('LunarLander-v2')
agent = DQLAgent(env)


train_the_model(agent,1000)
# test_DQL(agent)
