## Copyright (c) 2025 Cloudera, Inc. All Rights Reserved.
##
## This file is licensed under the Apache License Version 2.0 (the "License").
## You may not use this file except in compliance with the License.
## You may obtain a copy of the License at http:##www.apache.org/licenses/LICENSE-2.0.
##
## This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
## OF ANY KIND, either express or implied. Refer to the License for the specific
## permissions and limitations governing your use of the file.

import os

from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

from cdv_mcp_server.tools import (
    connections_tools,
    data_api_tools,
    datasets_tools,
    debugging_tools,
    filter_associations_tools,
    groups_tools,
    jobs_tools,
    migrations_tools,
    roles_tools,
    segments_tools,
    users_tools,
    visuals_tools,
    workspaces_tools,
)

mcp = FastMCP(
    name="Cloudera Data Visualization MCP Server",
    instructions="""
You are connected to a Cloudera Data Visualization (CDV) instance.  CDV lets you
explore data, create charts, and build dashboards on top of Impala/Hive data sources.

═══════════════════════════════════════════════════════════════════
MANDATORY WORKFLOW — follow this sequence for EVERY data question
═══════════════════════════════════════════════════════════════════

STEP 1 ─ Discover data sources
  Call: list_connections()
  Why:  Reveals available databases (e.g. Impala, Hive).
        The connection ID (dc_id) is needed for raw SQL queries and dataset creation.

STEP 2 ─ Discover existing datasets
  Call: list_datasets()
  Why:  Datasets are the named tables/views that CDV charts are built on.
        Always re-use an existing dataset; only call create_dataset() if
        the user explicitly asks for a new one AND none exists for that table.

STEP 3 ─ Explore table columns and data
  Call: query_dataapi(dataconnection_id=<dc_id>, query="SELECT * FROM schema.table LIMIT 5")
  Why:  You need the exact column names before creating any visual or answering
        any data question.  Column names are case-sensitive and CDV is strict.
        NOTE: SQL reserved words (date, time, etc.) must be backtick-quoted in queries.

STEP 4 ─ Get the workspace ID
  Call: list_workspaces()
  Why:  workspace_id is REQUIRED by create_smart_visual(). Without it the visual
        cannot be created.  Choose the workspace that matches the project context
        (e.g. "Logistics MCP Demo" or "Public").

STEP 5 ─ Answer filtered/aggregated questions with query_dataapi
  Call: query_dataapi(dataconnection_id=<dc_id>, query="SELECT ... WHERE ...")
  Why:  create_smart_visual() does NOT support filters — CDV generates invalid SQL
        for chart-level filters via the API.  For questions that require filtering
        (e.g. "for Mock Vendor X only"), ALWAYS use query_dataapi to get the data
        and present it as a table or Plotly visualization in your response.

STEP 6 ─ Create CDV chart visuals (unfiltered overviews)
  Call: create_smart_visual(dataset_id=<id>, visual_type=<type>, title=<title>,
                             columns=[...], workspace_id=<id>)
  Why:  Creates a persistent chart in CDV that users can interact with.
        Only the following visual types are supported via the API:
          • trellis-bars       — bar chart (one measure vs. one dimension)
          • trellis-groupedbars — grouped/stacked bars (one SUM + color dimension)
          • pie                — pie chart (one SUM + one dimension)
        ALL other chart types require CDV's interactive builder.
        
  Column rules:
    ✓ Use sum, avg, min, max as aggregate_function (count is NOT supported)
    ✓ Use simple STRING columns as dimensions (supplier_name, item_description, etc.)
    ✗ Do NOT use columns whose names start with avg_, sum_, min_, max_, count_
      as aggregate targets (CDV tokenizer bug — they will fail)
    ✗ Do NOT use date/timestamp columns as dimensions (CDV bracket conversion fails)
    ✗ Do NOT pass filters — use query_dataapi for filtered data instead

STEP 7 ─ Make charts visible — always create a dashboard
  Call: create_dashboard(title=<title>, workspace_id=<id>, visual_ids=[<id1>, <id2>...],
                         dataset_id=<primary_dataset_id>)
  Why:  Chart visuals created via create_smart_visual() are INVISIBLE in the CDV UI
        until they are placed inside a dashboard.  This step is MANDATORY.
        WARNING: Deleting a dashboard also permanently deletes all its linked charts.
        Save the visual IDs before deleting anything.

═══════════════════════════════════════════════════════════════════
DECISION TREE — which tool to use
═══════════════════════════════════════════════════════════════════

Question with a filter ("for Vendor X", "only Turbine Oil", etc.)
  → query_dataapi (run SQL with WHERE clause) + present data as table/Plotly
  → create_smart_visual for the unfiltered overview chart

Time-series question ("price trend", "over time")
  → query_dataapi to get the time-series data (present as table or Plotly)
  → Do NOT try create_smart_visual for time-series (date dimensions fail via API)

Heatmap or cross-tab question
  → query_dataapi to get the pivot data, format it for Plotly in your response
  → Do NOT try to create a heatmap in CDV via the API (not supported)

Aggregated overview (top suppliers, spend by category, etc.)
  → create_smart_visual with trellis-bars or trellis-groupedbars

Proportion/breakdown question ("what % of spend")
  → create_smart_visual with pie, OR query_dataapi for the numbers

═══════════════════════════════════════════════════════════════════
IMPORTANT — NEVER assume; always discover first
═══════════════════════════════════════════════════════════════════

• Never guess dataset_id, workspace_id, column names, or table names.
• Always run Steps 1–4 before creating any visual.
• If create_smart_visual returns an error about a column or visual type,
  read the error's "guidance" field — it tells you exactly what to change.
• The user cannot see the chart until you call create_dashboard.
""",
)

# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------


@mcp.tool()
def list_groups() -> str:
    """List all groups defined in CDV."""
    return groups_tools.list_groups()


@mcp.tool()
def get_group(object_id: int) -> str:
    """Get a single CDV group by its numeric ID."""
    return groups_tools.get_group(object_id)


@mcp.tool()
def create_group(body: dict) -> str:
    """
    Create a new CDV group.

    body fields:
      - name (str, required): group name
      - users (list[{id: int}], optional): list of user IDs to add
    """
    return groups_tools.create_group(body)


@mcp.tool()
def update_group(object_id: int, body: dict) -> str:
    """Update an existing CDV group by its numeric ID. Provide fields to change (e.g. name, users)."""
    return groups_tools.update_group(object_id, body)


@mcp.tool()
def delete_group(object_id: int) -> str:
    """Delete a CDV group by its numeric ID."""
    return groups_tools.delete_group(object_id)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


@mcp.tool()
def list_users() -> str:
    """List all users defined in CDV."""
    return users_tools.list_users()


@mcp.tool()
def get_user(object_id: int) -> str:
    """Get a single CDV user by their numeric ID."""
    return users_tools.get_user(object_id)


@mcp.tool()
def update_user(object_id: int, body: dict) -> str:
    """Update an existing CDV user by their numeric ID."""
    return users_tools.update_user(object_id, body)


@mcp.tool()
def edit_user_profile(username: str, body: dict) -> str:
    """Edit the profile of a CDV user identified by username (e.g. update email, name)."""
    return users_tools.edit_user_profile(username, body)


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------


@mcp.tool()
def list_roles() -> str:
    """List all roles defined in CDV."""
    return roles_tools.list_roles()


@mcp.tool()
def get_role(object_id: int) -> str:
    """Get a single CDV role by its numeric ID."""
    return roles_tools.get_role(object_id)


@mcp.tool()
def create_role(body: dict) -> str:
    """Create a new CDV role. body fields: name, permissions (list)."""
    return roles_tools.create_role(body)


@mcp.tool()
def update_role(object_id: int, body: dict) -> str:
    """Update an existing CDV role by its numeric ID."""
    return roles_tools.update_role(object_id, body)


@mcp.tool()
def delete_role(object_id: int) -> str:
    """Delete a CDV role by its numeric ID."""
    return roles_tools.delete_role(object_id)


# ---------------------------------------------------------------------------
# Segments
# ---------------------------------------------------------------------------


@mcp.tool()
def list_segments() -> str:
    """List all row-level security segments defined in CDV."""
    return segments_tools.list_segments()


@mcp.tool()
def get_segment(object_id: int) -> str:
    """Get a single CDV segment by its numeric ID."""
    return segments_tools.get_segment(object_id)


@mcp.tool()
def create_segment(body: dict) -> str:
    """Create a new CDV row-level security segment. body fields: name, filter_definition."""
    return segments_tools.create_segment(body)


@mcp.tool()
def update_segment(object_id: int, body: dict) -> str:
    """Update an existing CDV segment by its numeric ID."""
    return segments_tools.update_segment(object_id, body)


@mcp.tool()
def delete_segment(object_id: int) -> str:
    """Delete a CDV segment by its numeric ID."""
    return segments_tools.delete_segment(object_id)


# ---------------------------------------------------------------------------
# Filter Associations
# ---------------------------------------------------------------------------


@mcp.tool()
def list_filter_associations() -> str:
    """List all filter associations (segment-to-user/group mappings) defined in CDV."""
    return filter_associations_tools.list_filter_associations()


@mcp.tool()
def get_filter_association(object_id: int) -> str:
    """Get a single CDV filter association by its numeric ID."""
    return filter_associations_tools.get_filter_association(object_id)


@mcp.tool()
def create_filter_association(body: dict) -> str:
    """Create a new CDV filter association linking a segment to users or groups."""
    return filter_associations_tools.create_filter_association(body)


@mcp.tool()
def update_filter_association(object_id: int, body: dict) -> str:
    """Update an existing CDV filter association by its numeric ID."""
    return filter_associations_tools.update_filter_association(object_id, body)


@mcp.tool()
def delete_filter_association(object_id: int) -> str:
    """Delete a CDV filter association by its numeric ID."""
    return filter_associations_tools.delete_filter_association(object_id)


# ---------------------------------------------------------------------------
# Workspaces
# ---------------------------------------------------------------------------


@mcp.tool()
def list_workspaces() -> str:
    """
    STEP 4 of every visualization workflow — get the workspace_id required by create_smart_visual.

    CDV workspaces organize visuals and dashboards (similar to folders).
    The workspace_id returned here is a REQUIRED parameter for create_smart_visual()
    and create_dashboard().  Without it, visual creation will fail.

    Call this before creating any visual.  Choose the workspace that matches the
    project context (e.g. a dedicated project workspace or "Public").
    """
    return workspaces_tools.list_workspaces()


@mcp.tool()
def get_workspace(object_id: int) -> str:
    """Get a single CDV workspace by its numeric ID."""
    return workspaces_tools.get_workspace(object_id)


@mcp.tool()
def create_workspace(body: dict) -> str:
    """
    Create a new CDV workspace.

    body fields: name (str), desc (str), editable (bool), perms (list[str]),
    acl (list of [entry_type, permission, name] triplets).
    """
    return workspaces_tools.create_workspace(body)


@mcp.tool()
def update_workspace(object_id: int, body: dict) -> str:
    """Update an existing CDV workspace by its numeric ID."""
    return workspaces_tools.update_workspace(object_id, body)


@mcp.tool()
def delete_workspace(object_id: int) -> str:
    """Delete a CDV workspace by its numeric ID."""
    return workspaces_tools.delete_workspace(object_id)


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------


@mcp.tool()
def list_datasets() -> str:
    """
    STEP 2 of the workflow — list all datasets (named tables/views) available in CDV.

    In CDV: Connection → Dataset → Visual → Dashboard
    A dataset is a named pointer to a specific table or SQL query within a connection.
    Visuals and dashboards are built on datasets (using their numeric dataset_id).

    AFTER calling this tool, you will have dataset names and IDs, but NOT column names.
    ALWAYS follow up with:
      query_dataapi(dataconnection_id=<dc_id>, query="SELECT * FROM <schema.table> LIMIT 3")
    to discover the exact column names before creating any visual.

    Workflow reminder:
      1. list_connections()  → find dc_id (connection ID for SQL queries)
      2. list_datasets()     → find dataset_id and table name (THIS TOOL)
      3. query_dataapi(...)  → discover column names and sample data  ← DO THIS NEXT
      4. list_workspaces()   → find workspace_id for visual creation
      5. create_smart_visual(...)
      6. create_dashboard(...)

    Only call create_dataset() if no suitable dataset exists AND the user explicitly
    confirms they want a new one.  Always confirm with the user before creating anything.
    """
    return datasets_tools.list_datasets()


@mcp.tool()
def get_dataset(object_id: int) -> str:
    """Get a single CDV dataset by its numeric ID."""
    return datasets_tools.get_dataset(object_id)


@mcp.tool()
def create_dataset(body: dict) -> str:
    """
    Create a new CDV dataset backed by an existing data connection.

    A dataset points to a specific table or SQL query within a connection (dc_id).
    Visuals and dashboards are built on top of datasets.

    IMPORTANT: Do NOT call this without first calling list_connections() to identify
    the right connection (dc_id) and list_datasets() to confirm no suitable dataset
    already exists.  Always get explicit user confirmation before creating a new dataset.

    body fields: dc_id (int), name (str), type (str), detail (str, e.g. schema.table),
    description (str), info (object), lvname (str), settings (object).
    """
    return datasets_tools.create_dataset(body)


@mcp.tool()
def update_dataset(object_id: int, body: dict) -> str:
    """Update an existing CDV dataset by its numeric ID."""
    return datasets_tools.update_dataset(object_id, body)


@mcp.tool()
def delete_dataset(object_id: int) -> str:
    """Delete a CDV dataset by its numeric ID."""
    return datasets_tools.delete_dataset(object_id)


# ---------------------------------------------------------------------------
# Visuals
# ---------------------------------------------------------------------------


@mcp.tool()
def list_visuals(dataset_id: int | None = None, workspace_id: int | None = None) -> str:
    """
    List CDV visuals (dashboards). Optionally filter by dataset_id or workspace_id.

    IMPORTANT — CDV API LIMITATION:
    This endpoint only returns dashboard-type visuals (type="dashboard").
    Standalone chart visuals created via create_smart_visual() are NOT included in this
    listing even when they exist in the workspace.

    To work with standalone chart visuals:
      - Use get_visual(object_id) with the id returned when the visual was created.
      - Use create_dashboard() to group multiple chart visuals into a visible dashboard.

    After creating chart visuals with create_smart_visual(), always call create_dashboard()
    to combine them into a single navigable dashboard so the user can see them in the CDV UI.
    """
    return visuals_tools.list_visuals(dataset_id=dataset_id, workspace_id=workspace_id)


@mcp.tool()
def get_visual(object_id: int) -> str:
    """Get a single CDV visual by its numeric ID."""
    return visuals_tools.get_visual(object_id)


@mcp.tool()
def create_visual(body: dict) -> str:
    """
    Create a CDV visual using the raw admin API.

    Required body fields: title (str), type (str), dataset_id (int), workspace_id (int).
    Optional: description (str), data (object — visual spec), perm (list[str]).
    """
    return visuals_tools.create_visual(body)


@mcp.tool()
def update_visual(object_id: int, body: dict) -> str:
    """Update an existing CDV visual by its numeric ID."""
    return visuals_tools.update_visual(object_id, body)


@mcp.tool()
def delete_visual(object_id: int) -> str:
    """
    Delete a CDV visual or dashboard by its numeric ID.

    WARNING — CASCADE DELETION: Deleting a dashboard (type="dashboard") also
    permanently deletes ALL chart visuals linked to it as widgets.  If you need
    to preserve the chart visuals, note their IDs before deleting the dashboard.
    """
    return visuals_tools.delete_visual(object_id)


@mcp.tool()
def create_dashboard(
    title: str,
    workspace_id: int,
    visual_ids: list[int],
    dataset_id: int | None = None,
    description: str = "",
) -> str:
    """
    Create a CDV dashboard that groups one or more chart visuals into a single visible view.

    Use this tool after create_smart_visual() to make charts visible in the CDV workspace UI.
    Chart visuals created via the API are standalone artifacts; they only appear in the
    CDV workspace when placed inside a dashboard.

    visual_ids: list of visual IDs to include (in display order, left-to-right, top-to-bottom).
                Record these IDs — deleting the dashboard also deletes all linked visuals.
    workspace_id: the workspace where the dashboard will be created (from list_workspaces()).
    dataset_id: optional — the primary dataset for the dashboard (for global filter context).
                Use the dataset_id shared by most of the included visuals.
    description: optional short description shown in the workspace.

    Visuals are automatically tiled in a 2-column grid.  Odd trailing visuals span full width.

    WARNING: Deleting a dashboard (via delete_visual) permanently deletes all linked chart
    visuals.  Always save the visual IDs before deleting a dashboard.

    Returns the new dashboard's id and url.

    Example workflow:
      1. call list_workspaces()               → choose workspace_id
      2. call list_datasets()                 → confirm dataset_id with the user
      3. call create_smart_visual() × N       → collect visual_ids
      4. call create_dashboard(title="My Dashboard", workspace_id=4,
                               visual_ids=[131, 132, 133], dataset_id=12)
    """
    return visuals_tools.create_dashboard(
        title=title,
        workspace_id=workspace_id,
        visual_ids=visual_ids,
        dataset_id=dataset_id,
        description=description,
    )


@mcp.tool()
def create_smart_visual(
    dataset_id: str,
    visual_type: str,
    title: str,
    columns: list[dict],
    workspace_id: int | None = None,
) -> str:
    """
    Create a CDV chart visual that reliably renders data without SQL errors.

    This tool only exposes visual types and column configurations that are
    confirmed to work through the CDV API.  Unsupported patterns are rejected
    with a clear error and guidance on what to use instead.

    SUPPORTED visual_type values:
      - "trellis-bars"       Best for one measure vs. one dimension (horizontal bars).
      - "trellis-groupedbars" One SUM measure grouped by a color dimension.
      - "pie"                One SUM measure broken down by one dimension.

    NOT SUPPORTED via this tool (use CDV's interactive builder instead):
      - trellis-lines, trellis-areas  (time-series; timestamp dimensions fail via API)
      - scatter, histogram, boxplot   (require CDV builder shelf configuration)
      - table, crosstab               (use query_dataapi for tabular results)
      - All other chart types

    Each entry in columns must have:
      - column_name (str, required): exact column name in the dataset.
      - aggregate_function (str, optional): sum | avg | min | max
        Columns WITH this field are measures; columns WITHOUT are dimensions.
        IMPORTANT: "count" is not supported — use "sum" on a numeric column instead.
      - shelf (str, optional): explicit shelf override.
        Use "color_shelf" to add a grouping/color dimension to bar or pie charts.

    COLUMN COMPATIBILITY RULES (enforced, CDV-side constraints):
      - At least one measure (column with aggregate_function) is required.
      - Column names that start with avg_, sum_, min_, max_, count_ CANNOT be
        used as aggregate targets (CDV's tokenizer confuses them with functions).
        Example: avg(avg_lead_time_days) fails. Use a different column.
      - Date/timestamp columns (names with "date", "time", "year", etc.) should
        NOT be used as dimensions — CDV fails to generate valid SQL for them.
        Use CDV's builder for time-series charts.

    FILTERS ARE NOT SUPPORTED:
      CDV's filter SQL generation always produces bracket notation in the WHERE
      clause that Impala cannot parse.  After creating the visual, open it in
      CDV's interactive builder to add filters manually.

    EXAMPLES:

      Total spend by supplier (bar chart):
        columns=[
          {"column_name": "supplier_name"},
          {"column_name": "total_price", "aggregate_function": "sum"},
        ]

      Supplier spend grouped by priority (grouped bar):
        visual_type="trellis-groupedbars",
        columns=[
          {"column_name": "supplier_name"},
          {"column_name": "priority_code", "shelf": "color_shelf"},
          {"column_name": "total_price", "aggregate_function": "sum"},
        ]

      Spend breakdown by item (pie chart):
        visual_type="pie",
        columns=[
          {"column_name": "item_description"},
          {"column_name": "total_price", "aggregate_function": "sum"},
        ]

    VISIBILITY: Chart visuals do NOT appear in the CDV workspace until you call
    create_dashboard() with their IDs.  Always follow up with create_dashboard().

    Returns the created visual's metadata including its id, visual_id, and url.
    """
    return visuals_tools.create_smart_visual(dataset_id, visual_type, title, columns, workspace_id)


# ---------------------------------------------------------------------------
# Connections
# ---------------------------------------------------------------------------


@mcp.tool()
def list_connections() -> str:
    """
    STEP 1 of every data workflow — list all CDV data connections.

    A data connection is the top-level link to an external database (Impala, Hive, etc.).
    The connection's numeric ID (dc_id / dataconnection_id) is used when:
      • Querying raw SQL via query_dataapi(dataconnection_id=<id>, query="SELECT ...")
      • Creating a new dataset with create_dataset(body={"dc_id": <id>, ...})

    WORKFLOW — always run this FIRST, then:
      1. list_connections()           → identify the right connection and its ID
      2. list_datasets()              → find existing datasets built on that connection
      3. query_dataapi(...)           → explore table columns and sample data
      4. list_workspaces()            → get workspace_id for visual creation
      5. create_smart_visual(...)     → create charts
      6. create_dashboard(...)        → make charts visible in CDV

    Never create a new connection unless the user explicitly requests it and no
    existing connection points to their data source.
    """
    return connections_tools.list_connections()


@mcp.tool()
def get_connection(object_id: int) -> str:
    """Get a single CDV data connection by its numeric ID."""
    return connections_tools.get_connection(object_id)


@mcp.tool()
def create_connection(body: dict) -> str:
    """
    Create a new CDV data connection.

    IMPORTANT: Do NOT call this without first calling list_connections() and confirming
    with the user that no existing connection points to their target data source.

    body fields: name (str), type (str), connection_info (object with host, port, etc.).
    """
    return connections_tools.create_connection(body)


@mcp.tool()
def update_connection(object_id: int, body: dict) -> str:
    """Update an existing CDV data connection by its numeric ID."""
    return connections_tools.update_connection(object_id, body)


@mcp.tool()
def delete_connection(object_id: int) -> str:
    """Delete a CDV data connection by its numeric ID."""
    return connections_tools.delete_connection(object_id)


@mcp.tool()
def export_connection(object_id: int) -> str:
    """Export a CDV data connection definition by its numeric ID."""
    return connections_tools.export_connection(object_id)


# ---------------------------------------------------------------------------
# Migrations
# ---------------------------------------------------------------------------


@mcp.tool()
def export_migration() -> str:
    """Export all CDV visual artifacts (dashboards, datasets, connections) as a migration bundle."""
    return migrations_tools.export_migration()


@mcp.tool()
def import_migration(dataconnection_name: str, json_data: str | None = None, sanity_check: bool = True) -> str:
    """
    Import a CDV migration bundle.

    Args:
        dataconnection_name: Name of the data connection to associate imported artifacts with.
        json_data: Stringified JSON migration payload.
        sanity_check: Run validation before import (default True).
    """
    return migrations_tools.import_migration(dataconnection_name, json_data, sanity_check)


# ---------------------------------------------------------------------------
# Data API
# ---------------------------------------------------------------------------


@mcp.tool()
def query_dataapi(
    dataset: int | None = None,
    dataconnection_id: int | None = None,
    query: str | None = None,
    limit: int | None = None,
    dimensions: str | None = None,
    aggregates: str | None = None,
    filters: str | None = None,
) -> str:
    """
    STEP 3 & 5 of the workflow — explore columns, answer filtered questions, get raw data.

    This is the MOST IMPORTANT tool for data exploration and filtered analysis.
    It runs arbitrary SQL against the database and returns structured results.

    Returns: {"columns": [...], "rows": [{col: val}, ...]}

    ══ USE THIS TOOL FOR ══════════════════════════════════════════════════════

    1. COLUMN DISCOVERY (Step 3) — always do this before creating any visual:
       query_dataapi(dataconnection_id=10,
                     query="SELECT * FROM schema.table_name LIMIT 3")
       → reveals exact column names, data types, and sample values.
       → column names are case-sensitive; use EXACTLY as returned here.

    2. FILTERED QUESTIONS — when the user asks about a specific subset of data:
       "Show shipping codes for Mock Vendor X"
       "What is Turbine Oil's price trend?"
       "Which priority-1 orders are overdue?"
       → create_smart_visual() CANNOT apply filters (CDV API limitation).
       → Use this tool with a WHERE clause instead, then present results as a table.

    3. COUNT / FREQUENCY questions — when the user wants counts:
       "What are the most common shipping codes?"
       → create_smart_visual() does NOT support COUNT aggregation.
       → Use this tool: query="SELECT col, COUNT(*) as cnt FROM ... GROUP BY col ORDER BY cnt DESC"

    4. TIME-SERIES queries — price trends, monthly patterns, etc.:
       → Time-based CDV visuals are blocked via the API.
       → Use this tool to fetch the trend data, then describe it or format it for Plotly.

    5. HEATMAPS / CROSS-TABS — e.g. "spend by destination and shipping code":
       → CDV has no heatmap type via the API.
       → Use this tool to get the pivot data, format it for plotly.graph_objects.Heatmap.

    ══ HOW TO USE ═════════════════════════════════════════════════════════════

    Connection-based SQL (RECOMMENDED — most flexible):
      query_dataapi(dataconnection_id=<id_from_list_connections>,
                    query="SELECT col1, SUM(col2) FROM schema.table WHERE col3='val'
                           GROUP BY col1 ORDER BY 2 DESC LIMIT 20")

    Important SQL notes:
      • Table names use schema.table format (e.g. logistics.procurement_transactions)
      • SQL reserved words (date, time, year, etc.) must be backtick-quoted:
        ✓ SELECT `date`, `time` FROM ...   NOT: SELECT date, time FROM ...
      • Use standard Impala/Hive SQL syntax

    Dataset-based query (simpler, but less flexible):
      query_dataapi(dataset=<id_from_list_datasets>,
                    dimensions="col1,col2", aggregates="SUM(col3) as total", limit=20)
    """
    return data_api_tools.query_dataapi_post(
        dataset=dataset,
        dataconnection_id=dataconnection_id,
        query=query,
        limit=limit,
        dimensions=dimensions,
        aggregates=aggregates,
        filters=filters,
    )


@mcp.tool()
def query_enhanced_data_api(
    version: str,
    dataset: int | None = None,
    dsreq: str | None = None,
    limit: int | None = None,
    dimensions: str | None = None,
    aggregates: str | None = None,
) -> str:
    """
    Query data via the CDV Enhanced Data API (/api/data).

    version: '0' for legacy API (provide dataset, limit, dimensions, aggregates),
             '1' for enhanced API (provide dsreq — a JSON-formatted dataset request string).
    """
    return data_api_tools.query_enhanced_data_api_get(
        version=version,
        dataset=dataset,
        dsreq=dsreq,
        limit=limit,
        dimensions=dimensions,
        aggregates=aggregates,
    )


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------


@mcp.tool()
def run_job(schedule_ids: str | None = None, schedule_names: str | None = None) -> str:
    """
    Trigger a rerun of one or more CDV scheduled jobs.
    Provide exactly one of schedule_ids (comma-separated IDs) or schedule_names (comma-separated names).
    """
    return jobs_tools.run_job(schedule_ids=schedule_ids, schedule_names=schedule_names)


@mcp.tool()
def run_extract(extract_ids: str) -> str:
    """Run one or more CDV data extract jobs by their comma-separated IDs."""
    return jobs_tools.run_extract(extract_ids)


@mcp.tool()
def create_extract(
    src_dataset_id: int,
    tgt_dataconnection_id: int,
    tgt_dbname: str,
    tgt_tablename: str,
    dim_data: str,
    agg_data: str,
    partition_data: str = "[]",
    schedule_id: int | None = None,
) -> str:
    """
    Create a CDV data extract job.

    Args:
        src_dataset_id: Source dataset ID.
        tgt_dataconnection_id: Target data connection ID.
        tgt_dbname: Target database name.
        tgt_tablename: Target table name.
        dim_data: JSON string of dimension columns, e.g. '[{"expr":"[col]","alias":"col"}]'.
        agg_data: JSON string of aggregate columns, e.g. '[{"expr":"sum([col])","alias":"col"}]'.
        partition_data: JSON string of partition columns for incremental refresh (default '[]').
        schedule_id: Optional schedule ID to attach a job to the extract.
    """
    return jobs_tools.create_extract(
        src_dataset_id=src_dataset_id,
        tgt_dataconnection_id=tgt_dataconnection_id,
        tgt_dbname=tgt_dbname,
        tgt_tablename=tgt_tablename,
        dim_data=dim_data,
        agg_data=agg_data,
        partition_data=partition_data,
        schedule_id=schedule_id,
    )


# ---------------------------------------------------------------------------
# Debugging / Operations
# ---------------------------------------------------------------------------


@mcp.tool()
def get_gc_monitor() -> str:
    """Check whether GC monitoring is currently enabled on the CDV server."""
    return debugging_tools.get_gc_monitor()


@mcp.tool()
def set_gc_monitor(enabled: bool) -> str:
    """Enable or disable GC monitoring on the CDV server."""
    return debugging_tools.set_gc_monitor(enabled)


@mcp.tool()
def get_gc_stats() -> str:
    """Retrieve the current GC debug flags from the CDV server."""
    return debugging_tools.get_gc_stats()


@mcp.tool()
def set_gc_stats(debug_flags: str) -> str:
    """Set GC debug flags on the CDV server. Requires sys_viewlogs permission."""
    return debugging_tools.set_gc_stats(debug_flags)


@mcp.tool()
def get_log_levels() -> str:
    """Retrieve the current log level for the root logger on the CDV server."""
    return debugging_tools.get_log_levels()


@mcp.tool()
def set_log_level(level: str) -> str:
    """
    Set the log level for the root logger. Requires sys_viewlogs permission.
    level must be one of: CRITICAL, DEBUG, ERROR, FATAL, INFO, WARN, WARNING.
    """
    return debugging_tools.set_log_level(level)


@mcp.tool()
def get_logger_level(logger_name: str) -> str:
    """Retrieve the current log level for a specific logger by name."""
    return debugging_tools.get_logger_level(logger_name)


@mcp.tool()
def set_logger_level(logger_name: str, level: str) -> str:
    """
    Set the log level for a specific named logger. Requires sys_viewlogs permission.
    level must be one of: CRITICAL, DEBUG, ERROR, FATAL, INFO, WARN, WARNING.
    """
    return debugging_tools.set_logger_level(logger_name, level)


@mcp.tool()
def get_toggle_cprofile(
    module: str | None = None,
    owner: str | None = None,
    func: str | None = None,
) -> str:
    """
    Check whether cProfile profiling is enabled for a CDV server function.
    Defaults to sqlrun.views_jsonselect / jsonselect_parallel if not specified.
    """
    return debugging_tools.get_toggle_cprofile(module=module, owner=owner, func=func)


@mcp.tool()
def toggle_cprofile(
    module: str | None = None,
    owner: str | None = None,
    func: str | None = None,
    strip_dirnames: str | None = None,
    print_callees: str | None = None,
    print_callers: str | None = None,
) -> str:
    """
    Toggle cProfile profiling on/off for a CDV server function. Requires sys_viewlogs permission.
    If profiling is already enabled, calling this disables it.
    strip_dirnames, print_callees, print_callers: 'yes' or 'no'.
    """
    return debugging_tools.toggle_cprofile(
        module=module,
        owner=owner,
        func=func,
        strip_dirnames=strip_dirnames,
        print_callees=print_callees,
        print_callers=print_callers,
    )


@mcp.tool()
def reset_dataset_cache(dataset_id: int) -> str:
    """Reset the query result cache for a specific CDV dataset. Requires ds_manage permission."""
    return debugging_tools.reset_dataset_cache(dataset_id)


@mcp.tool()
def reset_dataconnection_cache(connection_id: int) -> str:
    """Reset the query result cache for a specific CDV data connection. Requires ds_manage permission."""
    return debugging_tools.reset_dataconnection_cache(connection_id)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    print(f"Starting Cloudera Data Visualization MCP Server via transport: {transport}")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
