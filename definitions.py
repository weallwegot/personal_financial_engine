import os
from pint import UnitRegistry

# load up the registry to be used everywhere
ureg = UnitRegistry()
# add currency as a type of unit since it is not part of the default
ureg.define('usd = [currency]')
Q_ = ureg.Quantity


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))