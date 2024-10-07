import random

class SocialAgent:
    def __init__(self, name):
        self.name = name
        self.beliefs = {
            'traits': ['introverted', 'extroverted'][random.randint(0, 1)],
            'friends': set(),
            'last_interaction': None
        }
        self.desires = {
            'make_friends': True,
            'attend_event': False
        }
        self.intentions = []

    def update_beliefs(self, other_agent):
        """ Update beliefs based on interaction with another agent. """
        self.beliefs['last_interaction'] = other_agent.name
        if other_agent.name not in self.beliefs['friends']:
            self.beliefs['friends'].add(other_agent.name)
            print(f"{self.name} made friends with {other_agent.name}!")

    def act(self, agents):
        """ Decide what to do based on desires. """
        if self.desires['make_friends']:
            potential_friend = random.choice(agents)
            if potential_friend != self:
                self.introduce(potential_friend)
                self.update_beliefs(potential_friend)

        if self.desires['attend_event']:
            self.intentions.append(f"{self.name} is attending a community event.")

    def introduce(self, other_agent):
        """ Simulate an introduction between two agents. """
        print(f"{self.name} is introducing themselves to {other_agent.name}.")

# Simulation
agents = [SocialAgent(f"Agent_{i}") for i in range(5)]

# Simulate interactions over a few time steps
for _ in range(3):
    print("New Time Step:")
    for agent in agents:
        agent.act(agents)
    print()
