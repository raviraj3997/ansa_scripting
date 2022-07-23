# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants
from ansa import calc
deck = constants.ABAQUS
ansys_deck = constants.ANSYS
import Connector_Fastner_to_CONTA_MPC
import MPC_to_Contact
import contact_set_correction
import Kinematic_Coupling
import cohesive_correction
import Write_Material
import export
import importlib
importlib.reload(Connector_Fastner_to_CONTA_MPC)
importlib.reload(MPC_to_Contact)
importlib.reload(contact_set_correction)
importlib.reload(Kinematic_Coupling)
importlib.reload(cohesive_correction)
importlib.reload(Write_Material)
importlib.reload(export)

import os
import time

# @ansa.session.defbutton('AUXILIARIES', 'Abaqus2MAPDL')

# def main():

#     folder = os.getcwd()

#     contact_set_correction.correcter_conta_set()
#     cohesive_correction.correct_cohasive(target = "GASKET")

#     # step = base.CollectEntities(constants.ABAQUS, None, 'STEP')
#     # base.DeleteEntity(step, True, True)

#     # step_manager = base.CollectEntities(constants.ABAQUS, None, 'STEP MANAGER')
#     # base.DeleteEntity(step_manager, True, True)

#     conn_sections = base.CollectEntities(deck, None, 'CONNECTOR_SECTION')
#     fasteners = base.CollectEntities(deck, None, 'FASTENER')
#     conns = Write_Connectors_and_Fasteners.process_entities(location= folder, connectors= conn_sections, fasteners= fasteners)

#     mpcs = base.CollectEntities(deck, None, 'MPC')
#     mpcs = MPC_to_Contact.process_entities(mpcs = mpcs)


#     Kinematic_Coupling.convert_kinematic_cupling('ABAQUS','ANSYS', 'JOINT')

#     Write_Material.upadate_materials()

#     export.export_cdb_from_ansa()


conn_sections = base.CollectEntities(deck, None, 'CONNECTOR_SECTION')
fasteners = base.CollectEntities(deck, None, 'FASTENER')
conns = Connector_Fastner_to_CONTA_MPC.process_entities(connectors= conn_sections, fasteners=fasteners)

# node = base.GetEntity(constants.ABAQUS,"NODE",337048137)
# fastener_obj = base.GetEntity(constants.ABAQUS,"FASTENER",1)

# n_loc = node.get_entity_values(constants.ANSYS,('X','Y','Z'))
# coords = (n_loc['X'], n_loc['Y'], n_loc['Z'])
# fast_prop = fastener_obj.get_entity_values(constants.ABAQUS,tuple(fastener_obj.card_fields(constants.ABAQUS)))
# ents = [fast_prop[f'SURF{i}'] for i in range(1,12) if fast_prop[f'SURF{i}'] != None]
# result = base.NearestShell(coordinates=coords, tolerance=500, search_entities=ents)
# shell = result[0]
# print(shell)

# vec = base.GetNormalVectorOfShell(shell[0])

# nodes = base.CollectEntities(constants.ABAQUS, shell, 'NODE')
# print(nodes)
# print(len(nodes))

# vec = base.GetNormalVectorOfShell(shell)
# print(vec)
# print("The shell with id " + str(id) + " has the normal vector dx: " + str(vec[0]) + " dy: " + str(vec[1]) + " dz: " + str(vec[2]))

# # m = base.ProjectPointDirectional(ents, coords[0], coords[1], coords[2], -vec[0], -vec[1], -vec[2], 10, project_on="elements")
# m = calc.ProjectPointToShell([ coords[0], coords[1], coords[2]], shell)
# print(m)




# def main():
#         fast = base.GetEntity(ansa.constants.ABAQUS, "FASTENER", 1)
#         mpc_nodes =  base.GetFastenerMPCNodes(fast)

#         for ref_node, surfaces in mpc_nodes.items():
#                 labs = ['__id__']
#                 ret = base.GetEntityCardValues(ansa.constants.ABAQUS, ref_node, labs)
#                 print(ret['__id__'])
#                 print("--------------------------------\n")
#                 for nodes in surfaces:
#                         for node in nodes:
#                                 ret = base.GetEntityCardValues(ansa.constants.ABAQUS, node, labs)
#                                 print(ret['__id__'])
#                         print("--------------------------------\n")

# if __name__ == '__main__':
#         main()
