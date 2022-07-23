import os
import re
import string
from typing import Set
import ansa
from ansa import base
from ansa import constants
import general_defs

import importlib
importlib.reload(general_defs)


def process_entities(connectors=[], fasteners=[]) -> None:
	# deleting the items
	conn_list = ['CONNECTOR', 'CONNECTOR_SECTION', 'CONNECTOR BEHAVIOR', 'CONNECTOR_ELASTICITY', 'CONNECTOR_DAMPING', 'CONNECTOR_STOP', 'CONNECTOR_CONSTITUTIVE_REFERENCE', 'CONNECTOR_MOTION', 'CONNECTOR_PLASTICITY', 'CONNECTOR_FRICTION']
	delete_entities=[]
	for item in conn_list:
		delete_entities.append(base.CollectEntities(constants.ABAQUS, None, item))

	fastneres_dict = Fasteners().get_fasteners_with_connectors(fasteners=fasteners)
	connector_data = ConnectorSections(conn_sections = connectors, fastneres_dict=fastneres_dict)
	connector_data.write()


	# deleting the items
	# conn_list = ['CONNECTOR', 'CONNECTOR_SECTION', 'CONNECTOR BEHAVIOR', 'CONNECTOR_ELASTICITY', 'CONNECTOR_DAMPING', 'CONNECTOR_STOP', 'CONNECTOR_CONSTITUTIVE_REFERENCE', 'CONNECTOR_MOTION', 'CONNECTOR_PLASTICITY', 'CONNECTOR_FRICTION']
	for entity in delete_entities:
		base.DeleteEntity(entity, False, False)

	base.DeleteEntity(fasteners, False, False)
	fast_property = base.CollectEntities(constants.ABAQUS, None, 'FASTENER_PROPERTY')
	base.DeleteEntity(fast_property, True, True)
	fast_interaction_out = base.CollectEntities(constants.ABAQUS, None, 'INTERACTION_OUTPUT')
	base.DeleteEntity(fast_interaction_out, True, True)
	# print(connector_data.all_connectors)
	
class ConnectorSections:

	def __init__(self, conn_sections:list, fastneres_dict) -> None:
		self.base = base
		self.deck = constants.ABAQUS
		
		self.conn_sections = conn_sections
		self.fastners = fastneres_dict
		self.global_orient = None
		# self.all_connectors = []

	def write(self):
		"""
		Write out the all properties (Material, Elemets, and Orientations) reataled to Given Connection Section. 

		"""
		joint_materials_dict = {}
		joint_materials_props = {}
		out_file = os.path.join(os.getcwd(),'connector_materials.dat')
		file = open(out_file, 'w')
		file.close()
		# count = 0
		for conn_section in self.conn_sections:
			conn_section_entities = conn_section.get_entity_values(self.deck,('MID','COMPONENT_1','COMPONENT_2','ORIENT_1','ORIENT_2' ))
			conn_mat = conn_section_entities['MID']
			conn_comp1 = conn_section_entities['COMPONENT_1'].strip()
			conn_comp2 = conn_section_entities['COMPONENT_2'].strip()

			ORIENT_1 = conn_section_entities['ORIENT_1']
			ORIENT_2 = conn_section_entities['ORIENT_2']

			# print([conn_comp1, conn_comp2])
			# self.all_connectors.append([conn_comp1,conn_comp2])
			# count+=1
			# print(count)
			if conn_mat != None:
				if conn_mat._name not in joint_materials_dict.keys():
					mat = general_defs.ConnectorMaterial()
					mat_props = mat.read_material_properties(material=conn_mat, deck='ABAQUS')
					mat_object = mat.define_ansys_material_model(props = mat_props, Name=conn_mat._name)
					mat.write_ansys_mapdl_commands(conn_mat,out_file, mat_id = mat_object._id)
					joint_materials_dict[conn_mat._name] = mat_object
					joint_materials_props[conn_mat._name] = mat_props
				else:
					mat_object = joint_materials_dict[conn_mat._name]
					mat_props = joint_materials_props[conn_mat._name]
				# print(f'MAterial for conn section {conn_mat._name}')
			else:
				mat_object = None
				mat_props = {}
	
			sec_elems = base.CollectEntities(constants.ANSYS, conn_section, None)
			sec_elems.sort(key=lambda x: x._id)

			if conn_section._name in self.fastners.keys():
				fastener_obj = self.fastners[conn_section._name]
			else:
				fastener_obj = None

			if fastener_obj == None:
				section_joint = self.create_ansys_section_joint(conn_comp1, conn_comp2, conn_section, mat_object, mat_props, ORIENT_1, ORIENT_2)
				for el in sec_elems:
					nodes = el.get_entity_values(self.deck,('G1','G2'))
					base.CreateEntity(constants.ANSYS, 'JOINT', fields = {'I':nodes['G1'],'J':nodes['G2'], 'PID':section_joint})
				# pass
			else:
				surf_counter = Fasteners().get_surfaces_count(fastener_obj)
				mpc_nodes =  base.GetFastenerMPCNodes(fastener_obj)
				for j in range(0,len(sec_elems),surf_counter-1):
					all_nodes = []
					el_nodes = sec_elems[j].get_entity_values(constants.ABAQUS,('G1','G2'))
					all_nodes.append(el_nodes['G1'])
					all_nodes.append(el_nodes['G2'])
					
					for jj in range(1, surf_counter-1):
						el_nodes = sec_elems[j+jj].get_entity_values(constants.ABAQUS,('G2',))
						all_nodes.append(el_nodes['G2'])

					direction, element = self.get_nearest_element_and_normal(all_nodes[0], fastener_obj)
					orient = self.create_local_for_joint(element)
					section_joint = self.create_ansys_section_joint(conn_comp1, conn_comp2, conn_section, mat_object, mat_props, orient, orient)

					self.project_and_modify_node(all_nodes, fastener_obj, direction)

					if all_nodes[0] not in mpc_nodes.keys():
						print(f'the mpc for the fastener may have error, please check before solve Fastener ID:{fastener_obj._id}')

					for kk in range(0, len(all_nodes)-1):
						base.CreateEntity(constants.ANSYS, 'JOINT', fields = {'I':all_nodes[kk],'J':all_nodes[kk+1], 'PID':section_joint})
					
					surface_nodes = mpc_nodes[all_nodes[0]]
					for grp_num in range(len(all_nodes)):
						mpc_pilot = all_nodes[grp_num]
						pilot_set = general_defs.Set('ANSYS').create_nodal_set(name=f"fastner_mpc_pilot_{mpc_pilot._id}", nodes= [mpc_pilot])
						mpc_surf_nodes = surface_nodes[grp_num]
						pinball = fastener_obj.get_entity_values(constants.ABAQUS,('INFLUENCE R',))['INFLUENCE R']
						surf_node_set = general_defs.Set('ANSYS').create_nodal_set(name=f"fastner_mpc_conta_{len(mpc_surf_nodes)}_{mpc_pilot._id}", nodes= mpc_surf_nodes)
						self.create_contact(mpc_pilot, '123456', pilot_set, surf_node_set, pinball)

	def project_and_modify_node(self, all_nodes, fastener_obj, vec):
		search_rad = fastener_obj.get_entity_values(constants.ABAQUS,('SEARCH R',))['SEARCH R']
		faces = Fasteners().get_surfaces(fastener_obj)
		projections = []
		lengths = []
		if len(faces) == len(all_nodes):
			for i, face in enumerate(faces):
				n_loc = all_nodes[0].get_entity_values(constants.ANSYS,('X','Y', 'Z'))
				elems = base.CollectEntities(constants.ANSYS, face, "SHELL", recursive=True)
				projection = base.ProjectPointDirectional(elems, n_loc['X'], n_loc['Y'], n_loc['Z'], vec[0], vec[1], vec[2], float(search_rad), project_on="elements")
				if projection == None:
					print(f'For fastener ID:{fastener_obj._id}, projection point was not found, check the joints.')
				projections.append(projection)
				all_nodes[i].set_entity_values(constants.ANSYS,{'X':projection[0],'Y':projection[1], 'Z':projection[2]})

		else:
			print(f'For fastener ID:{fastener_obj._id}, numebr of surfaces are not equal to number of nodes')

	def create_local_for_joint(self,element):
		nodes = base.CollectEntities(constants.ANSYS, element, 'NODE')
		vals = {'N1': nodes[0],'N2': nodes[1],'N3': nodes[2]}
		orient = base.CreateEntity(constants.ANSYS, "LOCAL_NODES_DYN", vals)
		return orient

	def get_nearest_element_and_normal(self, node, fastener_obj):
		n_loc = node.get_entity_values(constants.ANSYS,('X','Y','Z'))
		coords = (n_loc['X'], n_loc['Y'], n_loc['Z'])
		ents = Fasteners().get_surfaces(fastener_obj)
		shells= base.NearestShell(coordinates=coords, tolerance=500, search_entities=ents)
		shell = shells[0]
		vec = base.GetNormalVectorOfShell(shell)
		return vec, shell

	def create_contact(self, ref_node, dofs, ref_set, cont_set, pinball):
		# Below two lines are not generic
		variables_list = {'CONTA': 'CONTA175','CSID':cont_set, 'TSID':ref_set, 'PILOT NODE': ref_node._id, 'CNT_KEYOPT(12)':5, 'CNT_KEYOPT(4)':0, 'CNT_KEYOPT(2)':2, 'TRG_KEYOPT(2)':1, 'TRG_KEYOPT(4)':dofs}
		if pinball != None:
			variables_list['PINB'] = pinball
		base.CreateEntity(constants.ANSYS, 'CONTACT', variables_list) 


	def create_ansys_section_joint(self, conn_comp1, conn_comp2, conn_section, mat_object, mat_props, ORIENT_1, ORIENT_2):
		# print(conn_section._name)
		# print(conn_comp1)
		if conn_comp1 in ['CARTESIAN', 'CARDAN', 'EULER', 'ROTATION', 'AXIAL']:
			field_vals = {'Subtype':'General'}

		elif (conn_comp1 == 'UJOINT') or (conn_comp1 in ['JOIN', 'UNIVERSAL'] and conn_comp2 in ['JOIN', 'UNIVERSAL']):
			field_vals = {'Subtype':'Universal'}

		elif (conn_comp1 == 'WELD') or (conn_comp1 in ['JOIN', 'ALIGN'] and conn_comp2 in ['JOIN', 'ALIGN']):
			field_vals = {'Subtype':'Weld'}

		elif (conn_comp1 == 'HINGE') or (conn_comp1 in ['JOIN', 'REVOLUTE'] and conn_comp2 in ['JOIN', 'REVOLUTE']):
			field_vals = {'Subtype':'Revolute'}
			
		elif (conn_comp1 == 'TRANSLATOR') or (conn_comp1 in ['SLOT', 'ALIGN'] and conn_comp2 in ['SLOT', 'ALIGN']):
			field_vals = {'Subtype':'Translational'}

		elif conn_comp1 == 'JOIN' and not bool(conn_comp2):
			field_vals = {'Subtype':'Spherical'}

		# elif conn_comp1 == 'BEAM':
		# 	field_vals = {'Subtype':'Beam'}
		
		# elif (conn_comp1 == 'CYLINDRICAL') or (conn_comp1 in ['SLOT', 'REVOLUTE'] and conn_comp2 in ['SLOT', 'REVOLUTE']):
		# 	field_vals = {'Subtype':'Cylindrical'}

		# elif (conn_comp1 == 'PLANAR') or (conn_comp1 in ['SLIDE-PLANE', 'REVOLUTE'] and conn_comp2 in ['SLIDE-PLANE', 'REVOLUTE']):
		# 	field_vals = {'Subtype':'Planar'}

		# elif conn_comp1 == 'ALIGN' and not bool(conn_comp2):
		# 	field_vals = {'Subtype':'Orinet'}

		# elif (conn_comp1 == 'BUSHING') or (conn_comp1 in ['PROJECTION CARTESIAN', 'PROJECTION FLEXION-TORSION'] and conn_comp2 in ['PROJECTION CARTESIAN', 'PROJECTION FLEXION-TORSION']):
		# 	field_vals = {'Subtype':'General'}
		else:
			print(f"*CONNECTOR SECTION, ELSET={conn_section._name}: Joint Combination of joint type '{conn_comp1}' with '{conn_comp2}' is not processed. Rigid beam joint is defined")
			field_vals = {'Subtype':'Beam'}
		
		if mat_object != None:
			field_vals['MID'] = mat_object

		if "*CONSTITUTIVE REFERENCE" in mat_props.keys():
			r_lens = {f'length{i}':mat_props['*CONSTITUTIVE REFERENCE'][f'R.Len.{i}'] for i in range(1,4) if mat_props['*CONSTITUTIVE REFERENCE'][f'R.Len.{i}'] != None }
			r_angs = {f'angle1{i}':mat_props['*CONSTITUTIVE REFERENCE'][f'R.Ang.{i}'] for i in range(1,4) if mat_props['*CONSTITUTIVE REFERENCE'][f'R.Ang.{i}'] != None }

			for key, val in r_lens.items():
				field_vals[key] = val
			for key, val in r_angs.items():
				field_vals[key] = val

		if ORIENT_1 != None:
			field_vals['LSYS(I)'] = ORIENT_1
		else:
			if self.global_orient == None:
				variables_list = {'Name': 'GLOBAL_ORIENTATION_connectors','A1':0,'A2':0,'A3':0,'B1':0,'B2':0,'B3':1,'C1':1,'C2':0,'C3':0,}
				self.global_orient = base.CreateEntity(constants.ANSYS, 'LOCAL_R', variables_list) 
			field_vals['LSYS(I)'] = self.global_orient

		if ORIENT_2 != None:
			field_vals['LSYS(J)'] = ORIENT_2

		# print(field_vals)
		section_joint = base.CreateEntity(constants.ANSYS, 'SECTION_JOINT', fields = field_vals)
		# print(section_joint)
		
		field_vals ={ 'Name': f'fastnere_connector_joint_section_{section_joint._id}'}
		section_joint.set_entity_values(constants.ANSYS, field_vals)
		return section_joint
		

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


	def get_surfaces(self, fastener):
		fast_prop = fastener.get_entity_values(self.deck,tuple(fastener.card_fields(self.deck)))
		surfs = [fast_prop[f'SURF{i}'] for i in range(1,12) if fast_prop[f'SURF{i}'] != None]
		return surfs

	def get_surfaces_count(self, fastener):
		return len(self.get_surfaces(fastener))

