import os
import string
import ansa
from ansa import base
from ansa import constants
import math


def process_entities(location, connectors=[], fasteners=[]) -> None:
	fastneres_dict = Fasteners().get_fasteners_with_connectors(fasteners=fasteners)
	# aa=ConnectorSections(location, connectors, fastneres_dict).write()
	connector_data = ConnectorSections(location, connectors, fastneres_dict)
	connector_data.write()
	# print(connector_data.all_connectors)
	
class ConnectorSections:

	BASIC_TRANSLATION = ["ACCELEROMETER","AXIAL","CARTESIAN","JOIN","LINK","PROJECTION CARTESIAN","RADIAL-THRUST","SLIDE-PLANE","SLOT"]
	BASIC_ROTATION = ["ALIGN","CARDAN","CONSTANT VELOCITY","EULER","FLEXION-TORSION","PROJECTION FLEXION-TORSION","REVOLUTE","ROTATION","ROTATION-ACCELEROMETER","UNIVERSAL","FLOW-CONVERTER"]
	ASSEMBLED = ["BEAM","BUSHING","CVJOINT","CYLINDRICAL","HINGE","PLANAR","RETRACTOR","TRANSLATOR","UJOINT","WELD","SLIPRING"]

	def __init__(self, out_folder:str, conn_sections:list, fastneres_dict) -> None:
		self.base = base
		self.deck = constants.ABAQUS
		self.output_file_connector = os.path.join(out_folder , 'connectors_only.dat')
		self.output_file_connector_fastener = os.path.join(out_folder , 'connectors_and_fasteners.dat')
		self.conn_sections = conn_sections
		self.fastners = fastneres_dict
		self.connector_materials = ''
		self.out_file_check = ''
		self.all_connectors = []

	def write(self):
		"""
		Write out the all properties (Material, Elemets, and Orientations) reataled to Given Connection Section. 

		"""
		if len(self.conn_sections) != len(self.fastners.keys()):
			self.write_real_id(self.output_file_connector)

		if self.fastners:
			self.write_real_id(self.output_file_connector_fastener)

		for conn_section in self.conn_sections:
			conn_section_entities = conn_section.get_entity_values(self.deck,('MID','COMPONENT_1','COMPONENT_2','ORIENT_1','ORIENT_2' ))
			# print(conn_section.card_fields(self.deck))
			conn_mat = conn_section_entities['MID']
			conn_comp1 = conn_section_entities['COMPONENT_1'].strip()
			conn_comp2 = conn_section_entities['COMPONENT_2'].strip()
			self.all_connectors.append([conn_comp1,conn_comp2])

			conn_ref_length_commnads = ''

			if conn_section._name in self.fastners.keys():
				fastener = self.fastners[conn_section._name]
				write_in_file = self.output_file_connector_fastener
			else:
				fastener = None
				write_in_file = self.output_file_connector

			if write_in_file != self.out_file_check:
				self.out_file_check = write_in_file
				self.connector_materials = None

			if conn_mat != None:
				if conn_mat._name != self.connector_materials:
					# print(conn_mat._name)
					self.connector_materials = conn_mat._name
					ConnectorMaterial(self.out_file_check, conn_mat).write()
				conn_ref_length_commnads = ConnectorConstitutiveReference(conn_mat).get_commands()
				# print(conn_ref_length_commnads)
			else:
				# print(f"CONNECTOR SECTION with ELST:{conn_section._name} has no BEHAVIOR keyword. The connector element's behavior is determined by kinematic constraints only.")
				if self.connector_materials != '':
					self.connector_materials = ''
					file = open(self.out_file_check, 'a')

					file.write('*GET,MAT_MAX,MAT,0,NUM,MAX\n')
					file.write('M_ID = MAT_MAX+1\n')
					file.write('MP,DENS,M_ID,0.0\n')
					file.write('\n')
					file.write(f'MAT, M_ID\n')

					file.close()

			ORIENT_1 = conn_section_entities['ORIENT_1']
			ORIENT_2 = conn_section_entities['ORIENT_2']
			ConnectorOrientation(self.out_file_check, ORIENT_1, ORIENT_2, conn_comp1,  conn_comp2, conn_ref_length_commnads).write()

			ConnectorElement(self.out_file_check, conn_section, conn_comp1, conn_comp2, ORIENT_1, ORIENT_2, fastener).write()

	def write_real_id(self, file_out):
		file = open(file_out, 'w')
		file.write('*GET,REAL_MAX,RCON,0,NUM,MAX\n')
		file.write('R_ID = REAL_MAX + 1\n')
		file.write('R,R_ID\n')
		file.write('\n')
		file.write(f'REAL, R_ID\n')
		file.write('\n')
		file.close()

class ConnectorElement:
	
	def __init__(self, out_file, conn_section, conn_comp1, conn_comp2, ORIENT_1, ORIENT_2, fastener) -> None:
		self.base = base
		self.deck = constants.ABAQUS
		self.out_file_check = out_file
		self.conn_section = conn_section
		self.conn_comp1 = conn_comp1
		self.conn_comp2 = conn_comp2
		self.orient_1 = ORIENT_1
		self.orient_2 = ORIENT_2
		self.fastener = fastener

	def write(self):
		file = open(self.out_file_check, 'a')
		sec_elems = base.CollectEntities(self.deck, self.conn_section, None)
		if sec_elems:
			file.write('*get,TYPE_MAX,ETYP,0,NUM,MAX\n')
			file.write('ETYP_ID = TYPE_MAX + 1\n')
			file.write('ET,ETYP_ID,184\n')

			if self.conn_comp1 in ['CARTESIAN', 'CARDAN', 'EULER', 'ROTATION', 'AXIAL']:
				file.write('KEYOPT,ETYP_ID,1,16           ! General Joint\n')
				if self.conn_comp1 == 'AXIAL':
					file.write('KEYOPT,ETYP_ID,4,1          ! displacement dof are activated\n')

			elif (self.conn_comp1 == 'UJOINT') or (self.conn_comp1 in ['JOIN', 'UNIVERSAL'] and self.conn_comp2 in ['JOIN', 'UNIVERSAL']):
				file.write('KEYOPT,ETYP_ID,1,7           ! Universal Joint\n')

			elif (self.conn_comp1 == 'WELD') or (self.conn_comp1 in ['JOIN', 'ALIGN'] and self.conn_comp2 in ['JOIN', 'ALIGN']):
				file.write('KEYOPT,ETYP_ID,1,13          ! Weld Joint\n')

			elif (self.conn_comp1 == 'HINGE') or (self.conn_comp1 in ['JOIN', 'REVOLUTE'] and self.conn_comp2 in ['JOIN', 'REVOLUTE']):
				file.write('KEYOPT,ETYP_ID,1,6          ! Revolute Joint\n')
				file.write('KEYOPT,ETYP_ID,4,0          ! x-axix revolution\n')
				
			elif (self.conn_comp1 == 'TRANSLATOR ') or (self.conn_comp1 in ['SLOT', 'ALIGN'] and self.conn_comp2 in ['SLOT', 'ALIGN']):
				file.write('KEYOPT,ETYP_ID,1,10          ! Translational Joint\n')

			elif self.conn_comp1 == 'JOIN' and not bool(self.conn_comp2):
				file.write('KEYOPT,ETYP_ID,1,0          ! Rigid Link Joint\n')

			elif self.conn_comp1 == 'BEAM':
				file.write('KEYOPT,ETYP_ID,1,1          ! Rigid Beam\n')
			
			elif (self.conn_comp1 == 'CYLINDRICAL') or (self.conn_comp1 in ['SLOT', 'REVOLUTE'] and self.conn_comp2 in ['SLOT', 'REVOLUTE']):
				file.write('KEYOPT,ETYP_ID,1,11          ! Cylindrical Joint\n')
				file.write('KEYOPT,ETYP_ID,4,0           ! x-axix cylindrical\n')

			elif (self.conn_comp1 == 'PLANAR') or (self.conn_comp1 in ['SLIDE-PLANE', 'REVOLUTE'] and self.conn_comp2 in ['SLIDE-PLANE', 'REVOLUTE']):
				file.write('KEYOPT,ETYP_ID,1,12          ! Planar Joint\n')
				file.write('KEYOPT,ETYP_ID,4,0           ! x-axix planar\n')

			elif self.conn_comp1 == 'ALIGN' and not bool(self.conn_comp2):
				file.write('KEYOPT,ETYP_ID,1,14          ! Orient Joint\n')

			elif (self.conn_comp1 == 'BUSHING') or (self.conn_comp1 in ['PROJECTION CARTESIAN', 'PROJECTION FLEXION-TORSION'] and self.conn_comp2 in ['PROJECTION CARTESIAN', 'PROJECTION FLEXION-TORSION']):
				file.write('KEYOPT,ETYP_ID,1,16          ! General Joint\n')

			else:
				print(f"*CONNECTOR SECTION, ELSET={self.conn_section._name}: Joint Combination of joint type '{self.conn_comp1}' with '{self.conn_comp2}' is not processed. Rigid beam joint is defined")
				file.write('KEYOPT,ETYP_ID,1,1          ! Rigid Beam\n')

			file.write('\n')
			file.write('TYPE, ETYP_ID\n')
			file.write('\n')

			file.write(f'! element of "*CONNECTOR SECTION, ELSET={self.conn_section._name}".\n')


			if self.fastener == None:
				for elem in sec_elems:
					nodes = elem.get_entity_values(self.deck,('G1','G2'))
					file.write(f'E,{nodes["G1"]._id},{nodes["G2"]._id}\n')
			else:
				surf_counter = Fasteners().get_surface_count(self.fastener)
				for j in range(0,len(sec_elems),surf_counter-1):
					nodes = sec_elems[j].get_entity_values(self.deck,('G1','G2'))
					if self.fastener == None:
						file.write(f'E,{nodes["G1"]._id},{nodes["G2"]._id}\n')
					else:
						set_number = f'group_{j}'
						fastener_commands = Fasteners().get_fastener_commnands(self.fastener, nodes, self.orient_1, self.orient_2, sec_elems, set_number)
						file.write(fastener_commands)
				if self.fastener != None:
					file.write('\n')
					file.write('*get,dummy_max,ETYP,0,NUM,MAX\n')
					file.write('ESEL,S,TYPE,,ETYP_ID+1,dummy_max\n')
					file.write('ESEL,R,ENAME,,184\n')
					file.write('emodif,all,type,ETYP_ID\n')
					file.write('emodif,all,secnum,SEC_ID\n')
					file.write('emodif,all,mat,M_ID\n')
					file.write('allsel')
				
				# print(f'E,{nodes["G1"]._id},{nodes["G2"]._id}\n')
			file.write('\n')
				
		file.close()
		

class ConnectorConstitutiveReference:
	
	def __init__(self, material) -> None:
		self.base = base
		self.deck = constants.ABAQUS
		self.material = material

	def get_commands(self):
		conn_consti_refs = base.NameToEnts("^CONNECTOR CONSTITUTIVE REFERENCE:"+self.material._name+"$")
		if conn_consti_refs:
			conn_consti_ref = conn_consti_refs[0]
			props = ('R.Len.1','R.Len.2','R.Len.3','R.Ang.1','R.Ang.2','R.Ang.3',)
			conn_ref_len = conn_consti_ref.get_entity_values(self.deck, props)
			secdata_command = 'SECDATA'
			# print(conn_consti_ref._name)
			# print(conn_ref_len)
			for prop in props:
				if prop in conn_ref_len.keys() and conn_ref_len[prop] != None:
					secdata_command += f',{conn_ref_len[prop]}'
				else:
					secdata_command += ','
		else:
			secdata_command = ''

		return secdata_command

class ConnectorMaterial:
	
	def __init__(self, out_file, material) -> None:
		self.base = base
		self.deck = constants.ABAQUS
		self.out_file_check = out_file
		self.material = material

	def write(self):

		"""
			Write out the all Connector Material properties defined in Connector Behavior. 
		"""

		# Write Connector Elasticity:
		conn_elast_list = base.NameToEnts("^CONNECTOR ELASTICITY:"+self.material._name+"$")
		conn_damping_list = base.NameToEnts("^CONNECTOR DAMPING:"+self.material._name+"$")
		if conn_elast_list or conn_damping_list:
			
			print(f"Writing connector material NAME: {self.material._name}")
			file = open(self.out_file_check, 'a')
			file.write('*GET,MAT_MAX,MAT,0,NUM,MAX\n')
			file.write('M_ID = MAT_MAX+1\n')
			file.close()
			# print(conn_elast.card_fields(self.deck))
			if conn_elast_list:
				conn_elast = conn_elast_list[0]
				self.write_connector_elasticity(conn_elast)
			if conn_damping_list:
				conn_damp = conn_damping_list[0]
				self.write_connector_damping(conn_damp)

			file = open(self.out_file_check, 'a')
			file.write('\n')
			file.write(f'MAT, M_ID\n')
			file.close()
			
			# print(f"Writing connector material named TEst {conn_elast._name}")
	def write_connector_damping(self, conn_damp):
		file = open(self.out_file_check, 'a')
		file.write('\n')
		file.write(f'! Damping Properties : {conn_damp._name} \n')
		props = ('NONLINEAR(1)','NONLINEAR(2)','NONLINEAR(3)','NONLINEAR(4)','NONLINEAR(5)','NONLINEAR(6)',)
		# print(conn_damp._name)
		check_linear = conn_damp.get_entity_values(self.deck, props)
		all_linear = True
		if any([True if i == 'YES' else False for i in list(check_linear.values())]):
			all_linear = False
		# print(f'all_linear = {all_linear}')
		# print(conn_damp.card_fields(self.deck))

		if not conn_damp.get_entity_values(self.deck,('COMP_VISCOUS',)):
			print(f"*CONNECTOR DAMPING of material {self.material._name} is not processed. \n")
			file.write('MP,DENS,M_ID,0.0\n')
			file.write(f"! *CONNECTOR DAMPING of material {self.material._name} is not processed. \n")

		elif conn_damp.get_entity_values(self.deck,('COMP_VISCOUS',))['COMP_VISCOUS'] == 'YES':
			comps_ampping = {1:1,2:7,3:12,4:16,5:19,6:21}
			if all_linear:
				file.write('\n')
				file.write('TB,JOIN,M_ID,1,,DAMP\n')
			for i in range(1,7):
				props = (f'COMP({i})',f'DEP({i})',f'TYPE({i})',f'NONLINEAR({i})',f'Dam.Coef.({i})',f'Freq.({i})',f'Force({i})',f'Rel.Vel.({i})',f'DATA TABLE({i})')
				prop_dict = conn_damp.get_entity_values(self.deck, props)
				if f'DEP({i})' in prop_dict.keys() and  prop_dict[f'DEP({i})'] != 'YES':
					if prop_dict[f'COMP({i})'] == 'YES':
						if prop_dict[f'NONLINEAR({i})'] == 'YES':
							print(f"Nonlinear damping without dependent table is not processed. *CONNECTOR DAMPING, NAME:{conn_damp._name}.")
						else:
							if all_linear:
								damp = prop_dict[f'Dam.Coef.({i})']
								file.write(f'TBDATA,{comps_ampping[i]},{damp}\n')
							else:
								damp = prop_dict[f'Dam.Coef.({i})']
								file.write('\n')
								file.write(f'TB,JOIN,M_ID,1,3,JND{i}\n')
								file.write(f'TBPT,, -1.0,-{damp} \n')
								file.write(f'TBPT,,0.0,0.0\n')
								file.write(f'TBPT,, 1.0,{damp}\n')
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
							file.write(f'TB,JOIN,M_ID,{temps},{tbpts},JND{i}\n')
							file.write(tbpt_data)
						else:
							print(f"Tabular values are given for *CONNECTOR DAMPING with NAME:{conn_damp._name}. And this entity is not processed.")
		else:
			print(f"Matrix values are given for *CONNECTOR DAMPING with NAME:{conn_damp._name}. And this entity is not processed.")


		file.close()

	def write_connector_elasticity(self, conn_elast):
		# print(conn_elast)
		file = open(self.out_file_check, 'a')
		file.write('\n')
		file.write(f'! Stiffness Properties : {conn_elast._name} \n')
		
		props = ('NONLINEAR(1)','NONLINEAR(2)','NONLINEAR(3)','NONLINEAR(4)','NONLINEAR(5)','NONLINEAR(6)',)
		# print(conn_elast._name)
		check_linear = conn_elast.get_entity_values(self.deck, props)
		all_linear = True
		if any([True if i == 'YES' else False for i in list(check_linear.values())]):
			all_linear = False
		# print(f'all_linear = {all_linear}')

		if not conn_elast.get_entity_values(self.deck,('COMP',)):
			print(f"*CONNECTOR ELASTICITY of material {self.material._name} is not processed. \n")
			file.write('MP,DENS,M_ID,0.0\n')
			file.write(f"! *CONNECTOR ELASTICITY of material {self.material._name} is not processed. \n")

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
	

		file.close()


class ConnectorOrientation:
	def __init__(self, out_file, CSYS1, CSYS2, conn_comp1,  conn_comp2, conn_ref_length_commnads) -> None:
		self.base = base
		self.deck = constants.ABAQUS
		self.out_file_check = out_file
		self.csys_1 = CSYS1
		self.csys_2 = CSYS2
		self.conn_comp1 = conn_comp1
		self.conn_comp2 = conn_comp2
		self.conn_ref_length_commnads = conn_ref_length_commnads

	def write(self):

		file = open(self.out_file_check, 'a')
		file.write('\n')
		file.write('*get,SEC_MAX,SECP,,NUM,MAX\n')	
		file.write('SEC_ID = SEC_MAX + 1\n')

		if self.conn_comp1 in ['CARTESIAN', 'CARDAN', 'EULER', 'ROTATION', 'AXIAL']:
			joint_type = 'GENE'
			rdofs = ''
		
		elif (self.conn_comp1 == 'UJOINT') or (self.conn_comp1 in ['JOIN', 'UNIVERSAL'] and self.conn_comp2 in ['JOIN', 'UNIVERSAL']):
			joint_type = 'UNIV'

		elif (self.conn_comp1 == 'WELD') or (self.conn_comp1 in ['JOIN', 'ALIGN'] and self.conn_comp2 in ['JOIN', 'ALIGN']):
			joint_type = 'WELD'

		elif (self.conn_comp1 == 'HINGE') or (self.conn_comp1 in ['JOIN', 'REVOLUTE'] and self.conn_comp2 in ['JOIN', 'REVOLUTE']):
			joint_type = 'REVO'

		elif (self.conn_comp1 == 'TRANSLATOR ') or (self.conn_comp1 in ['SLOT', 'ALIGN'] and self.conn_comp2 in ['SLOT', 'ALIGN']):
			joint_type = 'PRIS'

		elif self.conn_comp1 == 'JOIN' and not bool(self.conn_comp2):
			joint_type = 'LINK'

		elif self.conn_comp1 == 'BEAM':
			joint_type = 'BEAM'
		
		elif (self.conn_comp1 == 'CYLINDRICAL') or (self.conn_comp1 in ['SLOT', 'REVOLUTE'] and self.conn_comp2 in ['SLOT', 'REVOLUTE']):
			joint_type = 'CYLI'

		elif (self.conn_comp1 == 'PLANAR') or (self.conn_comp1 in ['SLIDE-PLANE', 'REVOLUTE'] and self.conn_comp2 in ['SLIDE-PLANE', 'REVOLUTE']):
			joint_type = 'PLAN'

		elif self.conn_comp1 == 'ALIGN' and not bool(self.conn_comp2):
			joint_type = 'ORIE'

		elif (self.conn_comp1 == 'BUSHING') or (self.conn_comp1 in ['PROJECTION CARTESIAN', 'PROJECTION FLEXION-TORSION'] and self.conn_comp2 in ['PROJECTION CARTESIAN', 'PROJECTION FLEXION-TORSION']):
			joint_type = 'GENE'
			rdofs = ''

		else:
			joint_type = 'BEAM'
			print(f"Joint Combination of joint type '{self.conn_comp1}' with '{self.conn_comp2}' is not processed.")


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
		if joint_type != "LINK" and joint_type != 'BEAM':
			file.write(f'sectype,SEC_ID, joint, {joint_type},\n')
			file.write(f'SECJOIN,,{id_1},{id_2}\n')
			if joint_type == 'GENE':
				file.write(f'SECJOIN,RDOF,{rdofs}\n')
			file.write(f'{self.conn_ref_length_commnads}\n')
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




class Fasteners:
	def __init__(self) -> None:
		self.base = base
		self.deck = constants.ABAQUS
	
	def get_fasteners_with_connectors(self, fasteners):
		fastener_dict = {}
		for fastener in fasteners:
			fastener_details = fastener.get_entity_values(self.deck,('ELSET id','connector', 'standalone'))
			# print(fastener_details)
			if fastener_details['connector'] == 'yes':
				if fastener_details['standalone'] == 'no':
					fastener_elset = fastener_details['ELSET id']
					fastener_dict[fastener_elset._name] = fastener
				else:
					fastener_interaction = fastener.get_entity_values(self.deck,('INTERACTION',))['INTERACTION']
					print(f'*FASTENER with INTERACTION NAME:{fastener_interaction._name} is defined with standalone:yes, it is not processed')

			else:
				fastener_interaction = fastener.get_entity_values(self.deck,('INTERACTION',))['INTERACTION']
				if fastener_details['connector'] != 'yes':
					print(f'*FASTENER with INTERACTION NAME:{fastener_interaction._name} is defined with NODE SET, it is not processed')
				if fastener_details['standalone'] != 'no':
					print(f'*FASTENER with INTERACTION NAME:{fastener_interaction._name} is defined with standalone:yes, it is not processed')
		return fastener_dict


	def get_surface_count(self, fastener):
		fast_prop = fastener.get_entity_values(self.deck,tuple(fastener.card_fields(self.deck)))
		surfs = [fast_prop[f'SURF{i}'] for i in range(1,12) if fast_prop[f'SURF{i}'] != None]
		return len(surfs)

	def get_fastener_commnands(self, fastener, nodes, orient_1, orient_2, sec_elems, set_number):
		n1 = nodes['G1']._id
		if nodes['G2']:
			n2 = nodes['G2']._id
		else:
			n2 = ''

		fast_prop = fastener.get_entity_values(self.deck,tuple(fastener.card_fields(self.deck)))
		r_influ = fast_prop['INFLUENCE R']
		r_search = fast_prop['SEARCH R']
		interaction = fast_prop['INTERACTION']
		adjust = fast_prop['ADJUST']
		n_layers = fast_prop['NLAYERS']
		fast_orient = fast_prop['ORIENT']
		surfs = [fast_prop[f'SURF{i}'] for i in range(1,12) if fast_prop[f'SURF{i}'] != None]
		# Converting the surface component to node component
		for surf in surfs:
			set_list  = {'OUTPUT TYPE': 'NODE'}
			surf.set_entity_values(self.deck, set_list)
		fastner_mapdl_string = ''
		fastner_mapdl_string += f'SWGEN,{interaction._name}_{set_number},{r_influ},{surfs[0]._name},{surfs[1]._name},{n1},{n2},{r_search}\n'
		if len(surfs) > 2:
			fastner_mapdl_string += f'SWADD,{interaction._name}_{set_number},{r_search}'
			if len(surfs) > 11:
				for i in range(2,11):
					fastner_mapdl_string += f',{surfs[i]._name}'
				print(f'*FASTENER with INTERACTION NAME:{interaction._name} has more that 11 surfaces in it, only 11 are supported in MAPDL, others are not processed')
			else:
				for i in range(2,len(surfs)):
					fastner_mapdl_string += f',{surfs[i]._name}'
			fastner_mapdl_string += '\n'

		return fastner_mapdl_string