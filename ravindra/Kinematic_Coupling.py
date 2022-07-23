
# PYTHON script
import os
from platform import node
import ansa
from ansa import base
from ansa import constants
from general_defs import Mapper, Node, Set


def convert_kinematic_cupling(source_deck:str, target_deck:str, element_to_write:str):
    """
    :source_deck: 'ABAQUS'
    :target_deck: 'ANSYS'
    :element_to_write: CONTACT/JOINT
    
    """
    k_coup = base.CollectEntities(Mapper.deck_mapper[source_deck], None, 'KINEMATIC COUPLING')    
    coupling_object = KinematicCoupling()
    elem = coupling_object.create_equivalent_ansys_element(k_coup, source_deck=source_deck,target_deck=target_deck,  target_element = element_to_write)
    # update_object.create_contact_for_kinupdate_ematic_coupling(k_coup, source_deck=source_deck,target_deck=target_deck)
    # update_object.create_contact_for_kinematic_coupling(k_coup: list, source_deck:str, target_deck:str)
    base.DeleteEntity(k_coup, True, True)
    
    


class KinematicCoupling:
    def __init__(self) -> None:
        self.source_deck = ''
        self.source_deck_object = None
        self.target_deck = ''
        self.target_deck_object = None
        self.global_orient = None

    
    def create_equivalent_ansys_element(self, kinematic_couplings:list, source_deck:str, target_deck:str, target_element: str):
        
        self.source_deck = source_deck
        self.source_deck_object = Mapper.deck_mapper[source_deck]
        self.target_deck = target_deck
        self.target_deck_object = Mapper.deck_mapper[target_deck]

        if self.source_deck != 'ABAQUS' or self.target_deck != 'ANSYS':
            print('This functionality is only supported for ABAQUS to ANSYS translation.')
            return

        for coupling in kinematic_couplings:
            
            ref_node, nodes, dofs, orient = self.get_coupling_properties(coupling)
            if len(nodes)>1:
                print("There are more than one node in kinematic coupling, so equivlanet conatc element is created regardless of the target element type provided.")
                ref_set = Set(self.target_deck).create_nodal_set(name=f'KIN_COUPLING_REF_SET_{coupling._id}',nodes=[ref_node])
                cont_set = Set(self.target_deck).create_nodal_set(name=f'KIN_COUPLING_CONT_SET_{coupling._id}',nodes=nodes)
                self.create_contact(ref_node, nodes, dofs, orient, ref_set, cont_set)
            
            elif target_element == 'CONTACT':
                ref_set = Set(self.target_deck).create_nodal_set(name=f'KIN_COUPLING_REF_SET_{coupling._id}',nodes=[ref_node])
                cont_set = Set(self.target_deck).create_nodal_set(name=f'KIN_COUPLING_CONT_SET_{coupling._id}',nodes=nodes)
                self.create_contact(ref_node, nodes, dofs, orient, ref_set, cont_set)
            
            elif target_element == 'JOINT':
                self.create_joint(ref_node, nodes, dofs, orient)

            else:
                print('only Joint and Contact elements are supported as equivalent elements for Kinematic coupling.')
                

    def create_contact(self, ref_node, nodes, dofs, orient, ref_set, cont_set):
        # Below two lines are not generic
        variables_list = {'CONTA': 'CONTA175','CSID':cont_set, 'TSID':ref_set, 'PILOT NODE': ref_node._id, 'CNT_KEYOPT(12)':5, 'CNT_KEYOPT(4)':0, 'CNT_KEYOPT(2)':2, 'TRG_KEYOPT(2)':1, 'TRG_KEYOPT(4)':dofs[0]}
        base.CreateEntity(self.target_deck_object, 'CONTACT', variables_list) 

        # # modify_node
        nodes.append(ref_node)

        for node in nodes:
            n = Node(self.target_deck)
            n.change_orientation(node,orient)
         

    def create_joint(self, ref_node, nodes, dofs, orient):
        
        dof_mapping = {
            '1':'UX',
            '2':'UY',
            '3':'UZ',
            '4':'RX',
            '5':'RY',
            '6':'RZ'
        }
        variables_list = {'Subtype':'General', 'LSYS(I)':orient, 'LSYS(J)':orient, 'KEYOPT(4)': '    0'}
        for dof in str(dofs[0]):
            # print(dof)
            variables_list[f'dof{dof}'] = dof_mapping[dof]
        # print(variables_list)
        section = base.CreateEntity(self.target_deck_object, 'SECTION_JOINT', variables_list) 

        variables_list = {'PID': section,'I':ref_node, 'J':nodes[0],}
        base.CreateEntity(self.target_deck_object, 'JOINT', variables_list)

        


    def get_coupling_properties(self, coupling):
        fields = coupling.card_fields(self.source_deck_object)
        field_vals = coupling.get_entity_values(self.source_deck_object,(fields))

        ref_node = field_vals[Mapper.coupling[self.source_deck]['ref_node']]
        nodes = [field_vals[Mapper.coupling[self.source_deck]['nd_list']+f'{i}'] for i in range(0,len(fields)) if Mapper.coupling[self.source_deck]['nd_list']+f'{i}' in fields and i != 0]
        dofs = list(set([field_vals[Mapper.coupling[self.source_deck]['comp_list']+f'{i}'] for i in range(0,len(fields)) if Mapper.coupling[self.source_deck]['comp_list']+f'{i}' in fields and i != 0]))
        if Mapper.coupling[self.source_deck]['coup_ori'] in fields:
            orient = field_vals[Mapper.coupling[self.source_deck]['coup_ori']]
        else:
            if self.global_orient == None:
                variables_list = {'Name': 'GLOBAL_ORIENTATION','A1':0,'A2':0,'A3':0,'B1':0,'B2':0,'B3':1,'C1':1,'C2':0,'C3':0,}
                self.global_orient = base.CreateEntity(self.source_deck, 'ORIENTATION_R', variables_list) 
            orient = self.global_orient

        # print(ref_node)
        # print(nodes)
        # print(dofs)
        # print(orient)

        return ref_node, nodes, dofs, orient