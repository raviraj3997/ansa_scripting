# PYTHON script
import os
from ansa import base
from ansa import utils
from ansa import constants
deck = constants.ABAQUS

def correct_cohasive(target = "GASKET"):
    correct =DataBaseUpdate(deck)
    correct.change_element_type(source = 'COHESIVE', target=target)



class DataBaseUpdate:
    def __init__(self,deck):
        self.deck =  deck
        # Helper.sync_deck(self.deck)
    def change_element_type(self,source,target):
        '''
        Updater = DataBaseUpdate(base.CurrentDeck())
        Updater.change_element_type('COHESIVE','SOLID')
        :param source:
        :param target:
        :return:
        '''
        entities = base.CollectEntities(self.deck, None, source.upper())
        base.ChangeElemType(self.deck,entities,target.upper())