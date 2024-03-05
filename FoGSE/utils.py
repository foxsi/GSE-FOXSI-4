""" Nothing going on here, just some JSON handling. """

import json
import os

def get_system_dict(name: str, json_dict: dict):
    """
    Looks up the JSON `dict` in provided `json_dict`.

    Parameters
    ----------
    json_dict : dict
        A JSON dictionary (hopefully) containing fields with attribute `name`.

    Returns
    -------
    None or dict : The JSON field containing the `name` key, if one exists.
    """
    for element in json_dict:
        try:
            if element["name"] == name:
                return element
        except:
            continue
    return None

def get_ring_buffer_interface(json_dict):
    """
    Finds the dict called "ring_buffer_interface", no matter how nested it 
    might be in `json_dict`.

    Parameters
    ----------
    json_dict : dict
        A JSON dictionary (hopefully) containing a field "ring_buffer_interface".

    Returns
    -------
    None or dict : The JSON dict labeled "ring_buffer_interface".
    """
    try:
        return json_dict["ring_buffer_interface"]
    except KeyError:
        for key in json_dict.keys():
            try:
                if type(json_dict[key]) is dict:
                    return json_dict[key]["ring_buffer_interface"]
            except KeyError:
                continue
        return None
    
def _get_json_config():
    """ A function to access the JSON configuration file. """
    # get the JSON file with all settings
    FILE_DIR = os.path.dirname(os.path.realpath(__file__))
    json_config_file = os.path.join(FILE_DIR, "..", "foxsi4-commands", "systems.json")

    # open the JSON file and find the system's product byte size
    with open(json_config_file, "r") as json_config:
        return json.load(json_config)

def get_frame_size(system, product):
    """
    Method to retreive the "ring_frame_size_bytes" value for a given `system` 
    (e.g., cdte1, cmos1, etc.) and `product` (e.g., pc, hk, etc.).

    Parameters
    ----------
    system : `str`
        The system of interest (e.g., cdte1, cmos1, etc.).

    product : `str`
        The system's product of interest (e.g., pc, hk, etc.).

    Example
    -------
    >>> get_frame_size("cdte1", "pc")

    32780 # the number of bytes to a cdte1_pc frame in the ring buffer

    # same as running:
    # int(get_system_dict("cdte1",json_dict)["spacewire_interface"]["ring_buffer_interface"]["pc"]["ring_frame_size_bytes"], 16)
    """
    return int(get_ring_buffer_interface(get_system_dict(system,_get_json_config()))[product]["ring_frame_size_bytes"], 16)
    
def get_system_value(system, *args):
    """
    Method to retreive the "ring_frame_size_bytes" value for a given `system` 
    (e.g., cdte1, cmos1, etc.) and `product` (e.g., pc, hk, etc.).

    Parameters
    ----------
    system : `str`
        The system of interest (e.g., cdte1, cmos1, etc.).

    *args : `str`
        The system's keys to get the value needed (e.g., pc, hk, etc.).

    Example
    -------
    >>> int(get_system_value("cdte1", "spacewire_interface", "ring_buffer_interface", "pc", "ring_frame_size_bytes"), 16)

    32780 # the number of bytes to a cdte1_pc frame in the ring buffer

    # same as running:
    # `int(get_system_dict("cdte1",json_dict)["spacewire_interface"]["ring_buffer_interface"]["pc"]["ring_frame_size_bytes"], 16)`
    # or `get_frame_size("cdte1", "pc")`
    """
    sys_dict = get_system_dict(system,_get_json_config())

    # if there are no `args` then just want the system dictionary
    if len(args)==0: return sys_dict

    # now hunt down the value needed
    _output = sys_dict[args[0]]
    for a in args[1:]:
        _output = _output[a]
    return _output