
import re
import json
from typing import List, Dict

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


def parse_ip_interface_output(cli_output: str) -> List[Dict[str, str]]:
    """
    Parses the 'show ip interface' CLI output into a list of dictionaries.

    :param cli_output: Raw CLI output as a string
    :return: List of dictionaries with parsed interface data
    """
    lines = cli_output.strip().splitlines()
    data_lines = []
    start_parsing = False

    for line in lines:
        # Look for the line of dashes that separates the header from the data
        if re.match(r'-{10,}', line):
            start_parsing = True
            continue
        if start_parsing and line.strip():
            data_lines.append(line)

    interfaces = []
    for line in data_lines:
        # Split by 2+ spaces to get columns
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) >= 5:
            interface = {
                "name": parts[0],
                "ip_address": parts[1],
                "subnet_mask": parts[2],
                "status": parts[3],
                "forward": parts[4],
                "device": parts[5] if len(parts) > 5 else None
            }
            interfaces.append(interface)

    return interfaces


