from distutils.util import change_root
import os
from ansa import base
from ansa import utils
from ansa import constants
import time


def export_cdb_from_ansa():
    export_obj = Exporter()
    export_obj.exclude = ['CERIG']
    export_obj.export_cdb('new_include_file_set.cdb')


class Exporter:
    def __init__(self):
        self.exclude = []
        self._includes = ['__PROPERTIES__','__ELEMENTS__', 'NODE', '__COORD_SYSTEMS__','__MATERIALS__', 'CONTACT']
        self.include_entities = []
        self.exclude_entities = []
        self.entities_to_export  = []

    def set_exclude(self,exclude_containers):
        self.exclude = exclude_containers
    def add_to_exclude(self,item):
        if item not in self.exclude:
            self.exclude.append(item)
    def export_cdb(self, cdb_file):
        deck = constants.ANSYS
        self.change_deck(deck)
        if len(self.include_entities)==0:
            for include_item in self._includes:
                self.include_entities.extend(base.CollectEntities(deck,None, include_item))
        if len(self.exclude_entities)==0:
            for entity_type in self.exclude:
                exclude_list = base.CollectEntities(deck, None, entity_type)
                print(entity_type," : ", len(exclude_list))
                self.exclude_entities.extend(exclude_list)
        self.entities_to_export = set(self.include_entities) - set(self.exclude_entities)
        print("Exported Entities : ", len(self.entities_to_export))
        print("include_entities : ", len(self.include_entities))
        print("exclude_entities : ", len(self.exclude_entities))
        include = base.CreateEntity(deck, "INCLUDE", {'Name': cdb_file})
        base.AddToInclude(include, self.entities_to_export)

    def change_deck(self, deck):
        if deck != base.CurrentDeck():
            base.SetCurrentDeck(deck)
            time.sleep(20)