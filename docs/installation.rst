Installation
============
The minimal working python version is 3.5.x


Install beem with pip:

.. code:: bash

    pip install -U hiveengine

Sometimes this does not work. Please try::

    pip3 install -U hiveengine

or::

    python -m pip install hiveengine

Manual installation
-------------------
    
You can install beem from this repository if you want the latest
but possibly non-compiling version::

    git clone https://github.com/holgern/hiveengine.git
    cd hiveengine
    python setup.py build
    
    python setup.py install --user

Run tests after install::

    pytest
