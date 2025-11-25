"""
read_excel_print.py

Reads an Excel file provided by path and prints its data to the console.

Usage:
    python read_excel_print.py --file "path/to/file.xlsx" [--sheet SHEET_NAME] [--max-rows N]

Notes:
- This script uses pandas to read Excel files. For .xlsx files install `openpyxl`.
- Keep the script simple: it prints the DataFrame to stdout.

"""


import argparse
import sys
from typing import Optional
import ai_for_data_fill
from excel_writer import ExcelWriter

import pandas as pd
from openpyxl import load_workbook


def parse_args() -> argparse.Namespace:
    default_file = "./data.xlsx"
    default_sheet = 'sheet'
    default_row=2
    parser = argparse.ArgumentParser(description="Read an Excel file and print its contents to the console.")
    parser.add_argument("--file", "-f",  default=default_file ,help="Path to the Excel file (.xlsx, .xls)")
    parser.add_argument("--sheet", "-s", default=None, help="Sheet name or index to read (default: first sheet)")
    parser.add_argument("--max-rows", "-m", type=int, default=default_row, help="If set, only print up to this many rows")
    parser.add_argument("--no-index", dest="show_index",action="store_false", help="Hide DataFrame index when printing")
    parser.set_defaults(show_index=True)
    return parser.parse_args()


def read_excel(path: str, sheet: Optional[str] = None) -> pd.DataFrame:
    """Read an Excel file and return a DataFrame.
    """
    try:
        df = pd.read_excel(path, sheet_name=sheet)
        if isinstance(df, dict):
            first_key = next(iter(df))
            df = df[first_key]
        return df
    except FileNotFoundError:
        print("file not found")
    except Exception:
        print("somthing went wrong")


def exclude_irrelevent_data(data,exclude_columns_ai_request):
    for s in exclude_columns_ai_request:
        if s in data:
            del data[s]
    return data



def find_only_empty_and_fill(file, start_row, end_row, exclude_columns_ai_request, include_column_ai_response):
    file_path, sheet_name = file
    df = read_excel(file_path, sheet_name)

    helperAi = ai_for_data_fill.AIForDataFill(include_column_ai_response=include_column_ai_response)

    # Convert Excel row numbers to 0-based index for pandas
    start_idx = start_row - 2
    end_idx = end_row - 2

    # Use ExcelWriter context manager to keep file open during loop
    with ExcelWriter(file_path, sheet_name) as writer:
        for i in range(start_idx, end_idx + 1):
            row = df.iloc[i]

            # Skip if row has no empty cells
            if not row.isnull().any():
                print(f"Excel Row {i+2}: skipped (no empty cells).")
                continue

            # Check if any of the target columns are empty
            if row[include_column_ai_response].isnull().any():
                row_json = exclude_irrelevent_data(row.to_dict(), exclude_columns_ai_request)
                print(f"Excel Row {i+2}: processing...")

                ai_response = helperAi.get_response(row_json)

                if len(ai_response) > 0:
                    writer.write_row(df=df, row=i+2, data=ai_response, columns=include_column_ai_response)
                else:
                    print("Empty data response from AI:", ai_response)
                    sys.exit(1)  # Exit for saving AI call

                print(f"Excel Row {i+2}: processed.")
            else:
                print(f"Excel Row {i+2}: skipped (target columns filled).")



def main() -> int:
    args = parse_args()
    # Dont do Spelling mistake
    exclude_columns_ai_request = [
    "Sale Price",
    "Quantity",
    "Weight",
    "Pkg WT %",
    "MRP %",
    "Multiplier",
    "Ship Mult",
    "Discount %",
    "Tag",
    "attribute_name",
    "attribute_value",
    "gallery",
    "thumbnail",
    "meta_image"
]
    include_column_ai_response = ["Short Description","Description","Tag"]

    find_only_empty_and_fill(["C:\\Users\\AVERMA41\\Downloads\\data.xlsx","Sheet1"]
                              ,80                  #start row
                              ,83                  #end row
                             ,exclude_columns_ai_request
                             ,include_column_ai_response
                             )

    return 0



if __name__ == "__main__":
    raise SystemExit(main())
