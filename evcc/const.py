EVCC_LP_MODES = [ "off", "pv", "minpv", "now" ]
EVCC_API_BATTERY_BSOC = "buffersoc"
EVCC_API_BATTERY_BSTARTSOC = "bufferstartsoc"
EVCC_API_BATTERY_DISCHARGECONTROL = "batterydischargecontrol"
EVCC_API_BATTERY_PSOC = "prioritysoc"
EVCC_API_GRID_RESPOWER = "residualpower"
EVCC_API_LOADPOINT = "loadpoint"
EVCC_API_SESSIONS = "sessions"
EVCC_API_SMART_COST_LIMIT = "smartcostlimit"
EVCC_API_STATE = "state"
EVCC_API_TARIFF = "tariff"
# TODO: while mentioned at https://docs.evcc.io/docs/reference/api/
#  the "co2" doesn't seem to always exist. Need to check 
# EVCC_API_TARIFF_TYPES = [ "grid", "feedin", "co2", "planner" ]
EVCC_API_TARIFF_TYPES = [ "grid", "feedin", "planner" ]
EVCC_API_TELEMETRY = "settings/telemetry"
EVCC_API_VEHICLE = "vehicles"
EVCC_API_LIMITSOC = "limitsoc"
EVCC_API_VEHICLE_MINSOC = "minsoc"
EVCC_API_VEHICLE_PLANSOC = "plan/soc"
