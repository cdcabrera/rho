######################
Contributing to rho
######################

Bug reports and code and documentation patches are welcome. You can
help this project also by using the development version of rho
and by reporting any bugs you might encounter.

1. Reporting bugs
=================

It's important that you provide the full command argument list
as well as the output of the failing command.

.. code-block:: bash

    $ rho [COMPLETE ARGUMENT LIST THAT TRIGGERS THE ERROR]
    [COMPLETE OUTPUT]

Additionally, attach any relevant input files after scrubbing any private
information.


2. Contributing Code and Docs
=============================

Before working on a new feature or a bug, please browse `existing issues`_
to see whether it has been previously discussed. If the change in question
is a bigger one, it's always good to discuss before you starting working on
it.


Creating Development Environment
--------------------------------

Go to https://github.com/quipucords/rho and fork the project repository. Each
branch should correspond to an associated issue opened on the main repository
(e.g. ``issues/5`` --> https://github.com/quipucords/rho/issues/5).


.. code-block:: bash

    git clone https://github.com/<YOU>/rho

    cd rho

    git checkout -b issues/my_issue_#

    pip install -r requirements.txt

    make all


Making Changes
--------------

Please make sure your changes conform to `Style Guide for Python Code`_ (PEP8).
You can run the lint command on your branch to check compliance.

.. code-block:: bash

    make lint

Testing
-------

Before opening a pull requests, please make sure the `tests`_ pass
in all of the supported Python environments (2.7, 3.5, 3.6).
You should also add tests for any new features and bug fixes.

rho uses `pytest`_ for testing.

Adding Facts
------------

Adding facts requires changes in three places.

1. First, add information about your fact by calling `new_fact` in
   `rho/facts.py`.
2. Then, add an Ansible role to collect data for your fact. Be sure to
   use a `where` clause so the collection only runs when the fact is
   wanted.
3. Finally, update `library/spit_results.py` for any postprocessing
   that your fact needs. You may not need to do any postprocessing, if
   you just want the remote shell output reported as the fact value.

Running all tests:
******************

.. code-block:: bash

    # Run all tests on the current Python interpreter
    make tests

    # Run all tests on the current Python with coverage
    make tests-coverage


-----

See `Makefile`_ for additional development utilities.

.. _existing issues: https://github.com/quipucords/rho/issues?state=open
.. _AUTHORS: https://github.com/quipucords/rho/blob/master/AUTHORS.rst
.. _Makefile: https://github.com/quipucords/rho/blob/master/Makefile
.. _pytest: http://pytest.org/
.. _Style Guide for Python Code: http://python.org/dev/peps/pep-0008/
.. _tests: https://github.com/quipucords/rho/tree/master/tests
