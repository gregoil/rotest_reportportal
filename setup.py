"""Setup file for handling packaging and distribution."""
from setuptools import setup


setup(
    name='rotest_reportportal',
    version="2.0.1",
    description="Rotest result handler to send data to a ReportPortal system",
    long_description=open("README.rst").read(),
    license="MIT",
    author="gregoil",
    author_email="gregoil@walla.co.il",
    url="https://github.com/gregoil/rotest_reportportal",
    keywords="testing system reportportal unittest",
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,<3.8.0",
    install_requires=['rotest',
                      'attrdict',
                      'pyyaml',
                      'reportportal_client'],
    extras_require={
        "dev": ["flake8", "pylint",
                "pytest", "pytest-cov",
                "mock"]
    },
    packages=["rotest_reportportal"],
    entry_points={
        "rotest.result_handlers":
            ["reportportal = "
             "rotest_reportportal:ReportPortalHandler"]
    },
    zip_safe=False
)
