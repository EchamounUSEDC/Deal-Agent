"""Geospatial tools: interpret parcel/land geometry and read map images/PDFs."""

from __future__ import annotations

import json
import math
import os

from anthropic import beta_tool

from ..client import get_client
from ..config import settings
from ..util import file_to_content_block, message_text

SQ_M_PER_ACRE = 4046.8564224


def _geodesic_area_m2(geom) -> float:
    """Approximate planar area (m²) for a lon/lat geometry via a latitude-corrected
    equirectangular projection about the centroid. Good to a few % for parcel-sized
    polygons; for survey-grade output supply already-projected coordinates."""
    from shapely.ops import transform

    lat0 = geom.centroid.y
    m_per_deg_lon = 111_320.0 * math.cos(math.radians(lat0))
    m_per_deg_lat = 110_540.0

    def _project(x, y, z=None):  # noqa: ARG001
        return (x * m_per_deg_lon, y * m_per_deg_lat)

    return abs(transform(_project, geom).area)


def _load_geometries(path: str) -> list:
    """Return a list of shapely geometries from GeoJSON or (optionally) a shapefile."""
    from shapely.geometry import shape

    ext = os.path.splitext(path)[1].lower()
    if ext in (".geojson", ".json"):
        with open(path) as fh:
            data = json.load(fh)
        if isinstance(data, dict) and data.get("type") == "FeatureCollection":
            features = data.get("features", [])
        elif isinstance(data, dict) and data.get("type") == "Feature":
            features = [data]
        elif isinstance(data, list):
            features = data
        else:  # a bare geometry
            features = [{"geometry": data}]
        geoms = []
        for feat in features:
            geom = feat.get("geometry", feat) if isinstance(feat, dict) else feat
            if geom:
                geoms.append(shape(geom))
        return geoms
    if ext == ".shp":
        try:
            import geopandas as gpd
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Reading shapefiles requires geopandas (`pip install geopandas`). "
                "Alternatively convert the layer to GeoJSON."
            ) from exc
        return list(gpd.read_file(path).geometry)
    raise ValueError(f"Unsupported geometry file {ext!r}. Use .geojson, .json, or .shp.")


@beta_tool
def read_parcel_data(path: str) -> str:
    """Interpret parcel/land geometry and report total area, bounds, and centroid.

    Accepts GeoJSON (.geojson/.json) or a shapefile (.shp, if geopandas is installed).
    Returns parcel count, total area in acres and square meters, the bounding box,
    and the centroid. Lon/lat coordinates are detected and converted to meters
    automatically (approximate).

    Args:
        path: Path to a .geojson, .json, or .shp file describing one or more parcels.
    """
    try:
        geoms = _load_geometries(path)
    except FileNotFoundError:
        return f"Error: file not found at {path!r}."
    except Exception as exc:  # noqa: BLE001
        return f"Error reading {path!r}: {exc}"

    geoms = [g for g in geoms if g is not None and not g.is_empty]
    if not geoms:
        return f"Error: no usable geometry found in {path!r}."

    from shapely.ops import unary_union

    merged = unary_union(geoms)
    minx, miny, maxx, maxy = merged.bounds
    centroid = merged.centroid

    looks_lonlat = abs(minx) <= 180 and abs(maxx) <= 180 and abs(miny) <= 90 and abs(maxy) <= 90
    if looks_lonlat:
        area_m2 = _geodesic_area_m2(merged)
        crs_note = "coordinates look like lon/lat (EPSG:4326); area approximated in meters"
    else:
        area_m2 = abs(merged.area)
        crs_note = "coordinates assumed to be in a projected CRS measured in meters"

    result = {
        "file": path,
        "parcel_count": len(geoms),
        "total_area_acres": round(area_m2 / SQ_M_PER_ACRE, 4),
        "total_area_sq_meters": round(area_m2, 2),
        "total_area_sq_feet": round(area_m2 * 10.7639104, 2),
        "bounding_box": {"min_x": minx, "min_y": miny, "max_x": maxx, "max_y": maxy},
        "centroid": {"x": centroid.x, "y": centroid.y},
        "crs_note": crs_note,
    }
    return json.dumps(result, indent=2, default=str)


@beta_tool
def analyze_map(path: str, question: str) -> str:
    """Study a map image or PDF (plat, parcel map, survey, zoning or site plan) and
    answer a question about it using vision.

    Use this to read labels, lot lines, dimensions, zoning designations, easements,
    road frontage, and other features that only appear on the map itself.

    Args:
        path: Path to a map image (PNG/JPG/GIF/WebP) or a PDF.
        question: What to determine from the map, e.g. "What is the zoning and the
            road frontage in feet for the highlighted parcel?"
    """
    try:
        visual = file_to_content_block(path)
    except FileNotFoundError:
        return f"Error: file not found at {path!r}."
    except ValueError as exc:
        return f"Error: {exc}"

    client = get_client()
    resp = client.messages.create(
        model=settings.vision_model,
        max_tokens=2048,
        system=(
            "You are a land surveyor and cartographer. Read the supplied map or plat "
            "carefully and answer precisely. Quote any labels, dimensions, scale bars, "
            "and zoning codes you can see. If something is illegible or not shown, say so "
            "explicitly rather than guessing."
        ),
        messages=[{"role": "user", "content": [visual, {"type": "text", "text": question}]}],
    )
    return message_text(resp) or "No readable answer was produced from the map."
