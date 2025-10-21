import json
def export_motion_to_web_json(motion_seq, out_path: str):
    """
    Convert internal motion sequence to a simple web-consumable JSON format.
    """
    payload = {"version":"1.0","frames":motion_seq}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return out_path
