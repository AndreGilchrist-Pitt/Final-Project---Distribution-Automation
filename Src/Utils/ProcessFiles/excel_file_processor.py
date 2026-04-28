import importlib.util
import json
from pathlib import Path

import pandas as pd


class ExcelFileProcessor:
    """
    Helper class for reading Excel files and inspecting their sheets.

    Supports:
    - reading Excel .xlsx files with openpyxl,
    - skipping title/header-information rows,
    - choosing which Excel row should be used as the real column header,
    - skipping unknown columns,
    - requiring important columns,
    - converting sheets to dictionaries,
    - exporting sheets to JSON.
    """

    def __init__(self, file_path: str | Path):
        """
        Initialize the processor with an Excel file path.

        Args:
            file_path: Path to the Excel file.
        """
        self.file_path = Path(file_path).expanduser().resolve()

        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.file_path}")

        self._require_openpyxl()
        self._excel_file = pd.ExcelFile(self.file_path, engine="openpyxl")

    @staticmethod
    def _require_openpyxl() -> None:
        """
        Ensure openpyxl is installed before reading .xlsx files.
        """
        if importlib.util.find_spec("openpyxl") is None:
            raise ImportError(
                "Missing required dependency 'openpyxl'. "
                "This project uses pandas to read .xlsx Excel files, which requires openpyxl. "
                "Install it in your virtual environment with: python -m pip install openpyxl"
            )

    @staticmethod
    def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names by converting them to strings and trimming whitespace.

        Args:
            df: DataFrame whose columns should be normalized.

        Returns:
            DataFrame with cleaned column names.
        """
        df = df.copy()
        df.columns = df.columns.astype(str).str.strip()
        return df

    @staticmethod
    def _filter_columns(
            df: pd.DataFrame,
            columns: list[str] | None = None,
            require_columns: bool = False,
    ) -> pd.DataFrame:
        """
        Keep only known/requested columns and skip unknown columns.

        Args:
            df: DataFrame to filter.
            columns: Optional list of columns to keep.
            require_columns: If True, raise an error if any requested column is missing.

        Returns:
            Filtered DataFrame.
        """
        if columns is None:
            return df

        columns = [str(column).strip() for column in columns]

        missing_columns = [column for column in columns if column not in df.columns]

        if require_columns and missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        existing_columns = [column for column in columns if column in df.columns]
        return df[existing_columns]

    @staticmethod
    def _drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove rows where every value is empty.

        Args:
            df: DataFrame to clean.

        Returns:
            DataFrame with fully empty rows removed.
        """
        return df.dropna(how="all").reset_index(drop=True)

    @staticmethod
    def _normalize_empty_values(df: pd.DataFrame) -> pd.DataFrame:
        """
        Replace pandas NaN/NA values with empty strings.

        Args:
            df: DataFrame to clean.

        Returns:
            DataFrame with missing values replaced by empty strings.
        """
        return df.fillna("")

    @property
    def sheet_names(self) -> list[str]:
        """
        Return all sheet names in the Excel file.
        """
        return self._excel_file.sheet_names

    def read_sheet(
            self,
            sheet_name: str | int = 0,
            columns: list[str] | None = None,
            require_columns: bool = False,
            header_row: int = 0,
            drop_empty_rows: bool = True,
    ) -> pd.DataFrame:
        """
        Read a single sheet from the Excel file.

        Unknown columns are skipped when columns is provided.

        Args:
            sheet_name: Sheet name or sheet index. Defaults to first sheet.
            columns: Optional list of known columns to keep.
            require_columns: If True, raise an error when a requested column is missing.
            header_row: Zero-based row number to use as the real column header.
                        Use header_row=1 when the first Excel row is only title/header information.
            drop_empty_rows: If True, remove fully empty rows.

        Returns:
            pandas DataFrame containing the sheet data.
        """
        df = pd.read_excel(
            self.file_path,
            sheet_name=sheet_name,
            header=header_row,
            engine="openpyxl",
        )

        df = self._normalize_columns(df)

        if drop_empty_rows:
            df = self._drop_empty_rows(df)

        df = self._normalize_empty_values(df)

        return self._filter_columns(df, columns, require_columns)

    def read_all_sheets(
            self,
            columns_by_sheet: dict[str, list[str]] | None = None,
            require_columns: bool = False,
            header_row_by_sheet: dict[str, int] | None = None,
            default_header_row: int = 0,
            drop_empty_rows: bool = True,
    ) -> dict[str, pd.DataFrame]:
        """
        Read all sheets from the Excel file.

        Unknown columns are skipped for sheets listed in columns_by_sheet.

        Args:
            columns_by_sheet: Optional dictionary mapping sheet names to known columns.
            require_columns: If True, raise an error when a requested column is missing.
            header_row_by_sheet: Optional dictionary mapping sheet names to header rows.
            default_header_row: Header row used for sheets not listed in header_row_by_sheet.
            drop_empty_rows: If True, remove fully empty rows.

        Returns:
            Dictionary where keys are sheet names and values are DataFrames.
        """
        cleaned_sheets = {}

        for sheet_name in self.sheet_names:
            header_row = default_header_row

            if header_row_by_sheet is not None:
                header_row = header_row_by_sheet.get(sheet_name, default_header_row)

            columns = None
            if columns_by_sheet is not None:
                columns = columns_by_sheet.get(sheet_name)

            cleaned_sheets[sheet_name] = self.read_sheet(
                sheet_name=sheet_name,
                columns=columns,
                require_columns=require_columns,
                header_row=header_row,
                drop_empty_rows=drop_empty_rows,
            )

        return cleaned_sheets

    def preview_sheet(
            self,
            sheet_name: str | int = 0,
            rows: int = 5,
            columns: list[str] | None = None,
            require_columns: bool = False,
            header_row: int = 0,
            drop_empty_rows: bool = True,
    ) -> pd.DataFrame:
        """
        Return the first few rows of a sheet.

        Unknown columns are skipped when columns is provided.

        Args:
            sheet_name: Sheet name or sheet index. Defaults to first sheet.
            rows: Number of rows to preview.
            columns: Optional list of known columns to keep.
            require_columns: If True, raise an error when a requested column is missing.
            header_row: Zero-based row number to use as the real column header.
            drop_empty_rows: If True, remove fully empty rows.

        Returns:
            pandas DataFrame preview.
        """
        df = self.read_sheet(
            sheet_name=sheet_name,
            columns=columns,
            require_columns=require_columns,
            header_row=header_row,
            drop_empty_rows=drop_empty_rows,
        )
        return df.head(rows)

    def print_summary(
            self,
            header_row_by_sheet: dict[str, int] | None = None,
            default_header_row: int = 0,
    ) -> None:
        """
        Print a summary of all sheets, including row count and column names.

        Args:
            header_row_by_sheet: Optional dictionary mapping sheet names to header rows.
            default_header_row: Header row used for sheets not listed in header_row_by_sheet.
        """
        sheets = self.read_all_sheets(
            header_row_by_sheet=header_row_by_sheet,
            default_header_row=default_header_row,
        )

        print(f"Excel file: {self.file_path}")
        print(f"Number of sheets: {len(sheets)}")
        print("-" * 50)

        for sheet_name, df in sheets.items():
            print(f"Sheet: {sheet_name}")
            print(f"Rows: {len(df)}")
            print(f"Columns: {list(df.columns)}")
            print("-" * 50)

    def sheet_to_dicts(
            self,
            sheet_name: str | int = 0,
            columns: list[str] | None = None,
            require_columns: bool = False,
            header_row: int = 0,
            drop_empty_rows: bool = True,
    ) -> list[dict]:
        """
        Convert a sheet to a list of dictionaries.

        Unknown columns are skipped when columns is provided.

        Args:
            sheet_name: Sheet name or sheet index. Defaults to first sheet.
            columns: Optional list of known columns to keep.
            require_columns: If True, raise an error when a requested column is missing.
            header_row: Zero-based row number to use as the real column header.
            drop_empty_rows: If True, remove fully empty rows.

        Returns:
            List of dictionaries, one dictionary per row.
        """
        df = self.read_sheet(
            sheet_name=sheet_name,
            columns=columns,
            require_columns=require_columns,
            header_row=header_row,
            drop_empty_rows=drop_empty_rows,
        )
        return df.to_dict(orient="records")

    def export_sheet_to_json(
            self,
            sheet_name: str | int,
            output_path: str | Path,
            columns: list[str] | None = None,
            require_columns: bool = False,
            header_row: int = 0,
            drop_empty_rows: bool = True,
    ) -> None:
        """
        Export a sheet to a JSON file.

        Unknown columns are skipped when columns is provided.

        Args:
            sheet_name: Sheet name or sheet index.
            output_path: Destination JSON file path.
            columns: Optional list of known columns to keep.
            require_columns: If True, raise an error when a requested column is missing.
            header_row: Zero-based row number to use as the real column header.
            drop_empty_rows: If True, remove fully empty rows.
        """
        output_path = Path(output_path).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = self.sheet_to_dicts(
            sheet_name=sheet_name,
            columns=columns,
            require_columns=require_columns,
            header_row=header_row,
            drop_empty_rows=drop_empty_rows,
        )

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, default=str)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]
    excel_path = project_root / "Data" / "PowerWorld" / "Figure14_22_Baseline.xlsx"

    processor = ExcelFileProcessor(excel_path)

    print("Detected sheet names:")
    print(processor.sheet_names)

    header_rows = {
        "YBus": 1,
    }

    print("\nFile summary:")
    #processor.print_summary(header_row_by_sheet=header_rows)
    processor.print_summary(default_header_row=1)
    first_sheet = processor.sheet_names[0]
    first_sheet_header_row = header_rows.get(first_sheet, 1)

    print(f"\nPreview of first sheet with corrected header row: {first_sheet}")
    print(
        processor.preview_sheet(
            first_sheet,
            header_row=first_sheet_header_row,
        )
    )
    output_path = project_root / "Data" / "PowerWorld" / "YBus.json"

    processor.export_sheet_to_json(
        sheet_name="YBus",
        output_path=output_path,
        header_row=1,
    )

    print(f"Exported JSON to: {output_path}")