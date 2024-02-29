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