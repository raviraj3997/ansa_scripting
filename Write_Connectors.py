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

		self.connector_materials = ''

	def write(self):
		"""
		Write out the all properties (Material, Elemets, and Orientations) reataled to Given Connection Section. 

		"""
		file = open(self.output_file, 'w')
		file.write('*GET,REAL_MAX,RCON,0,0,NUM,MAX\n')
		file.write('R_ID = REAL_MAX + 1\n')
		file.write('R,R_ID\n')
		file.write('\n')
		file.write(f'REAL, R_ID\n')
		file.write('\n')
		file.close()

		for conn_section in self.conn_sections:
			conn_section_entities = conn_section.get_entity_values(self.deck,('MID','COMPONENT_1','COMPONENT_2','ORIENT_1','ORIENT_2' ))
			# print(conn_section.card_fields(self.deck))
			conn_mat = conn_section_entities['MID']
			conn_comp1 = conn_section_entities['COMPONENT_1']
			conn_comp2 = conn_section_entities['COMPONENT_2']

			if conn_mat != None:
				if conn_mat._name != self.connector_materials:
					self.connector_materials = conn_mat._name
					ConnectorMaterial(self.output_file, conn_mat, conn_comp1, conn_comp2).write()
			else:
				# print(f"CONNECTOR SECTION with ELST:{conn_section._name} has no BEHAVIOR keyword. The connector element's behavior is determined by kinematic constraints only.")
				self.connector_materials = ''
				file = open(self.output_file, 'a')

				file.write('*GET,MAT_MAX,MAT,0,NUM,MAX\n')
				file.write('M_ID = MAT_MAX+1\n')
				file.write('MP,DENS,M_ID,0.0\n')
				file.write('\n')
				file.write(f'MAT, M_ID\n')
				file.write('\n')

				file.close()

			ORIENT_1 = conn_section_entities['ORIENT_1']
			ORIENT_2 = conn_section_entities['ORIENT_2']
			ConnectorOrientation(self.output_file, ORIENT_1, ORIENT_2, conn_comp1,  conn_comp2).write()

			ConnectorElement(self.output_file, conn_section, conn_comp1, conn_comp2).write()

class ConnectorElement:
	
	def __init__(self, out_file, conn_section, conn_comp1, conn_comp2) -> None:
		self.base = base
		self.deck = constants.ABAQUS
		self.output_file = out_file
		self.conn_section = conn_section
		self.conn_comp1 = conn_comp1
		self.conn_comp2 = conn_comp2

	def write(self):
		file = open(self.output_file, 'a')
		sec_elems = base.CollectEntities(self.deck, self.conn_section, None)
		comps = ['CARTESIAN', 'CARDAN', 'BUSHING', 'AXIAL']
		if sec_elems:
			file.write('*get,TYPE_MAX,ETYP,0,NUM,MAX\n')
			file.write('ETYP_ID = TYPE_MAX + 1\n')
			file.write('ET,ETYP_ID,184\n')

			if self.conn_comp1 in comps:
				file.write('KEYOPT,E_id+1,1,16          ! General Joint\n')
			
			elif self.conn_comp1 == 'WELD':
				file.write('KEYOPT,E_id+1,1,13          ! Weld Joint\n')

			elif self.conn_comp1 == 'JOIN':
				if self.conn_comp2 == None:
					file.write('KEYOPT,E_id+1,1,0          ! Rigid Link Joint\n')
				elif self.conn_comp2 == 'ALIGN':
					file.write('KEYOPT,E_id+1,1,1          ! Rigid Beam\n')

			elif self.conn_comp1 == 'BEAM':
				file.write('KEYOPT,E_id+1,1,1          ! Rigid Beam\n')

			file.write('\n')
			file.write('TYPE, ETYP_ID\n')
			file.write('\n')

			file.write(f'! element of "*CONNECTOR SECTION, ELSET={self.conn_section._name}".\n')
			for elem in sec_elems:
				nodes = elem.get_entity_values(self.deck,('G1','G2'))
				# print(nodes)
				file.write(f'E,{nodes["G1"]._id},{nodes["G2"]._id}\n')
				# print(f'E,{nodes["G1"]._id},{nodes["G2"]._id}\n')
			
			file.write('\n')
				
		file.close()
		



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
		conn_elast_list = base.NameToEnts("^CONNECTOR ELASTICITY:"+self.material._name+"$")
		if conn_elast_list:
			conn_elast = conn_elast_list[0]
			print(f"Writing connector material NAME: {self.material._name}")
			# print(conn_elast.card_fields(self.deck))
			self.write_connector_elasticity(conn_elast)
			
			# print(f"Writing connector material named TEst {conn_elast._name}")

	def write_connector_elasticity(self, conn_elast):
		# print(conn_elast)
		file = open(self.output_file, 'a')
		file.write(f'! Stiffness Properties : {conn_elast._name} \n')
		comps = ['CARTESIAN', 'CARDAN', 'BUSHING', 'AXIAL']
		if self.conn_comp1 in comps or self.conn_comp2 in comps:
			file.write('*GET,MAT_MAX,MAT,0,NUM,MAX\n')
			file.write('M_ID = MAT_MAX+1\n')

			props = ('NONLINEAR(1)','NONLINEAR(2)','NONLINEAR(3)','NONLINEAR(4)','NONLINEAR(5)','NONLINEAR(6)',)
			# print(conn_elast._name)
			check_linear = conn_elast.get_entity_values(self.deck, props)
			all_linear = True
			if any([True if i == 'YES' else False for i in list(check_linear.values())]):
				all_linear = False
			# print(f'all_linear = {all_linear}')

			if not conn_elast.get_entity_values(self.deck,('COMP',)):
				print(f"*CONNECTOR BEHAVIOR, NAME:{self.material._name} is not processed. \n")
				file.write('MP,DENS,M_ID,0.0\n')
				file.write(f"! *CONNECTOR BEHAVIOR, NAME:{self.material._name} is not processed. \n")

			elif conn_elast.get_entity_values(self.deck,('COMP',))['COMP'] == 'YES':
				comps_ampping = {1:1,2:7,3:12,4:16,5:19,6:21}
				if all_linear:
					file.write('\n')
					file.write('TB,JOIN,M_ID,1,,STIF\n')
				for i in range(1,7):
					props = (f'COMP({i})',f'DEP({i})',f'RIGID({i})',f'NONLINEAR({i})',f'El.Stiff.({i})',f'Freq.({i})',f'Force({i})',f'Rel.Disp.({i})',f'DATA TABLE({i})')
					prop_dict = conn_elast.get_entity_values(self.deck, props)
					if f'DEP({i})' in prop_dict.keys() and  prop_dict[f'DEP({i})'] != 'YES' and f'RIGID({i})' in prop_dict.keys() and prop_dict[f'RIGID({i})'] != 'YES':
						if prop_dict[f'COMP({i})'] == 'YES':
							if prop_dict[f'NONLINEAR({i})'] == 'YES':
								print(f"Nonlinear stiffness without dependent table is not processed. *CONNECTOR ELASTICITY, NAME:{conn_elast._name}.")
							else:
								if all_linear:
									stiff = prop_dict[f'El.Stiff.({i})']
									file.write(f'TBDATA,{comps_ampping[i]},{stiff}\n')
								else:
									stiff = prop_dict[f'El.Stiff.({i})']
									file.write('\n')
									file.write(f'TB,JOIN,M_ID,1,3,JNS{i}\n')
									file.write(f'TBPT,, -1.0,-{stiff} \n')
									file.write(f'TBPT,,0.0,0.0\n')
									file.write(f'TBPT,, 1.0,{stiff}\n')
						else:
							pass
					else:
						if f'DEP({i})' in prop_dict.keys() and prop_dict[f'DEP({i})'] == 'YES':
							if prop_dict[f'NONLINEAR({i})'] == 'YES':
								tbpt_data = ''
								tbpts = 0
								temps = 0
								curr_temp = 0
								curve_data = self.base.GetLoadCurveData(prop_dict[f'DATA TABLE({i})'])
								# print(curve_data)
								for pt in curve_data:
									tbpts += 1
									if len(pt) == 3:
										if curr_temp != pt[2]:
											curr_temp = pt[2]
											temps += 1
											tbpt_data = tbpt_data + '\n'
											tbpt_data = tbpt_data + f'TBTEMP,{curr_temp}\n'
										tbpt_data = tbpt_data + f'TBPT,,{pt[1]},{pt[0]} \n'

									elif len(pt) == 2:
										tbpt_data = tbpt_data + f'TBPT,,{pt[1]},{pt[0]} \n'
								if temps == 0:
									temps = 1
								file.write(f'TB,JOIN,M_ID,{temps},{tbpts},JNS{i}\n')
								file.write(tbpt_data)
							else:
								print(f"Tabular values are given for *CONNECTOR ELASTICITY with NAME:{conn_elast._name}. And this entity is not processed.")

						if f'RIGID({i})' in prop_dict.keys() and prop_dict[f'RIGID({i})'] == 'YES':
							print(f"'RIGID' values are given for *CONNECTOR ELASTICITY with NAME:{conn_elast._name}. And this entity is not processed.")
			else:
				print(f"Matrix values are given for *CONNECTOR ELASTICITY with NAME:{conn_elast._name}. And this entity is not processed.")
			file.write('\n')
			file.write(f'MAT, M_ID\n')
			file.write('\n')
		else:
			print(f'{self.conn_comp1} is not processed for {self.material._name}')

		file.close()


class ConnectorOrientation:
	def __init__(self, out_file, CSYS1, CSYS2, conn_comp1,  conn_comp2) -> None:
		self.base = base
		self.deck = constants.ABAQUS
		self.output_file = out_file
		self.csys_1 = CSYS1
		self.csys_2 = CSYS2
		self.conn_comp1 = conn_comp1
		self.conn_comp2 = conn_comp2

	def write(self):
		general_joint_comps = ['CARTESIAN', 'CARDAN', 'BUSHING', 'AXIAL']

		joint_type = ''
		rdofs = ''
		if self.conn_comp1 in general_joint_comps:
			joint_type = 'gene'
			rdofs = ''

		elif self.conn_comp1 in 'WELD':
			joint_type = 'WELD'
			rdofs = ''

		file = open(self.output_file, 'a')
		file.write('*get,SEC_MAX,SECP,,NUM,MAX\n')	
		file.write('SEC_ID = SEC_MAX + 1\n')		
		file.write(f'sectype,SEC_ID, joint, {joint_type},\n')

		if self.csys_1 != None:
			id_1 = self.get_translated_id(self.csys_1)
			if self.csys_2 == None:
				id_2 = id_1
			else:
				id_2 = self.get_translated_id(self.csys_2)
		elif self.csys_2 != None:
			id_1 = 0
			id_2 = self.get_translated_id(self.csys_2)
		else:		
			id_1 = 0
			id_2 = 0

		file.write(f'SECJOIN,,{id_1},{id_2}\n')
		file.write(f'SECJOIN,RDOF,{rdofs}\n')
		file.close()
	

		file = open(self.output_file, 'a')
		file.write('\n')
		file.write(f'SECNUM, SEC_ID\n')
		file.write('\n')
		file.close()

	def get_translated_id(self, coord):
		coords = base.CollectEntities(self.deck, None, 'ORIENTATION_R')
		c_id  = coord._id
		if c_id > 10:
			csys = c_id
		else:
			if len(coords) > 10:
				csys = c_id + len(coords)
			else:
				csys  = c_id + 10
		return csys

