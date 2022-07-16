import os
import string
import ansa
from ansa import base
from ansa import constants
import math


def process_entities(mpcs=[]) -> None:
	connector_data = MPCs(mpcs)
	connector_data.write()
	base.DeleteEntity(mpcs, False, False)
	# print(connector_data.all_connectors)


class MPCs:

    def __init__(self, mpcs) -> None:
        self.base = base
        self.deck = constants.ABAQUS
        self.ansys_deck = constants.ANSYS
        self.mpcs = mpcs

    def write(self):
        debug_mode = constants.REPORT_ALL 
        variables_list = {'Subtype':'Beam', 'KEYOPT(2)':1} 
        beam_ent, debug_report = base.CreateEntity(self.ansys_deck, 'SECTION_JOINT', variables_list, debug = debug_mode)    

        variables_list = {'Subtype':'Link', 'KEYOPT(2)':1} 
        link_ent, debug_report = base.CreateEntity(self.ansys_deck, 'SECTION_JOINT', variables_list, debug = debug_mode)    
            
        type_mapping = {
            "BEAM":beam_ent._id,
            "PIN": link_ent._id
        }

        mpcs = base.CollectEntities(self.deck, None, 'MPC')
        for mpc in mpcs:
            type = mpc.get_entity_values(self.deck,('TYPE', ))['TYPE']
            if type in type_mapping.keys():
                fields = mpc.card_fields(self.deck)
                field_vals = mpc.get_entity_values(self.deck,(fields))
                node0 = field_vals['NODE0']._id
                nodes = [field_vals[f'NODE{i}']._id for i in range(0,len(fields)) if f'NODE{i}' in fields and i != 0]
                for node in nodes:
                    variables_list = {'I':node, 'J':node0, 'PID':type_mapping[type]} 
                    ent, debug_report = base.CreateEntity(self.ansys_deck, 'JOINT', variables_list, debug = debug_mode) 
            else:
                print(f"*MPC with type:'{type}' is not processed")   
