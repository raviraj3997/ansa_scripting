# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants
deck = constants.ABAQUS
ansys_deck = constants.ANSYS
import Write_Connectors_and_Fasteners
import Write_MPC
import importlib
importlib.reload(Write_Connectors_and_Fasteners)
importlib.reload(Write_MPC)


import os

folder = os.getcwd()    # files created will be 'connectors_only.dat', 'connectors_and_fasteners.dat', 'fasteners.dat'
conn_sections = base.CollectEntities(deck, None, 'CONNECTOR_SECTION')
fasteners = base.CollectEntities(deck, None, 'FASTENER')
print(folder)
conns = Write_Connectors_and_Fasteners.process_entities(location= folder, connectors= conn_sections, fasteners= fasteners)


mpcs = base.CollectEntities(deck, None, 'MPC')
mpcs = Write_MPC.process_entities(mpcs = mpcs)


# x=22
# aa = base.CollectEntities(deck, None, 'MPC')


# debug_mode = constants.REPORT_ALL 
# variables_list = {'Subtype':'Beam'} 
# beam_ent, debug_report = base.CreateEntity(ansys_deck, 'SECTION_JOINT', variables_list, debug = debug_mode)    

# variables_list = {'Subtype':'Link'} 
# link_ent, debug_report = base.CreateEntity(ansys_deck, 'SECTION_JOINT', variables_list, debug = debug_mode)    
	
# type_mapping = {
# 	"BEAM":beam_ent._id,
# 	"PIN": link_ent._id
# }

# mpcs = base.CollectEntities(deck, None, 'MPC')
# for mpc in mpcs:
#     type = mpc.get_entity_values(deck,('TYPE', ))['TYPE']
#     if type in type_mapping.keys():
#         fields = mpc.card_fields(deck)
#         field_vals = mpc.get_entity_values(deck,(fields))
#         node0 = field_vals['NODE0']._id
#         nodes = [field_vals[f'NODE{i}']._id for i in range(0,len(fields)) if f'NODE{i}' in fields and i != 0]
#         for node in nodes:
#             variables_list = {'I':node, 'J':node0, 'PID':type_mapping[type]} 
#             ent, debug_report = base.CreateEntity(ansys_deck, 'JOINT', variables_list, debug = debug_mode) 
#     else:
#         print(f"*MPC with type:'{type}' is not processed")   
	
# # new_include=base.CreateEntity(ansys_deck, "INCLUDE")
# # base.AddToInclude(new_include,aa)

# print(len(mpcs))
# print(aa)


# connectors = base.CollectEntities(deck, None, 'CONNECTOR')
# fasteners = base.CollectEntities(deck, None, 'FASTENER')

# base.DeleteEntity(connectors, False, False)
# base.DeleteEntity(fasteners, False, False)