
import re
import json
from typing import List, Dict, Union

def parse_system_output_json(cli_output: str) -> Dict[str, Union[str, dict]]:
    data = {}
    current_section = None
    section_indent = None

    lines = cli_output.strip().splitlines()
    
    for line in lines:
        # Normalize indentation
        indent_match = re.match(r'^(\s+)', line)
        indent = len(indent_match.group(1)) if indent_match else 0
        line = line.strip().rstrip(',')

        # Section header (e.g. "Flash Space:")
        if line.endswith(':') and not ':' in line[:-1]:
            section_name = line[:-1].strip()
            data[section_name] = {}
            current_section = data[section_name]
            section_indent = indent
            continue

        # Key-value pair
        if ':' in line:
            key, value = map(str.strip, line.split(':', 1))
            # If we're in a section, add to it
            if current_section is not None and indent > section_indent:
                current_section[key] = value
            else:
                # Top-level field
                data[key] = value
                current_section = None
                section_indent = None

    return data

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

def parse_interface_status(cli_output: str) -> List[Dict[str, str]]:
    lines = cli_output.strip().splitlines()

    # Skip header lines
    data_lines = []
    in_data = False
    for line in lines:
        if re.match(r"^\s*\d+/\d+/\d+", line):  # Data starts with a port format like 1/1/1
            in_data = True
        if in_data:
            data_lines.append(line.strip())

    parsed = []
    for line in data_lines:
        # The fields are space-separated but the speed values can be variable, so we use fixed-width slicing
        # Based on observed pattern, tweak if needed
        parts = re.split(r'\s{2,}', line)
        if len(parts) < 13:
            continue

        parsed.append({
            "port": parts[0],
            "admin_status": parts[1],
            "auto_nego": parts[2],
            "det_speed": parts[3],
            "det_duplex": parts[4],
            "det_pause": parts[5],
            "det_fec": parts[6],
            "cfg_speed": parts[7],
            "cfg_duplex": parts[8],
            "cfg_pause": parts[9],
            "cfg_fec": parts[10],
            "link_trap": parts[11],
            "eee": parts[12],
        })

    return parsed

def parse_interface_detail(cli_output: str) -> Dict[str, str]:
    data = {}
    rx_section = {}
    tx_section = {}

    lines = cli_output.strip().splitlines()
    current_section = "general"

    for line in lines:
        line = line.strip()

        # Skip prompt
        if line.startswith("ACSW"):
            continue

        # Detect section change
        if line.startswith("Rx"):
            current_section = "rx"
            continue
        elif line.startswith("Tx"):
            current_section = "tx"
            continue

        # Key-value parsing
        if ":" in line:
            parts = line.split(":")
            key = parts[0].strip()
            value = ":".join(parts[1:]).strip()

            # Handle comma-separated continuation values
            value = value.rstrip(",")

            # Merge multi-field lines (e.g., BandWidth + Duplex)
            if "," in value:
                sub_parts = [v.strip() for v in value.split(",")]
                for sub_part in sub_parts:
                    if ":" in sub_part:
                        sub_key, sub_val = [x.strip() for x in sub_part.split(":", 1)]
                        key = key + " / " + sub_key
                        value = sub_val

            # Assign based on section
            if current_section == "rx":
                rx_section[key] = value
            elif current_section == "tx":
                tx_section[key] = value
            else:
                data[key] = value

    # Merge sections
    if rx_section:
        data["Rx"] = rx_section
    if tx_section:
        data["Tx"] = tx_section

    return data

def parse_vlan_output_json(output: str):
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


