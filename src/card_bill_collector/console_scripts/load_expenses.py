import json
import pandas as pd
import dateparser


def parse_flexible_date_pt(date_string_with_text):
    parsed_date = dateparser.parse(
        date_string_with_text,
        languages=['pt'],
        settings={'PREFER_DATES_FROM': 'current_period'}
    )
    return parsed_date


if __name__ == "__main__":
    from pathlib import Path

    all_dfs = pd.DataFrame()

    files = Path(".").glob("expenses_*")

    for expense_data in files:
        with expense_data.open() as file:
            data = json.load(file)

        dates = []
        descriptions = []
        expanses = []

        for date, desc, expense in data:
            dates.append(date)
            descriptions.append(desc)
            expanses.append(expense["amount"])

        df = pd.DataFrame(dict(
            date=dates,
            description=descriptions,
            expanse=expanses,
        ))

        all_dfs = pd.concat([all_dfs, df])

    def rule(row):
        return parse_flexible_date_pt(row["date"])

    indices_sorted = all_dfs.apply(rule, axis=1).argsort()
    all_dfs_sorted = all_dfs.iloc[indices_sorted].reset_index(drop=True)

    with open("expanses_data.csv", "w") as file:
        file.write(all_dfs_sorted.to_csv(index=False))
