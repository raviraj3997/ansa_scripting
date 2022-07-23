
# PYTHON script
import os
from platform import node
import ansa
from ansa import base
from ansa import constants


class Mapper:
    deck_mapper = {
        'ANSYS': constants.ANSYS,
        'ABAQUS': constants.ABAQUS
    }

    node_mapper = {
        'ANSYS': 'NODE',
        'ABAQUS': 'NODE'
    }
    node_id_mapper = {
        'ANSYS': 'NODE',
        'ABAQUS': 'ID'
    }

    orinet_mapper = {
        'ANSYS': 'NODAL COORD',
        'ABAQUS': 'TRANSFORM'
    }

    ref_coordnite_sys_mapper = {
        'ANSYS': 'CSYS',
        'ABAQUS': 'SYSTEM'
    }

    component_name = {
        'ANSYS': 'Name',
        'ABAQUS': 'Name'
    }

    component_output_type = {
        'ANSYS': {
            'ELEMENT':'ELEMENT',
            'NODE': 'NODE',
            'NAME': 'Name',
            'SET': 'SET',
            'out_type': 'OUTPUT TYPE',
        },
        'ABAQUS': {
            'ELEMENT':'ELSET',
            'NODE':'NSET',
            'NAME': 'Name',
            'SET': 'SET',
            'out_type': 'OUTPUT TYPE',
        },
    }
    

    coupling = {
        'ABAQUS': {
            'ref_node': 'REF NODE',
            'coup_ori': 'ORIENT',
            'nd_list': 'G',
            'comp_list': 'C'
        }
    }

class Node:
    def __init__(self, deck: str) -> None:
        self.deck = deck
        self.deck_object = Mapper.deck_mapper[deck]

    def change_orientation(self, node, coordinate_system):
        set_list  = {Mapper.orinet_mapper[self.deck]: coordinate_system}
        node.set_entity_values(self.deck_object, set_list)

    def change_reference_coordinate_system(self, node, coordinate_system):
        set_list  = {Mapper.ref_coordnite_sys_mapper[self.deck]: coordinate_system}
        node.set_entity_values(self.deck_object, set_list)

    def change_location(self, node, new_location: list):
        set_list  = {
            'X': new_location[0],
            'Y': new_location[1],
            'Z': new_location[2],
        }
        node.set_entity_values(self.deck_object, set_list)

    def create_node(self, id=None, location=[0.0,0.0,0.0], reference_coordinate_system=None, orientation_coordinate_system=None):
        variables_list = {
            'X': location[0],
            'Y': location[1],
            'Z': location[2],
            Mapper.ref_coordnite_sys_mapper[self.deck]: reference_coordinate_system,
            Mapper.orinet_mapper[self.deck]: orientation_coordinate_system,
        }
        if id != None:
            variables_list[Mapper.node_id_mapper[self.deck]] = id

        node = base.CreateEntity(self.deck_object, Mapper.node_mapper[self.deck], variables_list) 
        return node


    
class Set:
    def __init__(self, deck: str) -> None:
        self.deck = deck
        self.deck_object = Mapper.deck_mapper[deck]


    def create_nodal_set(self, name: str, nodes:list):
        variables_list = {Mapper.component_output_type[self.deck]['NAME']: name, Mapper.component_output_type[self.deck]['out_type']: Mapper.component_output_type[self.deck]['NODE']}
        set = base.CreateEntity(self.deck_object, Mapper.component_output_type[self.deck]['SET'], variables_list) 
        base.AddToSet(set, nodes)
        return set


    def create_element_set(self, name: str, elements:list):
        variables_list = {Mapper.component_output_type[self.deck]['NAME']: name, Mapper.component_output_type[self.deck]['out_type']: Mapper.component_output_type[self.deck]['NODE']}
        set = base.CreateEntity(self.deck_object, Mapper.component_output_type[self.deck]['SET'], variables_list) 
        base.AddToSet(set, elements)
        return set


class ConnectorMaterial:
    def __init__(self) -> None:
        self.base = base
        self.deck_object = None
        self.properties = {}
        self.prop_mapping= {
            '*ELASTICITY':{
                'function':self.read_elsticity,
                'entity': 'EL>data'
            },
            '*DAMPING':{
                'function':self.read_damping,
                'entity': 'D>data'
            },
            '*CONSTITUTIVE REFERENCE':{
                'function':self.read_constitutive_ref_len,
                'entity': 'CNRF>data'
            },
            '*STOP':{
                'function':self.read_stops,
                'entity': 'STP>data'
            },
            '*PLASTICITY':{
                'function':self.read_plasticity,
                'entity': 'STP>data'
            },

        }

    def read_material_properties(self, material, deck: str):
        
        print(f'! Material Properties : {material._name}')
        if deck != 'ABAQUS':
            print(f'Material properties of the {deck} deck are not processed. use "ABAQUS" deck')
            available_fields = []
        else:
            self.deck_object = Mapper.deck_mapper[deck]
            fields = material.card_fields(self.deck_object)
            field_vals = material.get_entity_values(self.deck_object,(fields))

            available_fields = [field for field in field_vals.keys() if field_vals[field] == 'YES']

        for field in available_fields:
            # if field in ['*ELASTICITY','*DAMPING','*PLASTICITY','*STOP','*CONSTITUTIVE REFERENCE']:
            if field in ['*ELASTICITY','*DAMPING', '*CONSTITUTIVE REFERENCE']:
                function = self.prop_mapping[field]['function']
                self.properties[field] = function(field_vals[self.prop_mapping[field]['entity']])
                # print(self.properties[field])

            elif field != 'DEFINED':
                print(f"for connector material '{material._name}' field {field} is not processed")

            else:
                pass

        return self.properties

    def read_elsticity(self, entity):
        # print(f'! Stiffness Properties : {entity._name}')
        out_rpop = {}

        props = ('NONLINEAR(1)','NONLINEAR(2)','NONLINEAR(3)','NONLINEAR(4)','NONLINEAR(5)','NONLINEAR(6)',)

        check_linear = entity.get_entity_values(self.deck_object, props)
        all_linear = True
        if any([True if i == 'YES' else False for i in list(check_linear.values())]):
            all_linear = False

        out_rpop['linear'] = all_linear
        if entity.get_entity_values(self.deck_object,('COMP',))['COMP'] == 'YES':
            for i in range(1,7):
                props = (f'COMP({i})',f'DEP({i})',f'RIGID({i})',f'NONLINEAR({i})',f'El.Stiff.({i})',f'Freq.({i})',f'Force({i})',f'Rel.Disp.({i})',f'DATA TABLE({i})')
                prop_dict = entity.get_entity_values(self.deck_object, props)
                if prop_dict[f'COMP({i})'] != 'YES':
                    data = None

                elif f'DEP({i})' in prop_dict.keys() and  prop_dict[f'DEP({i})'] != 'YES' and f'RIGID({i})' in prop_dict.keys() and prop_dict[f'RIGID({i})'] != 'YES':
                    if prop_dict[f'NONLINEAR({i})'] == 'YES':
                        data = None
                        print(f"Nonlinear stiffness without dependent table is not processed. *CONNECTOR ELASTICITY, NAME:{entity._name}.")
                    else:
                        if all_linear:
                            data = prop_dict[f'El.Stiff.({i})']
                        else:
                            stiff = prop_dict[f'El.Stiff.({i})']
                            data = [[-stiff,-1,0],[0,0,0],[stiff,1,0]]
                else:
                    if f'DEP({i})' in prop_dict.keys() and prop_dict[f'DEP({i})'] == 'YES':
                        if prop_dict[f'NONLINEAR({i})'] == 'YES':
                            data = self.base.GetLoadCurveData(prop_dict[f'DATA TABLE({i})'])
                        else:
                            data = None
                            print(f"Linear tabular values are given for *CONNECTOR ELASTICITY with NAME:{entity._name}. And this entity is not processed.")
                    if f'RIGID({i})' in prop_dict.keys() and prop_dict[f'RIGID({i})'] == 'YES':
                        data = None
                        print(f"'RIGID' values are given for *CONNECTOR ELASTICITY with NAME:{entity._name}. And this entity is not processed.")

                out_rpop[f'component{i}'] = data
        else:
            print(f"Matrix values are given for *CONNECTOR ELASTICITY with NAME:{entity._name}. And this entity is not processed.")

        return out_rpop


    def read_damping(self, entity):
        out_rpop = {}
        # print(f'! Damping Properties : {entity._name}'
        props = ('NONLINEAR(1)','NONLINEAR(2)','NONLINEAR(3)','NONLINEAR(4)','NONLINEAR(5)','NONLINEAR(6)',)
        check_linear = entity.get_entity_values(self.deck_object, props)
        all_linear = True
        if any([True if i == 'YES' else False for i in list(check_linear.values())]):
            all_linear = False

        out_rpop['linear'] = all_linear
        if entity.get_entity_values(self.deck_object,('COMP_VISCOUS',))['COMP_VISCOUS'] == 'YES':
            for i in range(1,7):
                props = (f'COMP({i})',f'DEP({i})',f'TYPE({i})',f'NONLINEAR({i})',f'Dam.Coef.({i})',f'Freq.({i})',f'Force({i})',f'Rel.Vel.({i})',f'DATA TABLE({i})')
                prop_dict = entity.get_entity_values(self.deck_object, props)

                if prop_dict[f'COMP({i})'] != 'YES':
                    data = None

                elif f'DEP({i})' in prop_dict.keys() and  prop_dict[f'DEP({i})'] != 'YES':
                    if prop_dict[f'NONLINEAR({i})'] == 'YES':
                        data = None
                        print(f"Nonlinear damping without dependent table is not processed. *CONNECTOR DAMPING, NAME:{entity._name}.")
                    else:
                        if all_linear:
                            data = prop_dict[f'Dam.Coef.({i})']
                        else:
                            damp = prop_dict[f'Dam.Coef.({i})']
                            data = [[-damp,-1,0],[0,0,0],[damp,1,0]]
                else:
                    if f'DEP({i})' in prop_dict.keys() and prop_dict[f'DEP({i})'] == 'YES':
                        if prop_dict[f'NONLINEAR({i})'] == 'YES':
                            data = self.base.GetLoadCurveData(prop_dict[f'DATA TABLE({i})'])
                        else:
                            data = None
                            print(f"Linear tabular values are given for *CONNECTOR DAMPING with NAME:{entity._name}. And this entity is not processed.")
                out_rpop[f'component{i}'] = data
        else:
            print(f"Matrix values are given for *CONNECTOR DAMPING with NAME:{entity._name}. And this entity is not processed.")

        return out_rpop


    def read_constitutive_ref_len(self, entity):
        props = ('R.Len.1','R.Len.2','R.Len.3','R.Ang.1','R.Ang.2','R.Ang.3',)
        conn_ref_len = entity.get_entity_values(self.deck_object, props)

        return conn_ref_len

    def read_stops(self):
        pass

    def read_plasticity(self):
        pass

    def read_potential(self):
        pass

    def read_hardening(self):
        pass
    
    def read_damage(self):
        pass

    def read_derived_comp(self):
        pass

    def read_motion(self):
        pass

    def read_friction(self):
        pass

    def read_locks(self):
        pass


    def define_ansys_material_model(self, props, Name):
        self.deck_object = constants.ANSYS
        field_vals = {'EX':'EX', 'EX_val':0.001, 'Name':Name, 'DEFINED':'YES'}
        mat = base.CreateEntity(self.deck_object, 'USER DEFINE', fields = field_vals)

        return mat


    def write_ansys_mapdl_commands(self, material, out_file, mat_id):

        """
            Write out the all Connector Material properties defined in Connector Behavior. 
        """

        # Write Connector Elasticity:
        conn_elast_list = material.get_entity_values(constants.ABAQUS, ('*ELASTICITY',))['*ELASTICITY']
        conn_damping_list = material.get_entity_values(constants.ABAQUS, ('*DAMPING',))['*DAMPING']
        if conn_elast_list=='YES' or conn_damping_list == "YES":
            
            print(f"Writing connector material NAME: {material._name}")
            file = open(out_file, 'a')
            file.write(f'M_ID = {mat_id}\n')
            file.close()
            # print(conn_elast.card_fields(constants.ABAQUS))
            if conn_elast_list=='YES':
                conn_elast = material.get_entity_values(constants.ABAQUS, ('EL>data',))['EL>data'] 
                self.write_connector_elasticity(conn_elast, material, out_file)
            if conn_damping_list == "YES":
                conn_damp = material.get_entity_values(constants.ABAQUS, ('D>data',))['D>data']
                self.write_connector_damping(conn_damp, material, out_file)

            file = open(out_file, 'a')
            file.write('\n')
            file.close()
            
            # print(f"Writing connector material named TEst {conn_elast._name}")
    def write_connector_damping(self, conn_damp, material, out_file):
        file = open(out_file, 'a')
        file.write('\n')
        file.write(f'! Damping Properties : {conn_damp._name} \n')
        props = ('NONLINEAR(1)','NONLINEAR(2)','NONLINEAR(3)','NONLINEAR(4)','NONLINEAR(5)','NONLINEAR(6)',)
        # print(conn_damp._name)
        check_linear = conn_damp.get_entity_values(constants.ABAQUS, props)
        all_linear = True
        if any([True if i == 'YES' else False for i in list(check_linear.values())]):
            all_linear = False
        # print(f'all_linear = {all_linear}')
        # print(conn_damp.card_fields(constants.ABAQUS))

        if not conn_damp.get_entity_values(constants.ABAQUS,('COMP_VISCOUS',)):
            print(f"*CONNECTOR DAMPING of material {material._name} is not processed. \n")
            file.write('MP,DENS,M_ID,0.0\n')
            file.write(f"! *CONNECTOR DAMPING of material {material._name} is not processed. \n")

        elif conn_damp.get_entity_values(constants.ABAQUS,('COMP_VISCOUS',))['COMP_VISCOUS'] == 'YES':
            comps_ampping = {1:1,2:7,3:12,4:16,5:19,6:21}
            if all_linear:
                file.write('\n')
                file.write('TB,JOIN,M_ID,1,,DAMP\n')
            for i in range(1,7):
                props = (f'COMP({i})',f'DEP({i})',f'TYPE({i})',f'NONLINEAR({i})',f'Dam.Coef.({i})',f'Freq.({i})',f'Force({i})',f'Rel.Vel.({i})',f'DATA TABLE({i})')
                prop_dict = conn_damp.get_entity_values(constants.ABAQUS, props)
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
                            curve_data = base.GetLoadCurveData(prop_dict[f'DATA TABLE({i})'])
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

    def write_connector_elasticity(self, conn_elast, material, out_file):
        # print(conn_elast)
        file = open(out_file, 'a')
        file.write('\n')
        file.write(f'! Stiffness Properties : {conn_elast._name} \n')
        
        props = ('NONLINEAR(1)','NONLINEAR(2)','NONLINEAR(3)','NONLINEAR(4)','NONLINEAR(5)','NONLINEAR(6)',)
        # print(conn_elast._name)
        check_linear = conn_elast.get_entity_values(constants.ABAQUS, props)
        all_linear = True
        if any([True if i == 'YES' else False for i in list(check_linear.values())]):
            all_linear = False
        # print(f'all_linear = {all_linear}')

        if not conn_elast.get_entity_values(constants.ABAQUS,('COMP',)):
            print(f"*CONNECTOR ELASTICITY of material {material._name} is not processed. \n")
            file.write('MP,DENS,M_ID,0.0\n')
            file.write(f"! *CONNECTOR ELASTICITY of material {material._name} is not processed. \n")

        elif conn_elast.get_entity_values(constants.ABAQUS,('COMP',))['COMP'] == 'YES':
            comps_ampping = {1:1,2:7,3:12,4:16,5:19,6:21}
            if all_linear:
                file.write('\n')
                file.write('TB,JOIN,M_ID,1,,STIF\n')
            for i in range(1,7):
                props = (f'COMP({i})',f'DEP({i})',f'RIGID({i})',f'NONLINEAR({i})',f'El.Stiff.({i})',f'Freq.({i})',f'Force({i})',f'Rel.Disp.({i})',f'DATA TABLE({i})')
                prop_dict = conn_elast.get_entity_values(constants.ABAQUS, props)
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
                            curve_data = base.GetLoadCurveData(prop_dict[f'DATA TABLE({i})'])
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