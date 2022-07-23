import os
import string
import ansa
from ansa import base
from ansa import constants
import math
from general_defs import Set


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
        dofs_mapping = {
            "BEAM":'123456',
            "PIN": '123'
        }

        mpcs = base.CollectEntities(self.deck, None, 'MPC')
        for mpc in mpcs:
            type = mpc.get_entity_values(self.deck,('TYPE', ))['TYPE']
            # print(type)
            if type in dofs_mapping.keys():
                fields = mpc.card_fields(self.deck)
                field_vals = mpc.get_entity_values(self.deck,(fields))
                ref_node = field_vals['NODE0']
                # print(ref_node)
                nodes = [field_vals[f'NODE{i}'] for i in range(0,len(fields)) if f'NODE{i}' in fields and i != 0]
                
                # print(nodes)
                ref_set = Set('ANSYS').create_nodal_set(name=f'MPC_TARGET_{mpc._id}',nodes=[ref_node])
                cont_set = Set('ANSYS').create_nodal_set(name=f'MPC_CONTACT_{mpc._id}',nodes=nodes)
                dofs = dofs_mapping[type]
                self.create_contact(ref_node, dofs, ref_set, cont_set)
            else:
                print(f"*MPC with type:'{type}' is not processed")   

    def create_contact(self, ref_node, dofs, ref_set, cont_set):
        # Below two lines are not generic
        variables_list = {'CONTA': 'CONTA175','CSID':cont_set, 'TSID':ref_set, 'PILOT NODE': ref_node._id, 'CNT_KEYOPT(12)':5, 'CNT_KEYOPT(4)':0, 'CNT_KEYOPT(2)':2, 'TRG_KEYOPT(2)':1, 'TRG_KEYOPT(4)':dofs}
        base.CreateEntity(self.ansys_deck, 'CONTACT', variables_list) 

