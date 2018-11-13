from .onegdata import create_data_for_db as compute_onegrams

from .ngdata import (
    create_data_for_db as compute_bigrams,
    prepare_concl
)

from textproc import *