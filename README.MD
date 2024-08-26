# django-import-file

Not ready for use yet!

Developed by Jakub Jadczak, 2024

## Examples of How To Use with Django Class Based View

Simple Usage

Read csv

```python

from django_import_file import FileImportMixin

class ImportFile(FileImportMixin, FormView):
    model = RowsData
    form_class = ImportFileForm
    template_name = "main/home.html"
    file_extension = "csv"
    file_encoding = "utf-8"
    delimiter = ";"
    required_columns = ["name", "age", "email", "phone", "address"]
    messages_success = "Import successful with no errors."
    success_url = reverse_lazy("main:home")
```

Read xlsx

```python
class ImportFile(FileImportMixin, FormView):
    model = RowsData
    template_name = "main/home.html"
    file_extension = "xlsx"
    required_columns = ["name", "age", "email", "phone", "address"]
    sheet_name = "Sheet1"
    messages_success = "Import successful with no errors."
    form_class = ImportFileForm
    success_url = reverse_lazy("main:home")
```

With additional calculation method

```python
class ImportFile(FileImportMixin, FormView):
    model = RowsData
    form_class = ImportFileForm
    template_name = "main/home.html"
    file_extension = "csv"
    file_encoding = "utf-8"
    delimiter = ";"
    required_columns = ["name", "age", "email", "phone", "address"]
    messages_success = "Import successful with no errors."
    success_url = reverse_lazy("main:home")

    def calculate_district(self, row):
        # name after _ must be equal to field in model, you want to calculate
        if ...:
            return "..."
        else:
            return "..."

    def get_file_content(self, file_path: str):
        df =  super().get_file_content(file_path)
        df["age"] = df["age"] + 10
        return df
```

Options:

```python
#import
from django_import_file import FileImportMixin

#Declarations, examples
file_extension = "csv"
use_verbose = True # map column using verbose_name (columns name in the file must be equal to verbose_names)
map_column = {"name": "Full Name"} # map your own columns name, {model_name: file_name}
sheet_name = "Sheet1" # used in xlsx
required_columns = ["age", "name"] 
exclude_columns = ["address"]
delimiter = ";"
file_encoding = "utf-16-le"

```