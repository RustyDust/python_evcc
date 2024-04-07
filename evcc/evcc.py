from datetime import datetime, timezone
import logging
import traceback
import requests

from .const import *

LOGGER = logging.getLogger(__package__)

class evcc:
  def __init__(self, url) -> None:
    self.evcc_url = url
    self.evcc_api = url + "/api/"
    self.evcc_state = {}
    self.evcc_sessions = {}
    self.evcc_tarrifs = {}
    pass
  
  def _get(self, what, isretry=False):
    url = self.evcc_api + what
    response = requests.get(url=url, timeout=10)
    if not isretry and response.status_code == 401:
      return self._get(what, True)
    if response.status_code != 200:
      response.raise_for_status()

    return response.json()

  def _get_raw(self, what, isretry=False):
    url = self.evcc_api + what
    response = requests.get(url=url, timeout=10)
    if not isretry and response.status_code == 401:
      return self._get(what, True)
    return response
  
  def _post(self, what, isretry=False):
    url = self.evcc_api + what
    response = requests.post(url, timeout=10)

    if not isretry and response.status_code == 401:
      return self._post(what, True)
    if response.status_code != 200:
      response.raise_for_status()
    return response
  
  def _delete(self, what, isretry=False):
    url = self.evcc_api + what
    response = requests.delete(url, timeout=10)

    if not isretry and response.status_code == 401:
      return self._delete(what, True)
    if response.status_code != 200:
      response.raise_for_status()
    return response

  def _patch(self, what, isretry=False):
    url = self.evcc_api + what
    response = requests.patch(url, timeout=10)

    if not isretry and response.status_code == 401:
      return self.patch(what, True)
    if response.status_code != 200:
      response.raise_for_status()
    return response

  def get_last_session(self):
    return self.get_sessions()[0]

  def get_loadpoint_plan(self, lpid=0):
    respone = self._get_raw("{}/{}/plan".format(EVCC_API_LOADPOINT, lpid))
    if respone.status_code == 404:
      return None
    return respone.json()
  
  def get_sessions(self):
    self.evcc_sessions = self._get(EVCC_API_SESSIONS)["result"]
    return self.evcc_sessions
  
  def get_state(self):
    self.evcc_state = self._get(EVCC_API_STATE)["result"]
    return self.evcc_state
  
  def get_tariff(self):
    tariff_array = {}
    for tariff in EVCC_API_TARIFF_TYPES:
      typed_tariff = self._get(EVCC_API_TARIFF + "/" + tariff)["result"]
      tariff_array[tariff] = typed_tariff
    self.evcc_tarrifs = tariff_array
    return self.evcc_tarrifs

  def get_telemetry(self):
    return self._get(EVCC_API_TELEMETRY)["result"]
  
  def set_battery_buffer_soc(self, soc: int):
    return self._post("{}/{}".format(EVCC_API_BATTERY_BSOC, soc))
  
  def set_battery_buffer_start_soc(self, soc: int):
    return self._post("{}/{}".format(EVCC_API_BATTERY_BSTARTSOC, soc))
  
  def set_battery_discharge_control(self, state: bool):
    if state:
      return self._post("{}/{}".format(EVCC_API_BATTERY_DISCHARGECONTROL, True))
    else:
      return self._post("{}/{}".format(EVCC_API_BATTERY_DISCHARGECONTROL, False))
          
  def set_battery_priority_soc(self, soc: int):
    return self._post("{}/{}".format(EVCC_API_BATTERY_PSOC, soc))
  
  def set_grid_residual_power(self, power: int):
    return self._post("{}/{}".format(EVCC_API_GRID_RESPOWER, power))
  
  def set_smart_cost_limit(self, cost: float):
    return self._post("{}/{:.2f}".format(EVCC_API_SMART_COST_LIMIT, cost))

  def set_telemetry_state(self, state: bool):
    if state:
      return self._post("{}/{}".format(EVCC_API_TELEMETRY, True))
    else:
      return self._post("{}/{}".format(EVCC_API_TELEMETRY, False))

  def _check_vehicle(self, vehicle: str) -> bool:
    self.evcc_state = self.get_state()
    if vehicle not in self.evcc_state["vehicles"]:
      return False
    return True

  def set_vehicle_minsoc(self, vehicle: str, soc: int):
    # get current state so we can check the vehicle actually exists
    if self._check_vehicle(vehicle):
      return self._post("{}/{}/{}/{}".format(EVCC_API_VEHICLE, vehicle, EVCC_API_VEHICLE_MINSOC, soc))
    return False

  def set_vehicle_limitsoc(self, vehicle: str, soc: int):
    # get current state so we can check the vehicle actually exists
    if self._check_vehicle(vehicle):
      return self._post("{}/{}/{}/{}".format(EVCC_API_VEHICLE, vehicle, EVCC_API_LIMITSOC, soc))
    return False
  
  def create_vehicle_loadplan(self, vehicle: str, soc: int, finish: datetime):
    # can't create plans in the past
    ft = datetime.fromtimestamp(finish.timestamp, tz=timezone.utc)
    if ft < datetime.now(tz=timezone.utc):
      return False
    # check if vehicle exists
    if self._check_vehicle(vehicle):
      return self._post("{}/{}/{}/{}/{}".format(EVCC_API_VEHICLE, vehicle, EVCC_API_VEHICLE_PLANSOC, soc, ft.isoformat()))
    return False

  def delete_vehicle_loadplan(self, vehicle: str):
    if self._check_vehicle(vehicle):
      return self._delete("".format(EVCC_API_VEHICLE, vehicle, EVCC_API_VEHICLE_PLANSOC))
    return False

  def _check_loadpoint(self, lp: int):
    self.evcc_state = self.get_state()
    if "loadpoints" in self.evcc_state:
      if lp < len(self.evcc_state["loadpoints"]):
        return True
    return False
  
  def set_loadpoint_mode(self, lp: int, mode: str):
    if self._check_loadpoint(lp):
      if mode.lower() not in EVCC_LP_MODES:
        return
      return self._post("{}/{}/mode/{}".format(EVCC_API_LOADPOINT, lp, mode.lower()))
    return False

  def set_loadpoint_limitsoc(self, lp: int, soc: int):
    if self._check_loadpoint(lp):
      return self._post("{}/{}/{}/{}".format(EVCC_API_LOADPOINT, lp, EVCC_API_LIMITSOC, soc))
    return False
  
  def set_loadpoint_limitenergy(self, lp:int, energy: int):
    if self._check_loadpoint(lp):
      return self._post("{}/{}/energy/{}".format(EVCC_API_LOADPOINT, lp, energy))
    return False
      
  def set_loadpoint_chargeplan(self, lp: int, energy: int, finish: datetime):
    if energy < 1:
      return False
    ft = datetime.fromtimestamp(finish.timestamp, tz=timezone.utc)
    if ft < datetime.now(tz=timezone.utc):
      return False
    if self._check_loadpoint(lp):
      return self._post("{}/{}/plan/energy/{}/{}".format(EVCC_API_LOADPOINT, lp, energy, ft.isoformat()))
    return False

  def delete_loadpoint_plan(self, lp: int, plan: int):
    if self._check_loadpoint(lp):
      return self._delete("{}/{}/plan/energy".format(EVCC_API_LOADPOINT, lp,))
    return False
  
  def get_loadpoint_plan(self, lp: int):
    if self._check_loadpoint(lp):
      return self._get("{}/{}/plan".format(EVCC_API_LOADPOINT, lp))
    return False
  
  def set_loadpoint_phases(self, lp: int, phases: int):
    if self._check_loadpoint(lp):
      return self._post("{}/{}/phases/{}".format(EVCC_API_LOADPOINT, lp, phases))
    return False
  
  def set_loadpoint_mincurrent(self, lp: int, current: float):
    if self._check_loadpoint(lp):
      return self._post("{}/{}/mincurrent/{}".format(EVCC_API_LOADPOINT, lp, current))
    return False  

  def set_loadpoint_maxcurrent(self, lp: int, current: float):
    if self._check_loadpoint(lp):
      return self._post("{}/{}/maxcurrent/{}".format(EVCC_API_LOADPOINT, lp, current))
    return False  
      
  def set_loadpoint_threshold_enable(self, lp:int, thre: int):
    if self._check_loadpoint(lp):
      return self._post("{}/{}/enable/threshold/{}".format(EVCC_API_LOADPOINT, lp, thre))
    return False

  def set_loadpoint_threshold_disable(self, lp:int, thre: int):
    if self._check_loadpoint(lp):
      return self._post("{}/{}/disable/threshold/{}".format(EVCC_API_LOADPOINT, lp, thre))
    return False

  def set_loadpoint_vehicle(self, lp: int, vehicle: str):
    if self._check_loadpoint(lp):
      if self._check_vehicle(vehicle):
        return self._post("{}/{}/vehicle/{}".format(EVCC_API_LOADPOINT, lp, vehicle))
    return False
  
  def remove_loadpoint_vehicle(self, lp: int):
    if self._check_loadpoint(lp):
      return self._delete("{}/{}/vehicle".format(EVCC_API_LOADPOINT, lp))
    return False
  
  def loadpoint_start_vehicle_detechtion(self, lp: int):
    if self._check_loadpoint(lp):
      return self._patch("{}/{}/vehicle".format(EVCC_API_LOADPOINT, lp))
    return False
