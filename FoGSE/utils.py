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