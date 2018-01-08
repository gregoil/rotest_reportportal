"""Setup file for handling packaging and distribution."""
from setuptools import setup, find_packages


setup(
    name='rotest_reportportal',
    version="1.0.0",
    description="Rotest result handler to send data to a ReportPortal system",
    long_description=open("README.rst").read(),
    license="MIT",
    author="gregoil",
    author_email="gregoil@walla.co.il",
    url="https://github.com/gregoil/rotest-reportportal",
    keywords="testing system reportportal unittest",
    install_requires=['rotest',
                      'attrdict',
                      'pyyaml',
                      'reportportal_client'],
    packages=find_packages("."),
    package_dir={"": "."},
    entry_points={
        "rotest.result_handlers":
            ["reportportal = "
             "rotest_reportportal.result_handler:ReportPortalHandler"]
    },
    zip_safe=False
)
