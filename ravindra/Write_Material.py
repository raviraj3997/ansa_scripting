import os
import string
import ansa
from ansa import base
from ansa import constants
import math



def upadate_materials():
    mat = Materials()
    mat.make_material_defined()
    # mat.change_in_ansys_deck()


class Materials:
    def __init__(self) -> None:
        self.base = base
        self.deck = constants.ABAQUS
        self.ansys_deck = constants.ANSYS

    def make_material_defined(self):
        material_entities = base.CollectEntities(self.ansys_deck, None, '__MATERIALS__')
        fields = {"DEFINED": "YES"}
        for material in material_entities:
            base.SetEntityCardValues(self.ansys_deck, material, fields)

    def change_in_ansys_deck(self):
        mats = base.CollectEntities(self.deck, None, '__MATERIALS__')
        ans_mats = base.CollectEntities(self.ansys_deck, None, '__MATERIALS__')
        for mat in mats:
            mat_present = False
            for a_mat in ans_mats:
                if a_mat._name == mat._name:
                    # print(mat._name)
                    mat_present = True
                    break
            if mat_present == False:
                print(f"Material with name '{mat._name}' is not in ansys deck of ansa.")
            else:
                props = tuple(mat.card_fields(self.deck))
                prop_vals = mat.get_entity_values(self.deck,props)
                defined_props = [prop for prop in props if prop_vals[prop]=='YES']
                # print(prop_vals)
                if prop_vals['Elasticity'] == 'HYPERELASTIC':
                    if "*HYPERELASTIC" in defined_props:
                        self.change_hyperelastic(prop_vals, mat, a_mat)
                elif prop_vals['Elasticity'] == 'ELASTIC':
                    pass
                else:
                    print(f"Material with name '{mat._name}' has {prop_vals['Elasticity']}, which is not processed with script. check the material before use")

                if "*PLASTIC" in defined_props:
                    self.change_plastic(prop_vals, mat, a_mat)



    def change_hyperelastic(self, prop_vals, mat, a_mat):
        if prop_vals['method hyperel'] == 'REDUCED POLYNOMIAL':
            if prop_vals['TEST DATA HYEL'] == 'NO' and prop_vals['DEP_HYELA'] == 'NO':
                para_list = []
                for i in range(1,2*int(prop_vals['N'])+1):
                    para_list.append(prop_vals[f'f{i}'])
                print('HYPER MATERIAL')
                print(mat._name)
                print(para_list)
            else:
                print(f"material '{mat._name}' has test data or tabular data, which is not processed with script. check the material before use")

        else:
            print(f" the method '{prop_vals['method hyperel']}' for material '{mat._name}' is not processed with script. check the material before use")
    def change_plastic(self, prop_vals, mat, a_mat):
        if (prop_vals['HARDENING'] == ' ' or prop_vals['HARDENING'] == 'ISOTROPIC') and  prop_vals['RATE']== 'NO':
            table = prop_vals['DATA TABLE PLAST']
            data = self.base.GetLoadCurveData(table)
            print('Plast MATERIAL')
            print(mat._name)
            print(data)
        else:
            print(f"Material with name '{a_mat._name}' has {prop_vals['HARDENING']} material property, which is not processed with script. check the material before use")

