import setuptools
import io

long_description = io.open("README.md", encoding="utf-8") .read()

setuptools.setup(
    name="hsp_cf",
    version="1.0.0.dev35",
    author="Author",
    author_email="DL_HSP_Braniacs_Team@philips.com",
    pip="cf scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://tfsapac04.ta.philips.com/tfs/DHPCollection/DHP/_git/DevOpsLib",
    include_package_data=True,
    classifiers=[
        "Programming Language Support:: Python :: 2 and 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=['tests']),
    python_requires='>=2.7',
)