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

# Maps aggregate_function name → CDV fn_type integer
_AGG_FN_TYPE: dict[str, int] = {
    "count": 1,
    "avg": 2,
    "sum": 3,
    "min": 4,
    "max": 5,
}


def _shelf_entry(col_name: str, agg: str | None = None) -> dict:
    """Build a single CDV shelf entry dict."""
    return {
        "dataset_colname": col_name,
        "col_alias": col_name,
        "fn_type": _AGG_FN_TYPE.get(agg, 0) if agg else 0,
        "fn_name": agg or "",
    }


def _build_report_data(visual_type: str, title: str, columns: list[dict]) -> dict:
    """
    Construct a CDV report_data payload from a normalised column list.

    Columns that carry an ``aggregate_function`` are treated as measures;
    all others are dimensions.  Shelf assignment depends on visual_type:

    * table / crosstab / sparklines — all columns on x_shelf
    * pie                           — dims on color_shelf, measures on theta_shelf
    * everything else               — dims on x_shelf, measures on y_shelf
    """
    dimensions = [_shelf_entry(c["column_name"]) for c in columns if not c.get("aggregate_function")]
    measures = [_shelf_entry(c["column_name"], c["aggregate_function"]) for c in columns if c.get("aggregate_function")]

    if visual_type in {"table", "crosstab", "sparklines"}:
        x_shelf, y_shelf, color_shelf, theta_shelf = dimensions + measures, [], [], []
    elif visual_type == "pie":
        x_shelf, y_shelf, color_shelf, theta_shelf = [], [], dimensions, measures
    else:
        x_shelf, y_shelf, color_shelf, theta_shelf = dimensions, measures, [], []

    report_data = {
        "report_title": title,
        "report_subtitle": "",
        "selected_segments": [],
        "filters_shelf": [],
        "x_shelf": x_shelf,
        "y_shelf": y_shelf,
        "color_shelf": color_shelf,
        "theta_shelf": theta_shelf,
        "tooltip_shelf": [],
        "dimensions_shelf": [],
        "aggregates_shelf": [],
        "sort_orders_asc": [],
        "limit": 50,
        "sample_pct": 100,
        "settings": {},
        "user_settings": {},
        "click_behaviors": [],
    }
    return {"report_data": report_data, "report_type": visual_type}


def _enrich_visual_response(result_text: str) -> str:
    """Attach ``visual_id`` and ``url`` fields to a visual API response when an ``id`` is present."""
    try:
        result = json.loads(result_text)
        if isinstance(result, list) and result:
            result = result[0]
        if isinstance(result, dict) and "id" in result and "error" not in result:
            result["visual_id"] = result["id"]
            try:
                result["url"] = urljoin(get_base_url(), f"arc/apps/app/{result['id']}")
            except Exception:
                pass
        return json.dumps(result)
    except Exception:
        return result_text


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
    return _enrich_visual_response(cdv_post_admin(_BASE, body))


def update_visual(object_id: int, body: dict) -> str:
    return _enrich_visual_response(cdv_post_admin(f"{_BASE}/{object_id}", body))


def delete_visual(object_id: int) -> str:
    return cdv_delete(f"{_BASE}/{object_id}")


def create_smart_visual(
    dataset_id: str,
    visual_type: str,
    title: str,
    columns: list[dict],
    filters: Optional[list[dict]] = None,
    workspace_id: Optional[int] = None,
) -> str:
    """
    Create a CDV visual using the Smart Visual API, with automatic fallback to the
    admin API when the Smart Visual endpoint is unavailable (HTTP 404).

    Each entry in `columns` must have:
      - column_name (str, required)
      - aggregate_function (str, optional): sum | avg | min | max | count
        Columns with an aggregate_function are treated as measures; without are dimensions.

    workspace_id is required when the Smart Visual API is unavailable so the fallback
    admin-API path can create the visual in the correct workspace.

    Returns the created visual's metadata including its id, visual_id, and url.
    """
    if not columns:
        return json.dumps({"error": "`columns` cannot be empty."})

    if visual_type not in VALID_VISUAL_TYPES:
        return json.dumps({"error": f"Invalid visual_type '{visual_type}'. Must be one of: {sorted(VALID_VISUAL_TYPES)}"})

    validated: list[dict] = []
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

    # --- Attempt the Smart Visual API endpoint first ---
    form_data = {
        "dataset_id": str(dataset_id),
        "columns": json.dumps(validated),
        "filters": json.dumps(filters or []),
        "type": visual_type,
        "title": title,
    }
    result_text = cdv_post_form("arc/adminapi/v1/visuals/smart", data=form_data)

    try:
        result = json.loads(result_text)
    except Exception:
        return result_text

    # If the Smart Visual endpoint is not available on this instance, fall back to
    # the standard admin API and build the report_data shelf spec ourselves.
    if isinstance(result, dict) and result.get("status_code") == 404:
        if workspace_id is None:
            return json.dumps({
                "error": (
                    "Smart Visual API is not available on this CDV instance (HTTP 404). "
                    "Please provide workspace_id so the fallback admin-API path can be used."
                ),
                "hint": "Call list_workspaces() to find the correct workspace_id, then retry with workspace_id set.",
            })

        data_spec = _build_report_data(visual_type, title, validated)
        body: dict = {
            "title": title,
            "type": visual_type,
            "description": "",
            "dataset_id": int(dataset_id),
            "workspace_id": workspace_id,
            "data": data_spec,
        }
        result_text = cdv_post_admin(_BASE, body)
        try:
            result = json.loads(result_text)
        except Exception:
            return result_text

    # Enrich the response with a direct URL regardless of which path was taken.
    if isinstance(result, list) and result:
        result = result[0]
    if isinstance(result, dict) and "id" in result and "error" not in result:
        result["visual_id"] = result["id"]
        result["url"] = urljoin(get_base_url(), f"arc/apps/app/{result['id']}")
    return json.dumps(result)
