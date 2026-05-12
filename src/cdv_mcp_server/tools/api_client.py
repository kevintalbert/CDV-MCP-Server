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
import os
from urllib.parse import urljoin

import requests


def get_base_url() -> str:
    base_url = os.getenv("CDV_BASE_URL", "")
    if not base_url:
        raise ValueError("CDV_BASE_URL environment variable is not set.")
    return base_url.rstrip("/") + "/"


def get_api_key() -> str:
    api_key = os.getenv("CDV_API_KEY", "")
    if not api_key:
        raise ValueError("CDV_API_KEY environment variable is not set.")
    return api_key


def _json_headers() -> dict:
    return {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"apikey {get_api_key()}",
    }


def _form_headers() -> dict:
    return {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"apikey {get_api_key()}",
    }


def _build_url(path: str) -> str:
    """Resolve a CDV API path against the base URL.
    Paths should include the arc/ prefix, e.g. 'arc/adminapi/v1/groups'.
    """
    return urljoin(get_base_url(), path.lstrip("/"))


# ---------------------------------------------------------------------------
# GET — standard query params
# ---------------------------------------------------------------------------


def cdv_get(path: str, params: dict | None = None) -> str:
    try:
        response = requests.get(_build_url(path), headers=_json_headers(), params=params, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.HTTPError as e:
        return json.dumps({"error": str(e), "status_code": e.response.status_code, "detail": e.response.text})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# POST for admin CRUD — body wrapped in JSON array, sent as form `data` field
# CDV admin API pattern: POST data='[{...object...}]'
# ---------------------------------------------------------------------------


def cdv_post_admin(path: str, body: dict) -> str:
    """
    POST to a CDV admin CRUD endpoint.
    The body dict is wrapped in a JSON array and sent as the form `data` field,
    matching CDV's required request format for create/update operations.
    """
    try:
        form_data = {"data": json.dumps([body])}
        response = requests.post(_build_url(path), headers=_form_headers(), data=form_data, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.HTTPError as e:
        return json.dumps({"error": str(e), "status_code": e.response.status_code, "detail": e.response.text})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# POST for non-CRUD endpoints — form fields passed directly (no data array)
# Used by: data API, jobs, debugging endpoints
# ---------------------------------------------------------------------------


def cdv_post_form(path: str, data: dict) -> str:
    """POST with form-encoded fields sent directly (not wrapped in a data array)."""
    try:
        response = requests.post(_build_url(path), headers=_form_headers(), data=data, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.HTTPError as e:
        return json.dumps({"error": str(e), "status_code": e.response.status_code, "detail": e.response.text})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# POST for migration — multipart/form-data
# ---------------------------------------------------------------------------


def cdv_post_multipart(path: str, fields: dict, file_data: bytes | None = None, file_field: str = "import_file") -> str:
    try:
        headers = {"accept": "application/json", "Authorization": f"apikey {get_api_key()}"}
        files = {}
        if file_data is not None:
            files[file_field] = (file_field, file_data, "application/octet-stream")
        response = requests.post(_build_url(path), headers=headers, data=fields, files=files or None, timeout=120)
        response.raise_for_status()
        return response.text
    except requests.HTTPError as e:
        return json.dumps({"error": str(e), "status_code": e.response.status_code, "detail": e.response.text})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# DELETE — standard
# ---------------------------------------------------------------------------


def cdv_delete(path: str) -> str:
    try:
        response = requests.delete(_build_url(path), headers=_json_headers(), timeout=60)
        response.raise_for_status()
        return response.text if response.text else json.dumps({"result": "deleted"})
    except requests.HTTPError as e:
        return json.dumps({"error": str(e), "status_code": e.response.status_code, "detail": e.response.text})
    except Exception as e:
        return json.dumps({"error": str(e)})
