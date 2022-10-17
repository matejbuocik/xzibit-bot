import csv
from typing import Iterator
import aiofiles


TRANSLATION_TABLE = "".maketrans("áäčďéíĺľňóôŕšťúýž", "aacdeillnoorstuyz")


async def get_csv(file_name: str) -> Iterator:
    async with aiofiles.open(file_name, "r", encoding="utf-8") as file:
        lines = await file.readlines()
        return csv.reader(lines, delimiter=",")


async def nameday_from_date(file_name: str, day: int, month: int) -> str:
    csv_file = await get_csv(file_name)
    for row in csv_file:
        if (day, month) == (int(row[0]), int(row[1])):
            if len(row) == 2:
                return f"{day}.{month} nemá meniny nikto :("
            elif len(row) == 3:
                return f"{day}.{month} má meniny {row[2]}"
            else:
                names = ", ".join(row[2:])
                return f"{day}.{month} majú meniny {names}"

    return f"Error - invalid date: {day}.{month}."


async def nameday_from_name(file_name: str, name: str) -> str:
    csv_file = await get_csv(file_name)
    name = name.lower().translate(TRANSLATION_TABLE)

    for row in csv_file:
        for i in range(2, len(row)):
            if row[i].lower().translate(TRANSLATION_TABLE) == name:
                return f"{row[i]} má meniny {row[0]}.{row[1]}"

    return f"Error - could not find '{name}'"
