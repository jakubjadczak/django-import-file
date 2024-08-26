from abc import ABC, abstractmethod
import pandas as pd
import tempfile
from openpyxl import Workbook
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
import inspect


class ColumnCheckerStrategy(ABC):
    @abstractmethod
    def check(self, columns: list, field_names: list) -> bool:
        pass


class RequiredColumnChecker(ColumnCheckerStrategy):
    def check(self, columns: list, field_names: list) -> bool:
        if all(column in field_names for column in columns):
            return columns


class ExcludeColumnChecker(ColumnCheckerStrategy):
    def check(self, exclude_columns: list, field_names: list) -> bool:
        if all(column in field_names for column in exclude_columns):
            return [col for col in field_names if col not in exclude_columns]
        

class ColumnRenameStrategy(ABC):

    @abstractmethod
    def get_verbose_name(self, model, field: str):
        pass

    @abstractmethod
    def construct_dict(self, columns: list, column_map: dict = None, model = None):
        pass


class MapColumnRename(ColumnRenameStrategy):

    def get_verbose_name(self, model, field: str):
        raise NotImplementedError("This method is not implemented in this subclass")

    def construct_dict(self, columns: list, column_map: dict = None, model = None):
        # column_map = {"mat_name": "Material Name", ...}
        column_dict = {}
        for col in columns:
            el = column_map.get(col, None)
            if el != None:
                column_dict[col] = el
            else:
                column_dict[col] = col

        return column_dict
    

class VerboseNameColumnRename(ColumnRenameStrategy):

    def get_verbose_name(self, model, field: str):
        field = model._meta.get_field(field)
        if field.verbose_name:
            return field.verbose_name
        else:
            return None
    
    def construct_dict(self, columns: list, column_map: dict = None, model = None):
        # column_map = 
        column_dict = {}
        for col in columns:
            verbose = self.get_verbose_name(model, col)
            if verbose != None:
                column_dict[col] = verbose
            else:
                column_dict[col] = col

        return column_dict
    

class FieldNameColumnRename(ColumnRenameStrategy):
    def get_verbose_name(self, model, field: str):
        raise NotImplementedError("This method is not implemented in this subclass")
    
    def construct_dict(self, columns: list, column_map: dict = None, model = None):
        # column_map = 
        column_dict = {}
        for col in columns:
            column_dict[col] = col

        return column_dict




class FileImportMixin:
    def __init__(self):
        self.column_checkers = {
            "required": RequiredColumnChecker(),
            "exclude": ExcludeColumnChecker(),
        }
        self.column_rename = {
            "map_column": MapColumnRename(),
            "verbose_name": VerboseNameColumnRename(),
            "field_name": FieldNameColumnRename()
        }
        self.calculated_fields = []
        self.column_dict = {}

    def dispatch(self, request, *args, **kwargs):
        self.field_names = [field.name for field in self.model._meta.get_fields()]
        self.required_columns = self.get_required_columns()
        self.calculated_fields = self.get_calculated_fields()
        self.column_dict = self.construct_column_dict()
        return super().dispatch(request, *args, **kwargs)
    
    
    def construct_column_dict(self):
        try:
            if self.use_verbose == True:
                return self.column_rename["field_name"].construct_dict(
                    columns=self.required_columns,
                    column_map=self.map_column,
                    model=self.model
                )
        except AttributeError:
            pass

        try:
            if self.map_column:
                return self.column_rename["field_name"].construct_dict(
                    columns=self.required_columns,
                    column_map=self.map_column
                )
        except AttributeError:
            pass

        return self.column_rename["field_name"].construct_dict(
            columns=self.required_columns
        )


    def get_required_columns(self):
        try:
            if self.required_columns:
                return self.column_checkers["required"].check(
                    self.required_columns, self.field_names
                )
        except AttributeError:
            pass

        try:
            if self.exclude_columns:
                return self.column_checkers["exclude"].check(
                    self.exclude_columns, self.field_names
                )
        except AttributeError:
            pass

        return self.field_names

    def get_calculated_fields(self):
        """
        Find all methods starting with 'calculate_' and return their corresponding field names.
        """
        methods = [
            name
            for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name.startswith("calculate_")
        ]
        return [method_name.split("calculate_")[1] for method_name in methods]

    def form_valid(self, form):
        file = form.cleaned_data["file"]
        try:
            file_path = self.get_file_path(file)
            df = self.read_file(file_path)
            result = self.import_data(df)

            if result != "Import successful with no errors.":
                return self.get_error_response(result)

            messages.success(self.request, self.messages_success)
        except Exception as e:
            messages.error(self.request, str(e))

        return redirect(self.success_url)

    def get_file_path(self, file):
        if hasattr(file, "temporary_file_path"):
            return file.temporary_file_path()
        else:
            decoded_file_content = file.read().decode(self.file_encoding)
            with tempfile.NamedTemporaryFile(
                delete=False, mode="w", encoding=self.file_encoding
            ) as temp_file:
                temp_file.write(decoded_file_content)
                return temp_file.name

    def read_file(self, file_path: str):
        if self.file_extension == "csv":
            return pd.read_csv(
                file_path, delimiter=self.delimiter, encoding=self.file_encoding
            )
        elif self.file_extension == "xlsx":
            return pd.read_excel(file_path)
        else:
            raise ValueError("Invalid file extension.")

    def import_data(self, df):
        print(self.required_columns)
        missing_columns = [
            col for col in self.required_columns if col not in df.columns
        ]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        error_report = self.process_rows(df)

        if error_report:
            return self.generate_error_report(error_report)

        return "Import successful with no errors."

    def process_rows(self, df):
        save_dict = {}
        error_report = []
        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # for col in self.required_columns:
                    #     save_dict[col] = row.get(col, None)

                    for col, col_name in self.column_dict.items():
                        save_dict[col] = row.get(col_name, None)

                    for field in self.calculated_fields:
                        calculate_method = getattr(self, f"calculate_{field}")
                        save_dict[field] = calculate_method(row)

                    self.save_row(save_dict)
                except (ValidationError, ValueError) as e:
                    error_report.append(
                        {
                            "row_index": index + 2,
                            "error": str(e),
                        }
                    )
                finally:
                    save_dict.clear()
        return error_report

    def save_row(self, data):
        row = self.model(**data)
        row.full_clean()
        row.save()

    def generate_error_report(self, error_report):
        error_report_path = "import_error_report.xlsx"
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Import Errors"
        sheet.append(["Row Index", "Error"])

        for error in error_report:
            sheet.append([error["row_index"], error["error"]])

        workbook.save(error_report_path)
        return error_report_path

    def get_error_response(self, result):
        with open(result, "rb") as f:
            response = HttpResponse(
                f.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f"attachment; filename={result}"
            return response
