#from SurvivalAgent import SurvivalAgent
class Rule:
    def __init__(self, match_func, do_func):
        """
        Initialize the Rule with custom match and do functions.
        :param match_func: A function that defines the condition to match.
        :param do_func: A function that defines the action to take when matched.
        """
        self.match = match_func
        self.done=False# Assign the match function dynamically
        self.do = do_func       

class Belief:
    def __init__(self,name:str,type:str,position=None,extraInf=None):
        self.name=name
        self.position=position
        self.type=type
        self.extraInf=extraInf

#*** Match Functions ***
def match_hungry(agent)->bool:
    return agent.hunger<60
def match_know_food(agent)->bool:
    return any(belief.type=='food' for belief in agent.beliefs)
def match_know_water(agent)->bool:
    return any(belief.type=='water' for belief in agent.beliefs)
def match_thirst(agent)->bool:
    return agent.thirst<60
def match_dying(agent)->bool:
    return agent.health<40
def match_friend_in_danger(agent)->bool:
    return any(belief.type=='comunication' and belief.name=="danger" for belief in agent.beliefs)
def match_goal_arrived(agent,goal)->bool:

    """
    Checks if the Manhattan distance between two points is exactly 1.
    :param point1: Tuple (x1, y1) representing the first point.
    :param point2: Tuple (x2, y2) representing the second point.
    :return: True if Manhattan distance is 1, otherwise False.
    """
    x1, y1 = goal
    x2, y2 = agent.position
    manhattan_distance = abs(x1 - x2) + abs(y1 - y2)
    return manhattan_distance == 1
def match_has_food(agent):
    return any(x=="F" for x in agent.inventory )


#*** Match Functions for Desires ***

 
#***Do Functions***
def introduce_belief(agent, belief:Belief):
    agent.beliefs.append(belief)
def introduce_desire(agent, belief:Belief):
    agent.desires.append(belief)
def eliminate_belief(agent, belief: Belief):
    """
    Removes a belief from the agent's belief list if it matches the given belief.
    :param agent: The agent whose belief should be removed.
    :param belief: The belief to be removed.
    """
    agent.beliefs = [b for b in agent.beliefs if not (b.name == belief.name and b.type == belief.type and b.position == belief.position)]

rules_set=[
    Rule(lambda x: match_know_food(x),lambda x: add_pick_or_go_food(x)),
    Rule(lambda x: match_know_water(x) and match_thirst(x) , lambda x: add_pick_or_go_water(x)),
    Rule(lambda x: not match_know_food(x) and match_hungry(x),lambda x:introduce_desire(x,Belief('Explorar','desire'))),
    Rule(lambda x: not match_know_water(x) and match_thirst(x),lambda x:introduce_desire(x,Belief('Explorar','desire'))),
    Rule(lambda x: match_has_food(x) and match_hungry(x),lambda x:introduce_desire(x,Belief('Comer','desire0'))),
    Rule(lambda x: not match_know_water(x) and match_thirst(x),lambda x:introduce_desire(x,Belief('Comunicar sed','desire0'))),
    Rule(lambda x: not match_know_food(x) and match_hungry(x),lambda x:introduce_desire(x,Belief('Comunicar hambre','desire0')))
]
def add_pick_or_go_food(agent):
    for belief in agent.beliefs:
        if belief.type=='food':
            if match_goal_arrived(agent,belief.position):
                introduce_desire(agent,Belief('Coger comida','desire',belief.position))
            else:
                introduce_desire(agent,Belief('Buscar comida','desire',belief.position))

def add_pick_or_go_water(agent):
    for belief in agent.beliefs:
        if belief.type=='water':
            if match_goal_arrived(agent,belief.position):
                introduce_desire(agent,Belief('Beber agua','desire',belief.position))
            else:
                introduce_desire(agent,Belief('Buscar agua','desire',belief.position))


def get_highest_ranked_desire(agent):
    highest_desire_and_0step_desires:list[Belief]=[]
    one_step_desire=None
    rank=0
    for desire in agent.desires:
        if(desire.type=='desire0'):
            highest_desire_and_0step_desires.append(desire)
        else:
            actual_rank=rank_desire(desire,agent)
            if(actual_rank>rank):
                rank=actual_rank
                one_step_desire=desire
    if(one_step_desire!=None):
        highest_desire_and_0step_desires.append(one_step_desire)
    return highest_desire_and_0step_desires

def rank_desire(desire:Belief,agent):
     
    def heuristic(a, b):
        """ Heuristic function to estimate the distance between current node and target. """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    rank=0
    if(desire.name=='Buscar comida'):
        distance_proportion=1/heuristic(agent.position,desire.position)
        hunger_weight=(distance_proportion*(1/agent.hunger))
        return hunger_weight
    if(desire.name=='Coger comida'):
        hunger_weight=(1/agent.hunger)
        return hunger_weight
    if desire.name=='Beber agua':
        thirst_weight= (1/agent.thirst)
        return thirst_weight
    if desire.name=='Buscar agua':
        distance_proportion=1/heuristic(agent.position,desire.position)
        thirst_weight= distance_proportion*(1/agent.thirst)
        return thirst_weight
    if desire.name=='Explorar':
        total=0
        hunger_weight=0
        if(match_hungry(agent)):
            total+=1
            hunger_weight=1/agent.hunger
        
        thirst_weight=0
        if(match_thirst(agent)):
            total+=1
            thirst_weight=1/agent.thirst
        rank=(hunger_weight+thirst_weight)/total
        return total

        
    return rank


desire_action=  { 
'Buscar comida':lambda x,y,env: act_seek_for(x,y),
'Coger comida':lambda x,y,env: act_grab_food(x,y,env),
'Buscar agua':lambda x,y,env: act_seek_for(x,y),
'Beber agua': lambda x,y,env: act_grab_water(x,y),
}

def act_seek_for(agent,pos):
    print("Buscando recurso en ", pos)
    agent.move(pos,agent.memory)

def act_grab_food(agent,pos,env):
    print("Cogio comida en ", pos)
    agent.pick(pos,env)

def act_grab_water(agent,pos):
    print("Bebio agua en", pos)
    agent.pick_water(pos)
def act_explore(agent):
    agent.explore_unknown_area()
