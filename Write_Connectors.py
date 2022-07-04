from cgitb import text
import os
import ansa
from ansa import base
from ansa import constants
import math

class ConnectorSections:

	def __init__(self, conn_sections:list, out_file:str) -> None:
		self.base = base
		self.deck = constants.ABAQUS
		self.output_file = out_file
		self.conn_sections = conn_sections
		self.connector_materials = []

	def write(self):
		"""
		Write out the all properties (Material, Elemets, and Orientations) reataled to Given Connection Section. 

		"""
		file = open(self.output_file, 'w')
		file.close()

		for conn_section in self.conn_sections:
			conn_section_entities = conn_section.get_entity_values(self.deck,('MID','COMPONENT_1','COMPONENT_2','ORIENT_1','ORIENT_2' ))
			conn_mat = conn_section_entities['MID']
			conn_comp1 = conn_section_entities['COMPONENT_1']
			conn_comp2 = conn_section_entities['COMPONENT_2']

			if conn_mat != None:
				if conn_mat._name not in self.connector_materials:
					self.connector_materials.append(conn_mat._name)
					ConnectorMaterial(self.output_file, conn_mat, conn_comp1, conn_comp2).write()
			else:
				print("CONNECTOR SECTION with ELST:{} has no BEHAVIOR keyword. The connector element's behavior is determined by kinematic constraints only.")

			ORIENT_1 = conn_section_entities['ORIENT_1']
			ORIENT_2 = conn_section_entities['ORIENT_2']

			




class ConnectorMaterial:
	
	def __init__(self, out_file, material, conn_comp1, conn_comp2) -> None:
		self.base = base
		self.deck = constants.ABAQUS
		self.output_file = out_file
		self.material = material
		self.conn_comp1 = conn_comp1
		self.conn_comp2 = conn_comp2

	def write(self):

		"""
			Write out the all Connector Material properties defined in Connector Behavior. 
		"""

		# Write Connector Elasticity:
		conn_elast_list = base.NameToEnts("CONNECTOR ELASTICITY:"+self.material._name)
		if conn_elast_list:
			conn_elast = conn_elast_list[0]
			self.write_connector_elasticity(conn_elast)
			print(f"Writing connector material named TEst {self.material._name}")
			print(f"Writing connector material named TEst {conn_elast._name}")

	def write_connector_elasticity(self, conn_elast):
		file = open(self.output_file, 'a')
		comps = ['CARTESIAN','CARDAN']
		if self.conn_comp1 in comps and self.conn_comp2 in comps:
			file.write('*GET,MAT_MAX,MAT,0,NUM,MAX\n')
			file.write('M_ID = MAT_MAX+1\n')

			props = ('NONLINEAR(1)','NONLINEAR(2)','NONLINEAR(3)','NONLINEAR(4)','NONLINEAR(5)','NONLINEAR(6)',)
			check_linear = conn_elast.get_entity_values(self.deck, props)
			all_linear = True
			if any([True if i == 'YES' else False for i in list(check_linear.values())]):
				all_linear = False
			# print(f'all_linear = {all_linear}')

			if conn_elast.get_entity_values(self.deck,('COMP',))['COMP'] == 'YES':
				comps_ampping = {1:1,2:7,3:12,4:16,5:19,6:21}
				if all_linear:
					file.write('\n')
					file.write('TB,JOIN,M_ID,1,,STIF\n')
				for i in range(1,7):
					props = (f'COMP({i})',f'DEP({i})',f'RIGID({i})',f'NONLINEAR({i})',f'El.Stiff.({i})',f'Freq.({i})',f'Force({i})',f'Rel.Disp.({i})',)
					prop_dict = conn_elast.get_entity_values(self.deck, props)
					if prop_dict[f'DEP({i})'] != 'YES' and prop_dict[f'RIGID({i})'] != 'YES':
						if prop_dict[f'COMP({i})'] == 'YES':
							if prop_dict[f'NONLINEAR({i})'] == 'YES':
								print("Nonlinear Curve")
							else:
								if all_linear:
									stiff = prop_dict[f'El.Stiff.({i})']
									file.write(f'TBDATA,{comps_ampping[i]},{stiff}\n')
								else:
									stiff = prop_dict[f'El.Stiff.({i})']
									file.write('\n')
									file.write(f'TB,JOIN,M_ID,1,3,JNS{i}\n')
									file.write(f'TBDATA,,{-stiff}, -1.0 \n')
									file.write(f'TBDATA,,0.0,0.0\n')
									file.write(f'TBDATA,,{stiff}, 1.0\n')
						else:
							pass
					else:
						if prop_dict[f'DEP({i})'] != 'YES':
							print(f"Tabular values are given for *CONNECTOR ELASTICITY with NAME:{conn_elast._name}. And this entity is not converted.")
						if prop_dict[f'RIGID({i})'] != 'YES':
							print(f"'RIGID' values are given for *CONNECTOR ELASTICITY with NAME:{conn_elast._name}. And this entity is not converted.")
			else:
				print(f"Matrix values are given for *CONNECTOR ELASTICITY with NAME:{conn_elast._name}. And this entity is not converted.")
			file.write('\n')
			file.write(f'MAT, M_ID           !  Material Changed for following elements! \n')
			file.write('\n')
		else:
			print(f'{self.conn_comp1} is not Translated for {self.material._name}')

		file.close()

