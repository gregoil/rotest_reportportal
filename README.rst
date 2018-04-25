===================
rotest_reportportal
===================

.. image:: https://img.shields.io/pypi/v/rotest-reportportal.svg
    :alt: PyPI
    :target: https://pypi.python.org/pypi/rotest-reportportal/

.. image:: https://travis-ci.org/gregoil/rotest-reportportal.svg?branch=master
    :target: https://travis-ci.org/gregoil/rotest-reportportal

.. image:: https://img.shields.io/appveyor/ci/gregoil/rotest_reportportal.svg?branch=master
    :alt: AppVeyor
    :target: https://ci.appveyor.com/project/gregoil/rotest_reportportal

.. image:: https://coveralls.io/repos/github/gregoil/rotest_reportportal/badge.svg?branch=master
    :target: https://coveralls.io/github/gregoil/rotest_reportportal

What is it?
===========

A plugin to the `Rotest <https://github.com/gregoil/rotest>`_ testing
framework, that enables reporting the test results to the amazing
`Report Portal <http://reportportal.io/>`_ system.

Installation
============

Install it using ``pip``:

.. code-block:: console

    $ pip install rotest_reportportal

Configuration
=============

In the ``rotest.yml`` configuration file (or any of the available configuration
formats, like ``.rotest.yaml``) add the following entry:

.. code-block:: yaml

    rotest:
        <rotest configuration>

    reportportal:
        endpoint: http://<reportportal_host>:<port>
        project: <project name>

For example:

.. code-block:: yaml

    rotest:
        ...

    reportportal:
        endpoint: http://reportal:8080/
        project: SUPERADMIN_PERSONAL

In addition to that, you need to define the ``ROTEST_REPORTPORTAL_TOKEN``
environment variable a user's UUID. For example:

.. code-block:: yaml

    $ export ROTEST_REPORTPORTAL_TOKEN="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    $ # or, on Windows:
    $ set ROTEST_REPORTPORTAL_TOKEN="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

A couple of things about the UUID:

* You can obtain it from your user profile:
  ``http://{report_portal}:{port}/ui/#user-profile``

* Tests published with this UUID will identify the user that ran those tests.

* Unless you want everyone to be able to publish results for you, keep this
  UUID a secret (no mentioning in the repository's code or any public space).

Usage
=====

You can run tests and activate the result handler, in the following way:

.. code-block:: console

    $ python <some_test_file> -o reportportal
