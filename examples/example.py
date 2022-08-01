from pyrsistent import get_in
from digisondeindices import get_indices
import datetime as dt

print(get_indices(dt.datetime(2022, 2, 20), 'MHJ45'))