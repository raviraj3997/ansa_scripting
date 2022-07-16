# PYTHON script
import os
from ansa import base
from ansa import utils
from ansa import constants

def correcter_conta_set():
    correct = CorrectContactSet()
    correct.remove_interior_faces()

class CorrectContactSet:
    def __init__(self) -> None:
        self.base = base
        self.deck = constants.ABAQUS

    def remove_interior_faces(self):
        # set_ents = base.CollectEntities(self.deck,None, 'SET')
        # for ent in set_ents:
        #     all_facets = base.CollectEntities(self.deck,ent, 'SOLIDFACET')
        #     if len(all_facets)!=0:
        #         ret = base.GetInternalAndExternalFacets(self.deck,all_facets)
        #         if len(all_facets) != len(set(all_facets) - set(ret['internal_facets'])):
        #             print("MISMATCH in SET :", ent._name)
        #             print('ALL FACES : ' ,len(all_facets))
        #             print('EXTERIOR FACES : ',len(set(all_facets) - set(ret['internal_facets'])))
        #             base.RemoveFromSet(ent,set(all_facets) - (set(all_facets) - set(ret['internal_facets'])))
        #             fixed=base.CollectEntities(self.deck,ent, 'SOLIDFACET')
        #             print("FACETS after fixing : ",len(fixed))
        set_ents = base.CollectEntities(self.deck,None, 'SET')
        solids = base.CollectEntities(constants.ABAQUS, None, "SOLID")
        all_ext_faces = base.GetInternalAndExternalFacets(self.deck,solids)
        # print(len(all_ext_faces['external_facets']))
        for ent in set_ents:
            all_facets = base.CollectEntities(self.deck,ent, 'SOLIDFACET')
            if len(all_facets)!=0:
                common_sets = set(all_ext_faces['external_facets']) & set(all_facets)
                # print(ent._name, " Common with all facets are : ", len(common_sets))
                ret = base.GetInternalAndExternalFacets(self.deck,all_facets)
                #print("SET_NAME : ",ent._name)
                #print('ALL FACES : ' ,len(all_facets))
                #print('EXTERIOR FACES : ',len(set(all_facets) - set(ret['internal_facets'])))
                #print("-------------------------------------")
                facets_to_remove= set(all_facets) - common_sets
                if len(all_facets) !=common_sets:
                    print("MISMATCH in SET :", ent._name)
                    #print("SET_NAME : ",ent._name)
                    print('Original FACES : ' ,len(all_facets))
                    print('EXTERIOR FACES : ',len(common_sets))
                    print('INTERIOR FACES : ',len(facets_to_remove))
                    base.RemoveFromSet(ent,facets_to_remove)
                    fixed=base.CollectEntities(self.deck,ent, 'SOLIDFACET')
                    print("FACETS are fixing : ",len(fixed))