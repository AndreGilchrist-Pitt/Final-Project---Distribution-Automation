from pathlib import Path

from Src.Paths.paths import POWERWORLD_BASELINE_EXCEL_FILE
from Src.Utils.ProcessFiles.excel_file_processor import ExcelFileProcessor


def make_safe_json_file_name(sheet_name: str) -> str:
    """
    Convert an Excel sheet name into a safe JSON file name.

    Args:
        sheet_name: Excel sheet name.

    Returns:
        Safe JSON file name.
    """
    unsafe_characters = {
        "/": "_",
        "\\": "_",
        ":": "_",
        "*": "_",
        "?": "_",
        '"': "_",
        "<": "_",
        ">": "_",
        "|": "_",
        " ": "_",
    }

    safe_name = sheet_name.strip()

    for old, new in unsafe_characters.items():
        safe_name = safe_name.replace(old, new)

    return f"{safe_name}.json"


def export_all_sheets_to_source_directory(
        excel_file_path: str | Path,
        default_header_row: int = 1,
) -> None:
    """
    Export every sheet in an Excel file to individual JSON files.

    The JSON files are written to the same directory as the Excel file.

    Args:
        excel_file_path: Path to the source Excel file.
        default_header_row: Zero-based row index to use as the real column header.
                            Use 1 when the first Excel row is report/title information.
    """
    processor = ExcelFileProcessor(excel_file_path)
    output_directory = processor.file_path.parent

    print(f"Source Excel file: {processor.file_path}")
    print(f"Export directory: {output_directory}")
    print(f"Detected {len(processor.sheet_names)} sheets.")
    print("-" * 80)

    for sheet_name in processor.sheet_names:
        output_file_name = make_safe_json_file_name(sheet_name)
        output_path = output_directory / output_file_name

        processor.export_sheet_to_json(
            sheet_name=sheet_name,
            output_path=output_path,
            header_row=default_header_row,
            drop_empty_rows=True,
        )

        print(f"Exported sheet '{sheet_name}' -> {output_path}")

    print("-" * 80)
    print("Finished exporting all sheets.")


if __name__ == "__main__":
    export_all_sheets_to_source_directory(
        excel_file_path=POWERWORLD_BASELINE_EXCEL_FILE,
        default_header_row=1,
    )