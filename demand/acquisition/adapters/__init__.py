from demand.acquisition.adapters.factory import AdapterFactory
from demand.acquisition.adapters.gdelt import GDELTAdapter

AdapterFactory.register(
    "GDELT",
    GDELTAdapter,
)
