import os
from mcp.server import FastMCP

from json_fdk_context import JsonFdkContext

mcp = FastMCP("fdk_mcp_server")
ctx = JsonFdkContext(
    root_path=os.path.expanduser("~/workspace/0_data/fdk/sbb"),
)


@mcp.resource(":object//{object_id}/info")
async def get_info(object_id: str):
    return ctx.info_by(object_id)


@mcp.resource(":object//{object_id}/structured-description")
async def get_structured_description(object_id: str):
    return ctx.get_structured_description(object_id)


@mcp.resource(":object//{object_id}/component-relationships")
async def get_component_relationships(object_id: str):
    return ctx.get_component_relationships(object_id)


@mcp.resource(":object//{object_id}/assembly-relationships")
async def get_assembly_relationships(object_id: str):
    return ctx.get_assembly_relationships(object_id)


@mcp.resource(":object//{object_id}/release-history")
async def get_release_history(object_id: str):
    return ctx.get_release_history(object_id)


@mcp.resource(":object//{object_id}/sia-phase-scopes")
async def get_sia_phase_scopes(object_id: str):
    return ctx.get_sia_phase_scopes(object_id)


@mcp.resource(":object//{object_id}/ifc-assignments")
async def get_ifc_assignments(object_id: str):
    return ctx.get_ifc_assignments(object_id)


@mcp.resource(":object//{object_id}/ebkp-concepts")
async def get_ebkp_concepts(object_id: str):
    return ctx.get_ebkp_concepts(object_id)


@mcp.resource(":object//{object_id}/domain-models")
async def get_domain_models(object_id: str):
    return ctx.get_domain_models(object_id)


@mcp.resource(":object//{object_id}/property-sets")
async def get_property_sets(object_id: str):
    return ctx.get_property_sets(object_id)


@mcp.resource(":object//{object_id}/referenced-enumerations")
async def get_referenced_enumerations(object_id: str):
    return ctx.get_referenced_enumerations(object_id)


@mcp.resource(":object//{object_id}/mcp-model-content")
async def get_mcp_model_content(object_id: str):
    return {
        "info": ctx.info_by(object_id),
        "structured_description": ctx.get_structured_description(object_id),
        "component_relationships": ctx.get_component_relationships(object_id),
        "assembly_relationships": ctx.get_assembly_relationships(object_id),
        "release_history": ctx.get_release_history(object_id),
        "sia_phase_scopes": ctx.get_sia_phase_scopes(object_id),
        "ifc_assignments": ctx.get_ifc_assignments(object_id),
        "ebkp_concepts": ctx.get_ebkp_concepts(object_id),
        "domain_models": ctx.get_domain_models(object_id),
        "property_sets": ctx.get_property_sets(object_id),
        "referenced_enumerations": ctx.get_referenced_enumerations(object_id),
    }


# Main execution
def main():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
