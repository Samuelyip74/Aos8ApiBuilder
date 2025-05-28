
import re

def parse_output_json(output: str):
    lines = output.strip().splitlines()
    
    # Find the header line
    header_line = lines[0]
    headers = re.split(r"\s{2,}", header_line.strip())  # split on 2+ spaces

    # Parse each data line
    vlan_list = []
    for line in lines[2:]:  # skip header + separator line
        if not line.strip():
            continue
        parts = re.split(r"\s{2,}", line.strip())
        entry = dict(zip(headers, parts))
        vlan_list.append(entry)

    return vlan_list