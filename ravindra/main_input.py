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

@ansa.session.defbutton('AUXILIARIES', 'Abaqus2MAPDL')

def main():

    folder = os.getcwd()

    contact_set_correction.correcter_conta_set()
    cohesive_correction.correct_cohasive(target = "GASKET")

    # step = base.CollectEntities(constants.ABAQUS, None, 'STEP')
    # base.DeleteEntity(step, True, True)

    # step_manager = base.CollectEntities(constants.ABAQUS, None, 'STEP MANAGER')
    # base.DeleteEntity(step_manager, True, True)


    conn_sections = base.CollectEntities(deck, None, 'CONNECTOR_SECTION')
    fasteners = base.CollectEntities(deck, None, 'FASTENER')
    conns = Connector_Fastner_to_CONTA_MPC.process_entities(connectors= conn_sections, fasteners=fasteners)

    mpcs = base.CollectEntities(deck, None, 'MPC')
    mpcs = MPC_to_Contact.process_entities(mpcs = mpcs)


    Kinematic_Coupling.convert_kinematic_cupling('ABAQUS','ANSYS', 'JOINT')

    Write_Material.upadate_materials()

    export.export_cdb_from_ansa()

# conn_sections = base.CollectEntities(deck, None, 'CONNECTOR_SECTION')
# fasteners = base.CollectEntities(deck, None, 'FASTENER')
# conns = Connector_Fastner_to_CONTA_MPC.process_entities(connectors= conn_sections, fasteners=fasteners)

# vec = (0.15643452721490966, 2.1474605211052765e-06, 0.9876883307452995)
# n_loc = {'X': 242.36824035644, 'Y': -796.2670288086, 'Z': 498.48123168945}
# face = base.GetEntity(constants.ANSYS,  "SET", 164)
# print(face)
# elements = base.CollectEntities(constants.ANSYS, face, "SHELL", recursive=True)
# print(len(elements))
# projection = base.ProjectPointDirectional(elements, n_loc['X'], n_loc['Y'], n_loc['Z'], vec[0], vec[1], vec[2], float(10.0), project_on="elements")
# print(projection)
# et = calc.ProjectPointsToElements([(n_loc['X'], n_loc['Y'], n_loc['Z'])], elements, 10.0, vec)
# print(et)
# for proj in et:
# 		if proj is not None:
# 			print(proj.projection)
# 			print(proj.distance)
# 			print(proj.entity)
			
# nodes = base.CollectEntities(constants.ANSYS, proj.entity, 'NODE')
# print(nodes)