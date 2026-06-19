import papermill as pm
from pathlib import Path

Path("executed").mkdir(exist_ok=True)
Path("outputs").mkdir(exist_ok=True)

pm.execute_notebook(
    "01_loads.ipynb",
    "executed/01_loads_executed.ipynb"
)

pm.execute_notebook(
    "02_member_check.ipynb",
    "executed/02_member_check_executed.ipynb"
)