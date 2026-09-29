"""Merchant houses, workshops and their branch networks.

Editable at runtime via the MCP server's business tools; rows are persisted
to faerun/data/store/businesses.json rather than defined here.
"""

from ..data_store import load_businesses

BUSINESSES = load_businesses()
