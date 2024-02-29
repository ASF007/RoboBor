import json

import aiofiles


# for getting data from our files
async def read_file(file_name: str) -> dict:
    """Reads and returns the data of the given file."""
    async with aiofiles.open(file_name, mode="r", encoding="utf8") as file:
        json_str = await file.read()
        json_data = json.loads(json_str)

        return json_data


def get_config_for(data: dict, *, key: str):
    return data.get(key, "Invalid Key")
