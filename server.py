
from fastapi import FastAPI
from json_fdk_context import JsonFdkContext

app = FastAPI()
context = JsonFdkContext(root_path="path/to/your/data")

@app.get("/object/{object_id}/info")
async def get_info(object_id: str):
    return context.info_by(object_id)

@app.get("/object/{object_id}/structured-description")
async def get_structured_description(object_id: str):
    return context.get_structured_description(object_id)

@app.get("/object/{object_id}/component-relationships")
async def get_component_relationships(object_id: str):
    return context.get_component_relationships(object_id)

@app.get("/object/{object_id}/assembly-relationships")
async def get_assembly_relationships(object_id: str):
    return context.get_assembly_relationships(object_id)

@app.get("/object/{object_id}/release-history")
async def get_release_history(object_id: str):
    return context.get_release_history(object_id)

@app.get("/object/{object_id}/sia-phase-scopes")
async def get_sia_phase_scopes(object_id: str):
    return context.get_sia_phase_scopes(object_id)

@app.get("/object/{object_id}/ifc-assignments")
async def get_ifc_assignments(object_id: str):
    return context.get_ifc_assignments(object_id)

@app.get("/object/{object_id}/ebkp-concepts")
async def get_ebkp_concepts(object_id: str):
    return context.get_ebkp_concepts(object_id)

@app.get("/object/{object_id}/domain-models")
async def get_domain_models(object_id: str):
    return context.get_domain_models(object_id)

@app.get("/object/{object_id}/property-sets")
async def get_property_sets(object_id: str):
    return context.get_property_sets(object_id)

@app.get("/object/{object_id}/referenced-enumerations")
async def get_referenced_enumerations(object_id: str):
    return context.get_referenced_enumerations(object_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
