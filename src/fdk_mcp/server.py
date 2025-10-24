"""FDK MCP Server implementation."""

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations

from .adapters.presenters import JsonPresenter, MarkdownPresenter
from .infrastructure import Container
from .models import (
    AdvancedSearchInput,
    DetailLevel,
    GetCacheCoverageInput,
    GetObjectInput,
    GroupObjectsInput,
    LanguageCode,
    ListObjectsInput,
    ResponseFormat,
    SearchPropertiesInput,
)
from .use_cases import (
    AdvancedSearchRequest,
    AdvancedSearchUseCase,
    DownloadCatalogRequest,
    DownloadCatalogUseCase,
    GetCacheCoverageRequest,
    GetCacheCoverageUseCase,
    GetObjectRequest,
    GetObjectUseCase,
    GroupObjectsRequest,
    GroupObjectsUseCase,
    ListDomainsRequest,
    ListDomainsUseCase,
    ListObjectsRequest,
    ListObjectsUseCase,
    MatchMode,
    SearchPropertiesRequest,
    SearchPropertiesUseCase,
    UpdateCacheRequest,
    UpdateCacheUseCase,
)


mcp = FastMCP("fdk_mcp")

# Initialize Clean Architecture components
_container = Container()
_markdown_presenter = MarkdownPresenter()
_json_presenter = JsonPresenter()


@mcp.tool(
    name="fdk_list_objects",
    annotations=ToolAnnotations(
        title="List FDK Objects",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def fdk_list_objects(params: ListObjectsInput, ctx: Context) -> str:
    """List/search FDK catalog objects.

    Search and filter objects from the FDK catalog with pagination.
    Use this when exploring available objects or searching by criteria.

    Args:
        params (ListObjectsInput):
            - domain: Filter by domain name
            - search: Search term for names
            - limit: Max results (1-100, default 20)
            - offset: Skip results (default 0)
            - detail: concise or detailed
            - response_format: markdown or json

    Returns:
        str: Formatted list of matching objects

    Examples:
        - List bridges: domain="Brücken"
        - Search by name: search="Stütze"
        - First 50 items: limit=50, offset=0
    """
    try:
        await ctx.info(f"Listing objects: domain={params.domain}, search={params.search}")

        # Create use case instance
        use_case = _container.get_use_case(ListObjectsUseCase)

        # Create request
        request = ListObjectsRequest(
            domain_filter=params.domain,
            search_query=params.search,
            language="de",
            limit=params.limit,
            offset=params.offset,
        )

        # Execute use case
        response = await use_case.execute(request)

        await ctx.debug(f"Found {response.total} matching objects")

        # Format response using presenter
        if params.response_format == ResponseFormat.JSON:
            return _json_presenter.format_object_list(response.objects, response.total, params.offset)
        else:
            if params.detail == DetailLevel.DETAILED:
                return _markdown_presenter.format_object_list_detailed(response.objects, response.total, params.offset)
            else:
                return _markdown_presenter.format_object_list(response.objects, response.total, params.offset)

    except Exception as e:
        await ctx.error(f"Failed to list objects: {e}")
        return f"Error listing objects: {str(e)}"


@mcp.tool(
    name="fdk_get_object",
    annotations=ToolAnnotations(
        title="Get FDK Object Details",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def fdk_get_object(params: GetObjectInput, ctx: Context) -> str:
    """Get complete details for an FDK object.

    Retrieve full object information including PropertySets,
    Properties, relationships, and metadata.

    ⚡ CACHING:
        - Cached objects: <1ms response time (instant!)
        - Uncached objects: ~100ms download time (negligible)
        - Cache persists between sessions

    💡 FOR BULK OPERATIONS:
        If you need details for many objects (>20), consider using
        fdk_update_cache to pre-download all objects first. This avoids
        repeated individual downloads.

        Example workflow for bulk analysis:
        Step 1: Check cache coverage
                coverage = fdk_get_cache_coverage(domain_filter="YourDomain")
        Step 2: If many objects missing:
                fdk_update_cache(domain_filter="YourDomain")
        Step 3: Then fetch individual objects
                fdk_get_object(object_id="OBJ_1")
                fdk_get_object(object_id="OBJ_2")
                ...

    Args:
        params (GetObjectInput):
            - object_id: Object ID (e.g., 'OBJ_BR_1')
            - language: Language code (de/fr/it/en)
            - response_format: markdown or json

    Returns:
        str: Complete object details

    Examples:
        - Get object: object_id="OBJ_BR_1"
        - French version: object_id="OBJ_BR_1", language="fr"
        - JSON format: object_id="OBJ_BR_1", response_format="json"
    """
    try:
        await ctx.info(f"Fetching object: {params.object_id} (lang={params.language})")

        # Create use case instance
        use_case = _container.get_use_case(GetObjectUseCase)

        # Create request
        request = GetObjectRequest(object_id=params.object_id, language=params.language)

        # Execute use case
        response = await use_case.execute(request)

        await ctx.debug(f"Retrieved object: {response.object.name}")

        # Format response using presenter
        if params.response_format == ResponseFormat.JSON:
            return _json_presenter.format_object(response.object, from_cache=response.from_cache)
        else:
            return _markdown_presenter.format_object_detail(response.object, from_cache=response.from_cache)

    except Exception as e:
        await ctx.error(f"Failed to get object {params.object_id}: {e}")
        return f"Error getting object: {str(e)}"


@mcp.tool(
    name="fdk_search_properties",
    annotations=ToolAnnotations(
        title="Search Properties",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def fdk_search_properties(params: SearchPropertiesInput, ctx: Context) -> str:
    """Search properties across all FDK objects.

    Find properties by name across the entire catalog,
    showing context (object, PropertySet) for each match.

    ⚠️ DOWNLOAD NOTE:
    This searches PropertySets which require detailed object data.
    If objects aren't cached, they will be downloaded automatically.
    First-time searches may take 30s-2min depending on catalog size.

    💡 RECOMMENDED: For large searches, check cache first!
        Step 1: coverage = fdk_get_cache_coverage()
        Step 2: If estimated_download_time > 10 seconds:
                → Inform user about download time and ask for confirmation
        Step 3: Run this search

    ⚡ PERFORMANCE:
        - Cached catalog: Search completes in seconds
        - Uncached catalog: Downloads required (30s-2min first time)
        - Subsequent searches: Instant!

    Args:
        params (SearchPropertiesInput):
            - query: Search term (min 1 char)
            - limit: Max results (1-100)
            - response_format: markdown or json

    Returns:
        str: Matching properties with context

    Examples:
        - Find property: query="Breite"
        - Search material: query="Material"
        - Temperature properties: query="Temperatur"
    """
    try:
        await ctx.info(f"Searching properties: query='{params.query}'")

        # Create use case instance
        use_case = _container.get_use_case(SearchPropertiesUseCase)

        # Create request
        request = SearchPropertiesRequest(query=params.query, language="de", limit=params.limit)

        # Execute use case
        response = await use_case.execute(request)

        await ctx.debug(f"Found {response.total_matches} matching properties")

        # Format response using presenter
        if params.response_format == ResponseFormat.JSON:
            return _json_presenter.format_property_matches(response.matches, response.total_matches)
        else:
            if not response.matches:
                return f"No properties found matching '{params.query}'"
            return _markdown_presenter.format_property_matches(response.matches, response.total_matches)

    except Exception as e:
        await ctx.error(f"Failed to search properties '{params.query}': {e}")
        return f"Error searching properties: {str(e)}"


@mcp.tool(
    name="fdk_list_domains",
    annotations=ToolAnnotations(
        title="List Domains",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def fdk_list_domains(ctx: Context) -> str:
    """List all domains with object counts.

    Get overview of catalog organization by domain,
    showing how many objects exist in each category.

    Returns:
        str: Domain summary with counts

    Examples:
        - Use to explore catalog structure
        - Find which domains have most objects
    """
    try:
        await ctx.info("Listing domains")

        # Create use case instance
        use_case = _container.get_use_case(ListDomainsUseCase)

        # Create request
        request = ListDomainsRequest(language="de")

        # Execute use case
        response = await use_case.execute(request)

        await ctx.debug(f"Found {response.total_domains} domains")

        # Format response using presenter (always markdown for simplicity)
        return _markdown_presenter.format_domains_summary(
            response.domains, response.total_domains, response.total_objects
        )

    except Exception as e:
        await ctx.error(f"Failed to list domains: {e}")
        return f"Error listing domains: {str(e)}"


@mcp.tool(
    name="fdk_advanced_search",
    annotations=ToolAnnotations(
        title="Advanced Search",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def fdk_advanced_search(params: AdvancedSearchInput, ctx: Context) -> str:
    """Advanced search across ANY JSON field in FDK objects.

    IMPORTANT: Use this tool instead of writing Python loops or custom search code!
    This tool efficiently searches across all data with automatic detail loading.

    ⚠️ DOMAIN FILTER VALIDATION:
    If using domain_filter, you MUST first call fdk_list_domains to get
    the exact domain name! Domain matching is case-insensitive but requires
    exact name match (e.g., "Fahrbahn" not "Fahrbahn FB").

    ⚡ EFFICIENCY PATTERNS:

    COUNTING (most efficient):
      advanced_search(query="X", domain_filter="Y", limit=1)
      → Read response['total_matches'] for the count, NOT len(matches)!

    EXISTENCE CHECK:
      advanced_search(query="X", limit=1)
      → Check if response['total_matches'] > 0

    AGGREGATION BY DOMAIN:
      for domain in domains:
          result = advanced_search(query="X", domain_filter=domain, limit=1)
          counts[domain] = result['total_matches']

    RESPONSE STRUCTURE:
    {
      "total_matches": 1416,    ← Total matches (ALWAYS present - use for counting!)
      "matches": [...],         ← Actual match objects (only if limit > 0)
    }
    The 'total_matches' field is ALWAYS available, even with limit=1!

    ✅ DO:
    - Use limit=1 for counting/checking existence
    - Use response['total_matches'] for aggregations
    - Use domain_filter to scope searches

    ❌ DON'T:
    - Fetch limit=200 just to count len(matches)
    - Write loops to iterate through results for counting
    - Make large queries when you only need counts

    Search in any field: propertySets, properties, ifcClassAssignments, ebkpConcepts,
    aksCode, componentRelationships, assemblyRelationships, domainModel, and more.

    The tool automatically downloads detailed object data when needed, so you don't
    need to worry about whether data is available - just search!

    Args:
        params (AdvancedSearchInput):
            - search_fields: Which fields to search (default: ["all"])
            - query: Search term (required)
            - domain_filter: Optional domain restriction (call fdk_list_domains first!)
            - match_mode: How to match (contains/equals/starts_with/ends_with)
            - case_sensitive: Case-sensitive search (default: False)
            - limit: Max results (1-200, default: 50)
            - response_format: markdown or json

    Returns:
        str: Search results with object context and matched paths

    Examples:
        - DON'T: Write Python loops to search through objects
        - DON'T: Use domain_filter without calling fdk_list_domains first
        - DON'T: Use limit=200 just to count len(results)
        - DO: Use this tool for all searches!
        - DO: Use limit=1 for counting (reads response['total_matches'])

        - Count objects per domain (EFFICIENT):
          Step 1: domains = fdk_list_domains()
          Step 2: For each domain:
                  result = advanced_search(
                      search_fields=["propertySets"],
                      query="SBB-CFF-FFS_PO",
                      domain_filter=domain,
                      limit=1  ← Only metadata!
                  )
                  count = result['total_matches']  ← Use this, not len(matches)!

        - With domain filter (correct workflow):
          Step 1: Call fdk_list_domains to get available domains
          Step 2: Use EXACT domain name from list in domain_filter
          Example: domain_filter="Fahrbahn", query="SBB-CFF-FFS_PO"

        - Find PropertySet: search_fields=["propertySets"], query="Pset_WallCommon"
        - Find IFC class: search_fields=["ifcClassAssignments"], query="IfcWall"
        - Find eBKP code: search_fields=["ebkpConcepts"], query="C3.1"
        - Search all fields: search_fields=["all"], query="Stütze"
        - Exact match: match_mode="equals", query="IfcWall"
        - Starts with: match_mode="starts_with", query="Pset_"
        - Case-sensitive: case_sensitive=True

    ⚡ PERFORMANCE & CACHING:
        - Searches entire catalog in seconds
        - Auto-downloads missing data if not cached
        - First search may take 30s-2min if many objects need download
        - Subsequent searches are INSTANT!

    💡 RECOMMENDED: Check cache coverage first to inform user about download time!

        WORKFLOW for searches involving PropertySets or detailed fields:

        Step 1: Check cache coverage
            coverage = fdk_get_cache_coverage(domain_filter="YourDomain")

        Step 2: Evaluate estimated download time
            IF coverage.estimated_download_time > 10 seconds:
                → Inform user: "This search will download X objects (~Y seconds). Continue?"
                → Wait for user confirmation

        Step 3: Run the actual search
            fdk_advanced_search(query="...", domain_filter="...")

        WHY: First-time searches trigger downloads. Cache coverage prevents
        surprising delays and improves user experience!

        Example: "I need to download 500 objects (~1 minute) for this search. Proceed?"
    """
    try:
        await ctx.info(
            f"Advanced search: fields={params.search_fields}, query='{params.query}', "
            f"domain={params.domain_filter or 'all'}"
        )

        # Create use case instance
        use_case = _container.get_use_case(AdvancedSearchUseCase)

        # Map MatchMode enum from models to use_cases
        match_mode_map = {
            "contains": MatchMode.CONTAINS,
            "equals": MatchMode.EQUALS,
            "starts_with": MatchMode.STARTS_WITH,
            "ends_with": MatchMode.ENDS_WITH,
        }
        match_mode = match_mode_map.get(params.match_mode.value, MatchMode.CONTAINS)

        # Create request
        request = AdvancedSearchRequest(
            search_fields=params.search_fields,
            query=params.query,
            domain_filter=params.domain_filter,
            match_mode=match_mode,
            case_sensitive=params.case_sensitive,
            language="de",
            limit=params.limit,
        )

        # Execute use case
        response = await use_case.execute(request)

        await ctx.debug(f"Returning {len(response.matches)}/{response.total_matches} results")

        # Format response using presenter
        if params.response_format == ResponseFormat.JSON:
            return _json_presenter.format_search_matches(response.matches, response.total_matches)
        else:
            if not response.matches:
                return f"No matches found for '{params.query}' in fields: {', '.join(params.search_fields)}"
            return _markdown_presenter.format_search_matches(response.matches, response.total_matches)

    except Exception as e:
        await ctx.error(f"Failed advanced search: {e}")
        return f"Error performing advanced search: {str(e)}"


@mcp.tool(
    name="fdk_refresh_cache",
    annotations=ToolAnnotations(
        title="Refresh Cache",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def fdk_refresh_cache(ctx: Context) -> str:
    """Force cache refresh from API.

    Manually trigger cache update from the FDK API.
    Normally cache auto-refreshes every 24 hours.

    Returns:
        str: Cache update status

    Examples:
        - Use when you need latest data
        - Use after known catalog updates
    """
    try:
        await ctx.info("Refreshing cache from API")

        # Get cache repository directly
        cache = _container.get_cache_repository()
        if not cache:
            return "Error: Cache not available"

        # Force cache to be considered stale
        cache.update_metadata(0)

        # Use ListObjectsUseCase to trigger cache refresh
        use_case = _container.get_use_case(ListObjectsUseCase)
        request = ListObjectsRequest(language="de", limit=1)
        await use_case.execute(request)

        # Get cache stats
        stats = cache.get_cache_stats()
        await ctx.info(f"Cache refreshed: {stats.object_count} objects")

        # Format response using presenter
        release_name = stats.release.name if stats.release else None
        return _markdown_presenter.format_cache_stats(
            last_updated=stats.last_updated,
            object_count=stats.object_count,
            is_fresh=stats.is_fresh,
            release_name=release_name,
        )

    except Exception as e:
        await ctx.error(f"Failed to refresh cache: {e}")
        return f"Error refreshing cache: {str(e)}"


@mcp.tool(
    name="fdk_get_cache_stats",
    annotations=ToolAnnotations(
        title="Get Cache Stats",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def fdk_get_cache_stats(ctx: Context) -> str:
    """Get cache statistics and status.

    View cache metadata including last update time,
    object count, and freshness status.

    Returns:
        str: Cache statistics

    Examples:
        - Check cache status
        - Verify cache freshness
    """
    try:
        await ctx.info("Retrieving cache statistics")

        # Get cache repository directly
        cache = _container.get_cache_repository()
        if not cache:
            return "Error: Cache not available"

        # Get cache stats
        stats = cache.get_cache_stats()

        # Format response using presenter
        release_name = stats.release.name if stats.release else None
        return _markdown_presenter.format_cache_stats(
            last_updated=stats.last_updated,
            object_count=stats.object_count,
            is_fresh=stats.is_fresh,
            release_name=release_name,
        )

    except Exception as e:
        await ctx.error(f"Failed to get cache stats: {e}")
        return f"Error getting cache stats: {str(e)}"


@mcp.tool(
    name="fdk_get_cache_coverage",
    annotations=ToolAnnotations(
        title="Get Cache Coverage",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def fdk_get_cache_coverage(params: GetCacheCoverageInput, ctx: Context) -> str:
    """Analyze cache coverage and estimate download time.

    ⚡ USE THIS BEFORE expensive operations to inform the user!

    This tool shows:
    - How many objects are already cached (with full details)
    - How many need to be downloaded
    - Estimated download time
    - Smart recommendations

    💡 PROACTIVE COMMUNICATION PATTERN:

    BEFORE running searches that need PropertySets:
    1. Call this tool to check cache coverage
    2. If download time > 10 seconds, inform the user!
    3. Ask if they want to proceed

    Example workflow:
    ```
    User: "Find all objects with PropertySet X"

    Claude:
    1. coverage = get_cache_coverage()
    2. IF coverage.estimated_download_time > 10:
       → "This will download 500 objects (~1 minute). Proceed?"
    3. User confirms
    4. Run the actual search
    ```

    USE CASES:
    ✓ Check cache before expensive searches
    ✓ Estimate download time for user communication
    ✓ Decide whether to use update_cache first
    ✓ Show cache health to user

    PARAMETERS:
    - language: Language code (de/fr/it/en, default: de)
    - domain_filter: Only check coverage for specific domain
    - response_format: markdown or json

    EXAMPLE OUTPUT:
    📊 Cache Coverage Analysis
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Total Objects: 1687
    ✓ Cached with details: 1200 (71%)
    ⚠ Cached (summary only): 300 (18%)
    ✗ Not cached: 187 (11%)

    ⚡ Download Required
       Objects to download: 487
       Estimated time: ~30 seconds

    PERFORMANCE:
    - Very fast (<1 second)
    - Only fetches summary data from API
    - Local cache analysis
    """
    try:
        domain_info = f" for domain '{params.domain_filter}'" if params.domain_filter else ""
        await ctx.info(f"Analyzing cache coverage{domain_info}")

        # Create use case instance
        use_case = _container.get_use_case(GetCacheCoverageUseCase)

        # Create request
        request = GetCacheCoverageRequest(language=params.language, domain_filter=params.domain_filter)

        # Execute use case
        response = await use_case.execute(request)
        stats = response.stats

        await ctx.debug(
            f"Coverage: {stats.coverage_percentage}% ({stats.cached_with_details}/{stats.total_objects} with details)"
        )

        # Format response using presenter
        if params.response_format == ResponseFormat.JSON:
            return _json_presenter.format_cache_coverage(stats)
        else:
            return _markdown_presenter.format_cache_coverage(stats)

    except Exception as e:
        await ctx.error(f"Failed to analyze cache coverage: {e}")
        return f"Error analyzing cache coverage: {str(e)}"


@mcp.tool(
    name="fdk_download_all_objects",
    annotations=ToolAnnotations(
        title="Download All Objects",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def fdk_download_all_objects(
    ctx: Context,
    language: LanguageCode = "de",
    domain_filter: str | None = None,
    max_concurrent: int = 10,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
) -> str:
    """Download all detail objects from API to cache (FAST parallel version).

    Downloads complete detail data for FDK objects with parallel processing,
    including propertySets, relationships, and full metadata.
    This enables fast local searches using ripgrep/grep.

    ⚠️ DOMAIN FILTER VALIDATION:
    If using domain_filter, you MUST first call fdk_list_domains to get
    the exact domain name! Domain matching is case-insensitive but requires
    exact name match (e.g., "Fahrbahn" not "Fahrbahn FB").

    Args:
        language: Language code (de/fr/it/en, default: de)
        domain_filter: Optional domain filter (call fdk_list_domains first!)
        max_concurrent: Max parallel requests (default: 10, range: 1-20)
        response_format: Output format (markdown/json)

    Returns:
        str: Download summary with statistics

    Examples:
        - Download all: No domain_filter
        - With domain filter (correct workflow):
          Step 1: Call fdk_list_domains to get available domains
          Step 2: Use EXACT domain name: domain_filter="Hochbau"
        - Faster download: max_concurrent=15

    Note:
        - All 1687 objects: ~2-3 minutes (parallel)
        - Single domain: <1 minute
        - Requires ~100MB disk space for all
    """
    try:
        domain_info = f" (domain={domain_filter})" if domain_filter else ""
        await ctx.info(f"Starting download of all objects{domain_info}, max_concurrent={max_concurrent}")

        # Create use case instance
        use_case = _container.get_use_case(DownloadCatalogUseCase)

        # Create request
        request = DownloadCatalogRequest(language=language, domain_filter=domain_filter, max_concurrent=max_concurrent)

        # Execute use case
        response = await use_case.execute(request)
        stats = response.stats

        await ctx.info(f"Download completed: {stats.downloaded}/{stats.total_objects} successful")

        # Format response using presenter
        if response_format == ResponseFormat.JSON:
            return _json_presenter.format_download_stats(
                total=stats.total_objects,
                downloaded=stats.downloaded,
                cached=stats.cached,
                failed=stats.failed,
                duration=stats.duration_seconds,
            )
        else:
            result = "# Download All Objects\n\n"
            if domain_filter:
                result += f"**Domain Filter**: {domain_filter}\n\n"
            result += _markdown_presenter.format_download_stats(
                total=stats.total_objects,
                downloaded=stats.downloaded,
                cached=stats.cached,
                failed=stats.failed,
                duration=stats.duration_seconds,
            )
            return result

    except Exception as e:
        await ctx.error(f"Failed to download objects: {e}")
        return f"Error downloading objects: {str(e)}"


@mcp.tool(
    name="fdk_update_cache",
    annotations=ToolAnnotations(
        title="Update Cache",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def fdk_update_cache(
    ctx: Context,
    language: LanguageCode = "de",
    domain_filter: str | None = None,
    force_refresh: bool = False,
    max_concurrent: int = 10,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN,
) -> str:
    """Update missing or outdated objects in cache (FAST parallel version).

    Intelligently updates cache by downloading only:
    - New objects not yet cached
    - Summary-only objects (without propertySets)
    - All objects if force_refresh=True

    ⚠️ DOMAIN FILTER VALIDATION:
    If using domain_filter, you MUST first call fdk_list_domains to get
    the exact domain name! Domain matching is case-insensitive but requires
    exact name match (e.g., "Fahrbahn" not "Fahrbahn FB").

    Args:
        language: Language code (de/fr/it/en, default: de)
        domain_filter: Optional domain filter (call fdk_list_domains first!)
        force_refresh: Re-download all objects (default: False)
        max_concurrent: Max parallel requests (default: 10)
        response_format: Output format (markdown/json)

    Returns:
        str: Update summary with statistics

    Examples:
        - Regular updates: No force_refresh
        - With domain filter (correct workflow):
          Step 1: Call fdk_list_domains to get available domains
          Step 2: Use EXACT domain name: domain_filter="Hochbau"
        - Full refresh: force_refresh=True

    Note:
        - Much faster than full download if cache exists
        - Only downloads what's missing
        - Safe to run regularly
        - Parallel processing for speed
    """
    try:
        domain_info = f" (domain={domain_filter})" if domain_filter else ""
        refresh_mode = "force refresh" if force_refresh else "incremental update"
        await ctx.info(f"Starting cache update{domain_info}, mode={refresh_mode}")

        # Create use case instance
        use_case = _container.get_use_case(UpdateCacheUseCase)

        # Create request
        request = UpdateCacheRequest(
            language=language, domain_filter=domain_filter, force_refresh=force_refresh, max_concurrent=max_concurrent
        )

        # Execute use case
        response = await use_case.execute(request)
        stats = response.stats

        await ctx.info(f"Update completed: {stats.downloaded}/{stats.total_objects} successful")

        # Format response using presenter
        if response_format == ResponseFormat.JSON:
            return _json_presenter.format_download_stats(
                total=stats.total_objects,
                downloaded=stats.downloaded,
                cached=stats.already_cached,
                failed=stats.failed,
                duration=stats.duration_seconds,
            )
        else:
            result = "# Update Cache\n\n"
            if domain_filter:
                result += f"**Domain Filter**: {domain_filter}\n\n"
            result += _markdown_presenter.format_download_stats(
                total=stats.total_objects,
                downloaded=stats.downloaded,
                cached=stats.already_cached,
                failed=stats.failed,
                duration=stats.duration_seconds,
            )

            if stats.downloaded == 0 and stats.failed == 0:
                result += "\n**Cache is already up-to-date!**\n"

            return result

    except Exception as e:
        await ctx.error(f"Failed to update cache: {e}")
        return f"Error updating cache: {str(e)}"


@mcp.tool(name="fdk_group_objects")
async def fdk_group_objects(params: GroupObjectsInput, ctx: Context) -> str:
    """Group and/or sort FDK objects by attributes.

    This tool organizes a list of object IDs by grouping them according to one or more
    attributes and optionally sorting them. It's useful for answering questions like:
    - "Which domains have which PropertySets?"
    - "Group these objects by IFC class and then by domain"
    - "Sort these objects alphabetically by name"
    - "Show me all objects grouped by domain with counts"

    📋 SUPPORTED GROUP_BY FIELDS:
    - "domain" - Group by object domain (e.g., "Hochbau", "Brücken")
    - "ifcClass" - Group by IFC classification
    - "propertySet" - Group by PropertySet names (one object can appear in multiple groups!)
    - "name" - Group by object name

    📊 MULTI-LEVEL GROUPING:
    - Single: group_by="domain" → {domain: [objects]}
    - Multiple: group_by=["domain", "ifcClass"] → {domain: {ifcClass: [objects]}}
    - Special case: "propertySet" can duplicate objects across groups

    🔤 SORTING:
    - sort_by="name" - Sort alphabetically by object name
    - sort_by="id" - Sort by object ID
    - sort_by="domain" - Sort by domain name
    - order="asc" or "desc"
    - Sorts within groups if grouped, or entire list if not grouped

    💡 USAGE PATTERNS:

    1. PURE SORTING (no grouping):
       {
         "object_ids": ["OBJ_1", "OBJ_2", "OBJ_3"],
         "group_by": null,
         "sort_by": "name",
         "order": "asc"
       }

    2. GROUPING ONLY:
       {
         "object_ids": ["OBJ_1", "OBJ_2", "OBJ_3"],
         "group_by": "domain",
         "include_count": true
       }

    3. MULTI-LEVEL GROUPING WITH SORTING:
       {
         "object_ids": ["OBJ_1", "OBJ_2", "OBJ_3"],
         "group_by": ["domain", "ifcClass"],
         "sort_by": "name",
         "order": "asc",
         "include_count": true
       }

    4. ANALYZE PROPERTY SETS ACROSS DOMAINS:
       {
         "object_ids": [...all IDs from search...],
         "group_by": ["domain", "propertySet"],
         "include_count": true
       }
       → Shows which PropertySets are used in which domains

    ⚙️ PARAMETERS:
    - object_ids: List of object IDs (1-500 max)
    - group_by: Field(s) to group by (string or list), or null for no grouping
    - sort_by: Field to sort by (name/id/domain), or null for no sorting
    - order: Sort order ("asc" or "desc")
    - include_count: Include count of objects per group
    - language: Language code (de/fr/it/en)
    - response_format: "markdown" or "json"

    📦 CACHING:
    Objects are fetched from cache first, then from API if needed.
    This tool respects the same caching strategy as get_object.

    ✅ RETURN VALUE:
    - Markdown: Hierarchical tree with indented groups and object lists
    - JSON: Nested dict structure with group_counts

    Both formats include:
    - total_objects: Total number of objects processed
    - groups: Grouped/sorted objects (structure depends on group_by)
    - group_counts: Flat dict with counts per group (if include_count=true)
    """
    try:
        use_case: GroupObjectsUseCase = _container.get_use_case(GroupObjectsUseCase)

        # Convert params to request
        request = GroupObjectsRequest(
            object_ids=params.object_ids,
            group_by=params.group_by,
            sort_by=params.sort_by,
            order=params.order,
            include_count=params.include_count,
            language=params.language,
        )

        # Execute use case
        response = await use_case.execute(request)

        # Format response
        if params.response_format == ResponseFormat.JSON:
            return _json_presenter.format_grouped_objects(response.result)
        else:
            return _markdown_presenter.format_grouped_objects(response.result)

    except Exception as e:
        await ctx.error(f"Failed to group objects: {e}")
        return f"Error grouping objects: {str(e)}"


if __name__ == "__main__":
    mcp.run()
