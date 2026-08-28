"""Temporary feature visibility switches for the operations console."""

# These modules are intentionally unavailable in the current product scope.
# Keep the historical records in PostgreSQL so they can be restored later,
# but exclude them from menus and API registration.
HIDDEN_MENU_CODES = frozenset({"vehicle", "dispatch"})
