# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants

def main():
	# Need some documentation? Run this with F5
	deck = constants.ABAQUS
	prop = base.GetEntity(deck, "CONNECTOR", 2240128)
	print(prop)
	if prop == None:
		print('CONNECTOR property with ID 2240128 does not exist!')
	else:
		print('CONNECTOR property with ID 2240128, is named: ' )
		print(prop.get_entity_values(deck, ('G1',)))
		print(dir(prop))
	
	mbf = {'container': 'connections', 'collect_mode': 'contents'}
	connections = base.CollectEntities(deck, None, 'CONNECTOR')
	print("Total_connection are : ", len(connections))
	print(dir(connections[0]))
	
	conn_behave1 = base.CollectEntities(deck, None, 'CONNECTOR BEHAVIOR')
	conn_behave_type1 = conn_behave1[0]
	print("CONNECTOR BEHAVIOR : ", len(conn_behave1))
	print("CONNECTOR BEHAVIOR name is: ", conn_behave1[0]._name)
	
	conn_section = base.CollectEntities(deck, None, 'CONNECTOR_SECTION')
	conn_sec = conn_section[0]
	print("CONNECTOR SECTION : ", len(conn_section))
	print("CONNECTOR SECTION name is: ", conn_sec._name)
	
	# props_section =  conn_sec.get_entity_values(deck, ('ELSET',))
	
	print("CONNECTOR SECTION name is: ", conn_section[0]._name)
	connector_section_prop = conn_section[0].get_entity_values(deck,('MID','COMPONENT_1','COMPONENT_2','ORIENT_1','ORIENT_2'))
	print(connector_section_prop)
	behave = connector_section_prop['MID']
	mat_name = behave._name
	conn_behave2 = base.CollectEntities(deck, None, 'CONNECTOR_ELASTICITY')
	name = conn_behave2[0]._name
	conn_behave2_prop = conn_behave2[0].get_entity_values(deck,('COMP','COMP(1)','NONLINEAR(1)','El.Stiff.(1)', 'Freq.(1)'))
	stiff = conn_behave2_prop['El.Stiff.(1)']
	
	
	sets = base.CollectEntities(deck, None, 'SET')
	set = sets[-1]
	
	conn_sets =base.CollectEntities(deck, set, 'CONNECTOR_SECTION')
	conn_set= conn_sets[0]
	bb = base.CollectEntities(deck, conn_set, None)
	id_1 = bb[0]._id
	# mysets= base.CollectEntities(deck, None,'SET')

	# set_elems_shell_1=base.CollectEntities(deck, mysets[0], 'SHELL_SECTION')
	
	aa = 2
if __name__ == '__main__':
	main()


