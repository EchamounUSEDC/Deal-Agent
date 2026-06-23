"""Generate small sample inputs for trying out Deal-Agent.

    python examples/make_sample_data.py

Writes an operating statement (.xlsx + .csv) and a one-parcel GeoJSON (~1 acre) into
examples/sample_data/.
"""

from __future__ import annotations

import json
import os

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "sample_data")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)

    import pandas as pd

    statement = pd.DataFrame(
        {
            "Line Item": [
                "Gross Potential Rent",
                "Vacancy & Credit Loss",
                "Effective Gross Income",
                "Property Taxes",
                "Insurance",
                "Repairs & Maintenance",
                "Management Fee",
                "Total Operating Expenses",
                "Net Operating Income",
            ],
            "Annual Amount": [
                120000,
                -6000,
                114000,
                -14000,
                -4000,
                -9000,
                -4560,
                -31560,
                82440,
            ],
        }
    )
    statement.to_excel(os.path.join(OUT, "operating_statement.xlsx"), index=False)
    statement.to_csv(os.path.join(OUT, "operating_statement.csv"), index=False)

    # A roughly 1-acre rectangular parcel in lon/lat near Reno, NV.
    parcels = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"apn": "084-123-01", "name": "Subject Parcel"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-119.80000, 39.50000],
                            [-119.79925, 39.50000],
                            [-119.79925, 39.50057],
                            [-119.80000, 39.50057],
                            [-119.80000, 39.50000],
                        ]
                    ],
                },
            }
        ],
    }
    with open(os.path.join(OUT, "parcels.geojson"), "w") as fh:
        json.dump(parcels, fh, indent=2)

    print(f"Wrote sample data to {OUT}/")


if __name__ == "__main__":
    main()
