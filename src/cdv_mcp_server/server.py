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

mcp = FastMCP(name="Cloudera Data Visualization MCP Server")

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
def create_user(body: dict) -> str:
    """
    Create a new CDV user.

    body fields: username, email, first_name, last_name, password, groups, roles.
    """
    return users_tools.create_user(body)


@mcp.tool()
def update_user(object_id: int, body: dict) -> str:
    """Update an existing CDV user by their numeric ID."""
    return users_tools.update_user(object_id, body)


@mcp.tool()
def delete_user(object_id: int) -> str:
    """Delete a CDV user by their numeric ID."""
    return users_tools.delete_user(object_id)


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
    """List all workspaces in CDV."""
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
    """List all datasets defined in CDV."""
    return datasets_tools.list_datasets()


@mcp.tool()
def get_dataset(object_id: int) -> str:
    """Get a single CDV dataset by its numeric ID."""
    return datasets_tools.get_dataset(object_id)


@mcp.tool()
def create_dataset(body: dict) -> str:
    """
    Create a new CDV dataset.

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
    List CDV visuals. Optionally filter by dataset_id or workspace_id.
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
    """Delete a CDV visual by its numeric ID."""
    return visuals_tools.delete_visual(object_id)


@mcp.tool()
def create_smart_visual(
    dataset_id: str,
    visual_type: str,
    title: str,
    columns: list[dict],
    filters: list[dict] | None = None,
) -> str:
    """
    Create a CDV visual using the Smart Visual API.

    visual_type must be one of:
      trellis-bars, trellis-groupedbars, trellis-lines, trellis-areas,
      scatter, packed-bubbles, pie, radial, chord, leaflet,
      kpi, gauge, bullet, histogram, boxplot,
      table, crosstab, sparklines, treemap, dendrogram, network,
      combo, corelation, corelation-flow, calendar-heatmap, dashboard.

    Each entry in columns must have:
      - column_name (str, required): the dataset column to use
      - aggregate_function (str, optional): sum | avg | min | max | count
        Columns with an aggregate_function are treated as measures; without are dimensions.

    filters is an optional list of filter definitions (defaults to no filters).

    Returns the created visual's metadata including its id, visual_id, and url.
    """
    return visuals_tools.create_smart_visual(dataset_id, visual_type, title, columns, filters)


# ---------------------------------------------------------------------------
# Connections
# ---------------------------------------------------------------------------


@mcp.tool()
def list_connections() -> str:
    """List all data connections defined in CDV."""
    return connections_tools.list_connections()


@mcp.tool()
def get_connection(object_id: int) -> str:
    """Get a single CDV data connection by its numeric ID."""
    return connections_tools.get_connection(object_id)


@mcp.tool()
def create_connection(body: dict) -> str:
    """
    Create a new CDV data connection.

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
    Query data via the CDV Data API (/apps/dataapi).

    Dataset-based querying: provide dataset (ID), optionally limit,
    dimensions (comma-separated column names), aggregates (comma-separated expressions),
    filters (comma-separated filter expressions).

    Connection-based querying: provide dataconnection_id and a SQL query string.
    """
    return data_api_tools.query_dataapi_get(
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
