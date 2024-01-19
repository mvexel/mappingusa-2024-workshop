import bz2
import csv
import xml.etree.ElementTree as ET


def is_within_bounding_box(elem, min_lat, min_lon, max_lat, max_lon):
    elem_min_lat = float(elem.get("min_lat", 0))
    elem_min_lon = float(elem.get("min_lon", 0))
    elem_max_lat = float(elem.get("max_lat", 0))
    elem_max_lon = float(elem.get("max_lon", 0))

    return (
        min_lat <= elem_min_lat <= max_lat
        and min_lon <= elem_min_lon <= max_lon
        and min_lat <= elem_max_lat <= max_lat
        and min_lon <= elem_max_lon <= max_lon
    )


def process_bz2_xml_to_csv(bz2_xml_file, csv_file, bbox):
    min_lon, min_lat, max_lon, max_lat = bbox
    with bz2.open(bz2_xml_file, "rt") as file, open(
        csv_file, "w", newline=""
    ) as csv_out:
        csv_writer = csv.writer(csv_out)
        first_row = True
        count = 0
        progress_interval = (
            10000  # Adjust this number for more or less frequent updates
        )

        for event, elem in ET.iterparse(file, events=("start",)):
            if elem.tag == "changeset":
                count += 1
                if count % progress_interval == 0:
                    print(f"Processed {count} changesets...")

                if is_within_bounding_box(elem, min_lat, min_lon, max_lat, max_lon):
                    if first_row:
                        headers = elem.keys()
                        csv_writer.writerow(headers)
                        first_row = False
                    csv_writer.writerow([elem.get(k) for k in headers])

                # Clear the element to free up memory
                elem.clear()


if __name__ == "__main__":
    bounding_box = (
        -114.54,
        38.28,
        -109.79,
        42.38,
    )  # made this using https://boundingbox.klokantech.com/
    # bounding_box = (
    #     -180,
    #     -90,
    #     180,
    #     90,
    # )  # made this using https://boundingbox.klokantech.com/

    process_bz2_xml_to_csv("changesets-latest.osm.bz2", "output.csv", bounding_box)
