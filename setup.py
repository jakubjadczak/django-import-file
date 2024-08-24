from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


VERSION = "0.0.5"
DESCRIPTION = "Django Mixin allows easy import of files into Django models."
LONG_DESCRIPTION = (
    """Django Mixin allows easy import of files into Django models.
    Allows you to import files in the following formats: .csv, .xlsx.
    With error messages"""
)

# Setting up
setup(
    name="django_import_file",
    version=VERSION,
    author="Jakub Jadczak",
    author_email="<jakubjadczak02@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["pandas", "openpyxl"],
    keywords=["python", "django", "import", "file", "import file", "import excel"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
