# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants
deck = constants.ABAQUS
import Write_Connectors
import importlib
importlib.reload(Write_Connectors)



# def main():
# 	# Need some documentation? Run this with F5
deck = constants.ABAQUS

conn_sections = base.CollectEntities(deck, None, 'CONNECTOR_SECTION')
conn_sec = conn_sections[0]
connector_section_prop = conn_sec.get_entity_values(deck,('MID',))

print(connector_section_prop)

# 	sec_elems = base.CollectEntities(deck, conn_sec, None)
	
# 	behave = connector_section_prop['MID']
# 	mat_name = behave._name
	
# 	dirr = dir(behave)
# 	mat_elast = base.NameToEnts("^CONNECTOR ELASTICITY:"+mat_name)
# 	conn_behave2 = base.CollectEntities(deck, None, 'CONNECTOR_ELASTICITY')
# 	name = conn_behave2[0]._name
# 	conn_behave2_prop = conn_behave2[0].get_entity_values(deck,('COMP','COMP(1)','NONLINEAR(1)','El.Stiff.(1)', 'Freq.(1)'))
# 	stiff = conn_behave2_prop['El.Stiff.(1)']
	
# 	coordinate_sys = connector_section_prop['ORIENT_1']
# 	c_name = coordinate_sys._name
	
# 	aa = 2
# if __name__ == '__main__':
# 	main()

import os

connector_file = os.path.join(os.getcwd(), 'connectors_input.dat')


conns = Write_Connectors.ConnectorSections(conn_sections, connector_file)
conns.write()

x=22
