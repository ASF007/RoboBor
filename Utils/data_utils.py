import aiofiles

# for getting data from our files
async def read_file(file_name: str):
    """Reads and returns the data of the given file."""
    async with aiofiles.open(file_name, "r") as file:
        data = await file.read()
        return data