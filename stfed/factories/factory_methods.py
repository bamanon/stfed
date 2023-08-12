import stfed.factories.ani
import stfed.factories.fon
import stfed.factories.mif
import stfed.factories.pal
import stfed.factories.tlb

import stfed.model


def factory_method_for_resource(resource: stfed.model.Resource):
    rt = stfed.model.ResourceType(resource.resource_type)
    if rt == stfed.model.ResourceType.ANI:
        return stfed.factories.ani.parse
    elif rt == stfed.model.ResourceType.FON:
        return stfed.factories.fon.parse
    elif rt == stfed.model.ResourceType.MIF:
        return lambda r: stfed.factories.mif.parse_map_info_res(r.data())
    elif rt == stfed.model.ResourceType.PAL:
        return lambda r: stfed.factories.pal.parse(r.data())
    elif rt == stfed.model.ResourceType.TLB:
        return lambda r: stfed.factories.tlb.parse_tile_library(r.data())
    else:
        return None