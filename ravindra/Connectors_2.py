# PYTHON script
import os
import ansa
from ansa import base
from ansa import constants
deck = constants.ABAQUS
import Write_Connectors_and_Fasteners
import importlib
importlib.reload(Write_Connectors_and_Fasteners)

all_keys = ansa.utils.DatabaseBrowserInfo(deck)
print('\n'.join(all_keys.keys()))
print(all_keys)
print(len(all_keys.keys()))
# def main():
# 	# Need some documentation? Run this with F5
# deck = constants.ABAQUS

# conn_sections = base.CollectEntities(deck, None, 'CONNECTOR_SECTION')
# conn_sec = conn_sections[0]
# print(conn_sec._name)


# fastener_dict = {}

# fastener_sections = base.CollectEntities(deck, None, 'FASTENER')
# for fastener_section in fastener_sections:
#     fastener_elset_val = fastener_section.get_entity_values(deck,('ELSET id','connector', 'standalone'))
#     if fastener_elset_val['connector'] == 'yes' and fastener_elset_val['standalone'] == 'no' :
#         fastener_elset = fastener_elset_val['ELSET id']
#         fastener_dict[fastener_elset._name] = fastener_section
#     else:
#         fastener_interaction = fastener_section.get_entity_values(deck,('INTERACTION',))['INTERACTION']
#         if fastener_elset_val['connector'] != 'yes':
#             print(f'*FASTENER with INTERACTION NAME:{fastener_interaction._name} is defined with NODE SET, it is not processed')
#         if fastener_elset_val['standalone'] != 'no':
#             print(f'*FASTENER with INTERACTION NAME:{fastener_interaction._name} is defined with standalone:yes, it is not processed')

# # print(fastener_dict)

# fast = fastener_dict['HM_C_ST_ST_FATIGUE_1372']


# print(tuple(fast.card_fields(deck)))

# fast_prop = fast.get_entity_values(deck,tuple(fast.card_fields(deck)))
# r_influ = fast_prop['INFLUENCE R']
# r_search = fast_prop['SEARCH R']
# interaction = fast_prop['INTERACTION']
# adjust = fast_prop['ADJUST']
# n_layers = fast_prop['NLAYERS']
# fast_orient = fast_prop['ORIENT']


# surfs = [fast_prop[f'SURF{i}'] for i in range(1,12) if fast_prop[f'SURF{i}'] != None]

# print(interaction._name)
# print(surfs)

# print(f'SWGEN,{interaction._name},{r_influ},{surfs[0]},{surfs[1]},{n1},{n2},{r_search}')


# elset = base.CollectEntities(deck, fastener_section, None)
# print(elset)


# fastener_section_SET = fastener_section.get_entity_values(deck,('ELSET id',))
# if fastener_section_SET:
# 	set_id = fastener_section_SET['ELSET id'] 
# print(set_id)

# fastener_section_SET = base.GetEntity(deck, "SET", 928)
# print(set_id._name)
# print(fastener_section_SET._name)

# conn = base.NameToEnts("^"+set_id._name+"$")
# print(conn)

# print(connector_section_prop)

# sec_elems = base.CollectEntities(deck, conn_sec, None)

# behave = connector_section_prop['MID']
# mat_name = behave._name

# dirr = dir(behave)


# mat_elast1 = base.NameToEnts("^CONNECTOR ELASTICITY:CURVE_BUSHING/10_BEHAVIOR$")
# mat_elast2 = base.NameToEnts("^CONNECTOR ELASTICITY:CURVE_BUSHING/10_BEHAVIOR:1$")

# print(mat_elast1)
# print(mat_elast2)
# elast1 = mat_elast1[0]
# elast2 = mat_elast2[0]
# print(elast1)
# print(elast2)

# props1 = elast1.get_entity_values(deck,('COMP','COMP(1)','NONLINEAR(1)','El.Stiff.(1)', 'Freq.(1)', 'DATA TABLE(1)'))
# print(props1)

# props2 = elast2.get_entity_values(deck,('COMP','COMP(1)','NONLINEAR(1)','El.Stiff.(1)', 'Freq.(1)','DATA TABLE(1)'))
# print(props2)


# if props1['NONLINEAR(1)'] == "YES":
#     print("Prop1")
#     print(props1)
#     ent = ansa.base.NameToEnts("^CONNECTOR ELASTICITY:CURVE_BUSHING/10_BEHAVIOR Data Table$")
#     curve_data = ansa.base.GetLoadCurveData(ent[0])
#     print(curve_data)

# if props2['NONLINEAR(1)'] == "YES":
#     print("Prop2")
#     print(props2)
#     ent = ansa.base.NameToEnts("^CONNECTOR ELASTICITY:CURVE_BUSHING/10_BEHAVIOR:1 Data Table$")
#     print(sorted(ent))
#     curve_data = ansa.base.GetLoadCurveData(ent[0])
#     print(curve_data)
    
# coordinate_sys = connector_section_prop['ORIENT_1']
# c_name = coordinate_sys._name

# aa = 2
# if __name__ == '__main__':
#     main()

import os

folder = os.getcwd()    # files created will be 'connectors_only.dat', 'connectors_and_fasteners.dat', 'fasteners.dat'
conn_sections = base.CollectEntities(deck, None, 'CONNECTOR_SECTION')
fasteners = base.CollectEntities(deck, None, 'FASTENER')

conns = Write_Connectors_and_Fasteners.process_entities(location = folder, connectors = conn_sections, fasteners = fasteners)
# conns.write()

# x=22

sda = 5