# django-import-file

Not ready for use yet!

Developed by Jakub Jadczak, 2024

## Examples of How To Use with Django Class Based View

Simple Usage

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
```
