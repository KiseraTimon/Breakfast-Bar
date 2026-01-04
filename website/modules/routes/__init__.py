"""Developer Remarks
---
1. Imports
Observe that all flask imports have been made in this __init__ file
This creates implicit dependency declarations; meaning a hidden dependency chain exists in the route Files
I intentionally designed the system this way as to lighten my workload when importing dependencies

---
2. The god module
Due to issue no.1 this __init__ file is a god module, meaning all other route files depend on this module
As a result, code may break if their is refactoring or rearrangement of the files in this package

"""


from flask import Blueprint, render_template

# Blueprint Object
routes = Blueprint("routes", __name__)

# Route Files
from . import views, portal, auth

__all__ = ["routes"]
