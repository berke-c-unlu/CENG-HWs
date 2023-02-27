import random
import copy
import numpy as np


     

class Agent:
    def __init__(self, symbol, alpha, gamma, epsilon):
        self.symbol = symbol
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.Q_table = {} # key (state, action) -> value (Q-value)

        # Initialize Q-table
        self.initialize_Q_table()

    def initialize_Q_table(self):
        self.Q_table = self.__create_Q_table()
    
    def get_Q_value(self, i, j, action):
        # if Q[state][action] is not defined, return 0
        if self.Q_table[(i,j)][action][1] == 0:
            return 0
        return self.Q_table[(i,j)][action][1]

    def update_Q_value(self, i, j, action, new_value):
        self.Q_table[(i,j)][action] = (self.Q_table[(i,j)][action][0], new_value)



    def __create_Q_table(self):
        # Create a Q-table with all possible states and actions
        state = "---------"
        permutations = [(state, 0)]
        Q_table = {}

        # Create permutations
        for i in range(9):
            for state in permutations: 
                if state[0][i] == "-":
                    state_x = state[0][:i] + "X" + state[0][i+1:]
                    state_o = state[0][:i] + "O" + state[0][i+1:]
                    permutations.append((state_x, 0)) # add to permutations
                    permutations.append((state_o, 0)) # add to permutations
        
        # Create Q-table
        for i in range(3):
            for j in range(3):
                Q_table[(i,j)] = permutations

        return Q_table


class Q_learning_agent(Agent):
    def __init__(self, symbol, alpha, gamma, epsilon):
        super().__init__(symbol, alpha, gamma, epsilon)
        


class SARSA_agent(Agent):
    def __init__(self, symbol, alpha, gamma, epsilon):
        super().__init__(symbol, alpha, gamma, epsilon)



class Game:
    def __init__(self, agent1 : Q_learning_agent or SARSA_agent, agent2 : Q_learning_agent or SARSA_agent):
        self.state = '---------' # S
        self.actions = [0, 1, 2, 3, 4, 5, 6, 7, 8] # A

        self.agent1 = agent1 # X agent
        self.agent2 = agent2 # O agent

    def reset_game(self):
        self.state = '---------'
        self.actions = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    def is_game_over(self):
        # Return True if the game is over, False otherwise
        # Check rows and columns and diagonals
        for i in range(0, 9, 3):
            if self.state[i] == self.state[i + 1] == self.state[i + 2] and self.state[i] != '-':
                return True
        for i in range(3):
            if self.state[i] == self.state[i + 3] == self.state[i + 6] and self.state[i] != '-':
                return True
        if self.state[0] == self.state[4] == self.state[8] and self.state[0] != '-':
            return True
        if self.state[2] == self.state[4] == self.state[6] and self.state[2] != '-':
            return True
        # Check draw
        if '-' not in self.state:
            return True
        # Game is not over
        return False

    def who_won(self):
        # Check if the game is over
        # Return 1 if X wins, -1 if O wins, 0 if draw, None if the game is not over
        # Check rows
        for i in range(0, 9, 3):
            if self.state[i] == self.state[i + 1] == self.state[i + 2] != '-':
                return self.state[i]
        # Check columns
        for i in range(3):
            if self.state[i] == self.state[i + 3] == self.state[i + 6] != '-':
                return self.state[i]
        # Check diagonals
        if self.state[0] == self.state[4] == self.state[8] != '-':
            return self.state[0]
        if self.state[2] == self.state[4] == self.state[6] != '-':
            return self.state[2]
        # Check draw
        if '-' not in self.state:
            return 0
        # Game is not over
        return None

    def get_reward_value(self, agent_symbol):
        # Return the reward for the agent with the given symbol
        # Return 1 if the agent wins, -1 if the agent loses, 0 if draw, None if the game is not over
        won = self.who_won()
        if won is None:
            return 0
        elif won == agent_symbol:
            return 1
        elif won == 0:
            return 0
        else:
            return -1

    def get_possible_actions(self):
        # Return a list of possible actions for the current board
        return [i for i in range(9) if self.state[i] == '-']

    def choose_action(self, agent_symbol : str):
        # Choose an action for the agent
        if np.random.random() < self.agent1.epsilon:
            possible_actions = self.get_possible_actions()
            chosen_action = possible_actions[np.random.randint(0, len(possible_actions))]
        else:
            possible_actions = self.get_possible_actions()
            ij_list = []
            for act in possible_actions:
                i,j = self.__create_ij_from_action(act)
                ij_list.append((i,j))
            if agent_symbol == 'X':
                # find maxQ for agent1 by looking every possible action in Q-table
                qs = [self.agent1.Q_table[key][action][1] for key,action in zip(ij_list, possible_actions)]
                maxQ = max(qs) if len(qs) >= 1 else qs[0]

                # If there are multiple actions with the same maxQ, choose one of them randomly
                count = qs.count(maxQ)
                if count > 1:
                    best = [i for i in range(len(possible_actions)) if qs[i] == maxQ]
                    chosen_action_ind = np.random.choice(best)
                else:
                    chosen_action_ind = qs.index(maxQ)
                chosen_action = possible_actions[chosen_action_ind]
            else:
                # find maxQ for agent2 by looking every possible action in Q-table
                qs = [self.agent2.Q_table[key][action][1] for key,action in zip(ij_list, possible_actions)]
                maxQ = max(qs) if len(qs) >= 1 else qs[0]

                # If there are multiple actions with the same maxQ, choose one of them randomly
                count = qs.count(maxQ)
                if count > 1:
                    best = [i for i in range(len(possible_actions)) if qs[i] == maxQ]
                    chosen_action_ind = np.random.choice(best)
                else:
                    chosen_action_ind = qs.index(maxQ)
                chosen_action = possible_actions[chosen_action_ind]
        return chosen_action
                
    def act(self, agent_symbol : str, action : int):
        # Update the board with the given action
        # Return the new state
        if self.state[action] == '-':
            self.state = self.state[:action] + agent_symbol + self.state[action+1:]
        return self.state


    def play_game(self, episode_count : int):
        for _ in range(episode_count):
            self.reset_game()
            # choose which agent will start the game
            chosen = np.random.choice(['X', 'O'])
            first = self.agent1 if chosen == 'X' else self.agent2
            second = self.agent2 if chosen == 'X' else self.agent1
            current_player = first

            # Play the game
            while not self.is_game_over():
                action = self.choose_action(current_player.symbol)
                # get i,j from state
                i,j = self.__create_ij_from_action(action)
                # Update the board
                new_state = self.act(current_player.symbol, action)
                # Update Q-table
                reward = self.get_reward_value(current_player.symbol)

                # if current player is an Q-learning agent
                if isinstance(current_player, Q_learning_agent):
                    # Update Q-table
                    # Q(s,a) = Q(s,a) + alpha * (reward + gamma * maxQ(S',a) - Q(s,a))
                    old_Q_value = current_player.get_Q_value(i, j, action)
                    max_Q_value = 0
                    for a in self.get_possible_actions():
                        i,j = self.__create_ij_from_action(a)
                        max_Q_value = max(max_Q_value, current_player.get_Q_value(i, j, a))                    
                    new_Q_value = old_Q_value + current_player.alpha * (reward + current_player.gamma * max_Q_value - old_Q_value)
                    current_player.update_Q_value(i, j, action, new_Q_value)
                
                # if current player is an Sarsa agent
                elif isinstance(current_player, SARSA_agent):
                    # Update Q-table
                    # Q(s,a) = Q(s,a) + alpha * (reward + gamma * Q(S',a') - Q(s,a))
                    old_Q_value = current_player.get_Q_value(i, j, action)
                    if self.is_game_over():
                        new_Q_value = old_Q_value + current_player.alpha * (reward - old_Q_value)
                        break
                    next_action = self.choose_action(current_player.symbol)
                    next_i, next_j = self.__create_ij_from_action(next_action)
                    next_Q_value = current_player.get_Q_value(next_i, next_j, next_action)
                    new_Q_value = old_Q_value + current_player.alpha * (reward + current_player.gamma * next_Q_value - old_Q_value)


                current_player = first if current_player == second else second



        return self.agent1.Q_table, self.agent2.Q_table
        

    
    def __create_ij_from_action(self, action):
        i = action // 3
        j = action % 3
        return i, j
   



def SolveMDP(method_name : str, problem_file_name : str, random_seed : int) -> list:
    ### Read the problem file
    with open(problem_file_name, 'r') as f:
        lines = f.readlines()
        # Find indexes of labels []
        alpha_index = lines.index('[alpha]\n')
        gamma_index = lines.index('[gamma]\n')
        epsilon_index = lines.index('[epsilon]\n')
        episode_index = lines.index('[episode count]\n')

        # Read values
        alpha = float(lines[alpha_index + 1])
        gamma = float(lines[gamma_index + 1])
        epsilon = float(lines[epsilon_index + 1])
        episode_count = int(lines[episode_index + 1])


    # Set random seed
    np.random.seed(random_seed)
    if method_name == 'QLearning':
        first_agent = Q_learning_agent('X',alpha, gamma, epsilon)
        second_agent = SARSA_agent('O',alpha, gamma, epsilon)
        game = Game(first_agent, second_agent)

        q_table1, q_table2 = game.play_game(episode_count)
        print(q_table1)


    elif method_name == 'SARSA':
        first_agent = SARSA_agent('X',alpha, gamma, epsilon)
        second_agent = Q_learning_agent('O',alpha, gamma, epsilon)
        game = Game(first_agent, second_agent)

        q_table1, q_table2 = game.play_game(episode_count)
        print(q_table1)