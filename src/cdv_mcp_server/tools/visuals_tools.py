## Copyright (c) 2025 Cloudera, Inc. All Rights Reserved.
##
## This file is licensed under the Apache License Version 2.0 (the "License").
## You may not use this file except in compliance with the License.
## You may obtain a copy of the License at http:##www.apache.org/licenses/LICENSE-2.0.
##
## This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
## OF ANY KIND, either express or implied. Refer to the License for the specific
## permissions and limitations governing your use of the file.

import json
from typing import Optional
from urllib.parse import urljoin

from cdv_mcp_server.tools.api_client import cdv_delete, cdv_get, cdv_post_admin, cdv_post_form, get_base_url

_BASE = "arc/adminapi/v1/visuals"

VALID_VISUAL_TYPES = {
    # Bar / line / area families
    "trellis-bars", "trellis-groupedbars", "trellis-lines", "trellis-areas",
    # Scatter / bubble
    "scatter", "packed-bubbles",
    # Pie / radial / chord
    "pie", "radial", "chord",
    # Maps
    "leaflet",
    # KPI / gauge / bullet
    "kpi", "gauge", "bullet",
    # Statistical
    "histogram", "boxplot",
    # Tabular
    "table", "crosstab", "sparklines",
    # Hierarchical / network
    "treemap", "dendrogram", "network",
    # Combo / flow
    "combo", "corelation", "corelation-flow",
    # Time
    "calendar-heatmap",
    # Dashboard container
    "dashboard",
}

VALID_AGGS = {"sum", "avg", "min", "max", "count"}


def list_visuals(dataset_id: int | None = None, workspace_id: int | None = None) -> str:
    params: dict = {}
    if dataset_id is not None:
        params["dataset_id"] = dataset_id
    if workspace_id is not None:
        params["workspace_id"] = workspace_id
    return cdv_get(_BASE, params=params or None)


def get_visual(object_id: int) -> str:
    return cdv_get(f"{_BASE}/{object_id}")


def create_visual(body: dict) -> str:
    """
    Create a visual using the raw admin API.
    Required body fields: title, type, dataset_id, workspace_id.
    Optional: description, data (visual spec JSON object), perm.
    """
    return cdv_post_admin(_BASE, body)


def update_visual(object_id: int, body: dict) -> str:
    return cdv_post_admin(f"{_BASE}/{object_id}", body)


def delete_visual(object_id: int) -> str:
    return cdv_delete(f"{_BASE}/{object_id}")


def create_smart_visual(
    dataset_id: str,
    visual_type: str,
    title: str,
    columns: list[dict],
    filters: Optional[list[dict]] = None,
) -> str:
    """
    Create a CDV visual using the Smart Visual API (arc/adminapi/v1/visuals/smart).

    Each entry in `columns` must have:
      - column_name (str, required)
      - aggregate_function (str, optional): sum | avg | min | max | count
        Columns with an aggregate_function are measures; without are dimensions.

    Returns the created visual metadata including id, visual_id, and url.
    """
    if not columns:
        return json.dumps({"error": "`columns` cannot be empty."})

    if visual_type not in VALID_VISUAL_TYPES:
        return json.dumps({"error": f"Invalid visual_type '{visual_type}'. Must be one of: {sorted(VALID_VISUAL_TYPES)}"})

    validated = []
    for col in columns:
        if "column_name" not in col:
            return json.dumps({"error": f"Each column must have a 'column_name'. Got: {col}"})
        agg = col.get("aggregate_function")
        if agg is not None and agg not in VALID_AGGS:
            return json.dumps({"error": f"Invalid aggregate_function '{agg}'. Must be one of: {sorted(VALID_AGGS)}"})
        entry: dict = {"column_name": col["column_name"]}
        if agg:
            entry["aggregate_function"] = agg
        validated.append(entry)

    data = {
        "dataset_id": str(dataset_id),
        "columns": json.dumps(validated),
        "filters": json.dumps(filters or []),
        "type": visual_type,
        "title": title,
    }

    result_text = cdv_post_form("arc/adminapi/v1/visuals/smart", data=data)
    try:
        result = json.loads(result_text)
        if isinstance(result, dict) and "id" in result:
            result["visual_id"] = result["id"]
            result["url"] = urljoin(get_base_url(), f"arc/apps/app/{result['id']}")
        return json.dumps(result)
    except Exception:
        return result_text
