# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants
deck = constants.ABAQUS
ansys_deck = constants.ANSYS
import Write_Connectors_and_Fasteners
import MPC_to_Contact
import contact_set_correction
import Kinematic_Coupling
import cohesive_correction
import Write_Material
import export
import importlib
importlib.reload(Write_Connectors_and_Fasteners)
importlib.reload(MPC_to_Contact)
importlib.reload(contact_set_correction)
importlib.reload(Kinematic_Coupling)
importlib.reload(cohesive_correction)
importlib.reload(Write_Material)
importlib.reload(export)

import os
import time

# @ansa.session.defbutton('AUXILIARIES', 'Abaqus2MAPDL')

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
    conns = Write_Connectors_and_Fasteners.process_entities(location= folder, connectors= conn_sections, fasteners= fasteners)

    mpcs = base.CollectEntities(deck, None, 'MPC')
    mpcs = MPC_to_Contact.process_entities(mpcs = mpcs)


    Kinematic_Coupling.convert_kinematic_cupling_to_contact('ABAQUS','ANSYS', 'JOINT')

    Write_Material.upadate_materials()

    export.export_cdb_from_ansa()

