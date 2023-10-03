from dataclasses import dataclass
import requests
import base64
import time
from enum import Enum
from json.decoder import JSONDecodeError

@dataclass
class HycubeBattery:
	soc: int
	p: float
	i: float
	u: float
	t: float

	def __init__(self):
		return

	def parseData(self, dataRow, getValues, plantCheck):
		self.soc = dataRow.get('BatteryCapacity')
		self.p = dataRow.get('BatteryPower')
		self.t = dataRow.get('temp_bat')

		self.soc = getValues.get('Battery_C')
		self.p = getValues.get('Battery_P')
		self.i = getValues.get('Battery_I')
		self.u = getValues.get('Battery_V')

		return self

@dataclass
class HycubeInverter:
	i1: float
	i2: float
	i3: float
	u1: float
	u2: float
	u3: float
	p1: float
	p2: float
	p3: float

	def __init__(self):
		return

	def parseData(self, getValues):
		self.soc = getValues.get('Battery_C')
		self.p1 = getValues.get('Inv1_P_L1')
		self.p2 = getValues.get('Inv1_P_L2')
		self.p3 = getValues.get('Inv1_P_L3')
		self.u1 = getValues.get('Inv1_V_L1')
		self.u2 = getValues.get('Inv1_V_L2')
		self.u3 = getValues.get('Inv1_V_L3')
		self.i1 = getValues.get('Inv1_I_L1')
		self.i2 = getValues.get('Inv1_I_L2')
		self.i3 = getValues.get('Inv1_I_L3')

		return self

@dataclass
class HycubeGrid:
	i1: float
	i2: float
	i3: float
	u1: float
	u2: float
	u3: float
	p: float
	f: float

	def __init__(self):
		return

	def parseData(self, getValues):
		self.p = getValues.get('Grid_P')
		self.u1 = getValues.get('Grid_V_L1')
		self.u2 = getValues.get('Grid_V_L2')
		self.u3 = getValues.get('Grid_V_L3')
		self.i1 = getValues.get('Grid_I_L1')
		self.i2 = getValues.get('Grid_I_L2')
		self.i3 = getValues.get('Grid_I_L3')
		self.f = getValues.get('Grid_f')

		return self

@dataclass
class HycubeHome:
	p: float

	def __init__(self):
		return

	def parseData(self, getValues):
		self.p = getValues.get('Home_P')

		return self

@dataclass
class HycubeWallbox:
	id: int
	p: float
	connection: bool
	lock: bool
	booster: bool
	carConnected: bool
	carChargingRequest: bool
	chargingMode: int
	minChargingPower: int
	minSolarPower: int
	allowBatDischarging: bool
	phaseCount: int
	chargingPriority: int
	houseMaxFuse: int
	wallboxMaxFuse: int
	name: str
	endpoint: str

	def __init__(self, endpoint: str):
		self.endpoint = endpoint

	def parseData(self, id, dataRow, wallboxGetSettings):
		self.id = id

		self.p = dataRow.get('wallbox' + str(id) + '_power')
		self.connection = dataRow.get('wallbox' + str(id) + '_connection')
		self.lock = dataRow.get('wallbox' + str(id) + '_blockCharging')
		self.booster = dataRow.get('wallbox' + str(id) + '_boosterState')

		value = dataRow.get('wallbox' + str(id) + '_state')
		if value >= 4 and value <= 7:
			self.carConnected = True
		else:
			self.carConnected = False

		value = dataRow.get('wallbox' + str(id) + '_state')
		if value == 6 or value == 7:
			self.carChargingRequest = 1
		else:
			self.carChargingRequest = 0

		self.chargingMode = wallboxGetSettings.get('wallboxSettings').get('Wallbox' + str(id)).get('chargingMode')
		self.minChargingPower = wallboxGetSettings.get('wallboxSettings').get('Wallbox' + str(id)).get('minChargingPower')
		self.minSolarPower = wallboxGetSettings.get('wallboxSettings').get('Wallbox' + str(id)).get('minSolarPower')
		self.allowBatDischarging = wallboxGetSettings.get('wallboxSettings').get('Wallbox' + str(id)).get('allowBatDischarging')

		phaseCount = wallboxGetSettings.get('wallboxSettings').get('Wallbox' + str(id)).get('phase')
		if phaseCount == 0:
			self.phaseCount = 3
		else:
			self.phaseCount = phaseCount

		self.chargingPriority = wallboxGetSettings.get('wallboxSettings').get('Wallbox' + str(id)).get('chargingPriority')
		self.houseMaxFuse = wallboxGetSettings.get('wallboxSettings').get('Wallbox' + str(id)).get('houseMaxFuse')
		self.wallboxMaxFuse = wallboxGetSettings.get('wallboxSettings').get('Wallbox' + str(id)).get('wallboxMaxFuse')
		self.name = wallboxGetSettings.get('wallboxSettings').get('Wallbox' + str(id)).get('Name')

		return self

	def setLock(self, value: bool):
		request = requests.get("http://%s/Wallbox/setBlockCharging/?wallbox=%d&value=%d" % (self.endpoint, self.id, int(value)), timeout=1)

	def setBooster(self, value: bool):
		request = requests.get("http://%s/Wallbox/booster/?wallbox=%d&value=%d" % (self.endpoint, self.id, int(value)), timeout=1)

	def setChargingMode(self, value: int):
		if value < 0 or value > 2:
			# TODO: throw error
			return

		request = requests.get("http://%s/Wallbox/setWallboxMode/?wallbox=%d&mode=%d" % (self.endpoint, self.id, value), timeout=1)

	def setChargingPriority(self, value: bool):
		request = requests.get("http://%s/Wallbox/setPriority/?wallbox=%d&mode=%d" % (self.endpoint, self.id, int(value)), timeout=1)

	def setAllowBatDischarging(self, value: bool):
		request = requests.get("http://%s/Wallbox/batteryDischargingPermission/?wallbox=%d&mode=%d" % (self.endpoint, self.id, int(value)), timeout=1)

	def setMinChargingPower(self, value: int):
		request = requests.get("http://%s/Wallbox/setWallboxMode/?wallbox=%d&mode=1&minChargingPower=%d&minSolarPower=%d" % (self.endpoint, self.id, value, self.minSolarPower), timeout=1)
	
	def setMinSolarPower(self, value: int):
		request = requests.get("http://%s/Wallbox/setWallboxMode/?wallbox=%d&mode=1&minChargingPower=%d&minSolarPower=%d" % (self.endpoint, self.id, self.minChargingPower, value), timeout=1)

	def setWallboxMaxFuse(self, value: int):
		request = requests.get("http://%s/Wallbox/setWallboxMaxFuse/?wallbox=%d&value=%d" % (self.endpoint, self.id, value), timeout=1)
	
	def setHomeMaxFuse(self, value: int):
		request = requests.get("http://%s/Wallbox/setHomeMaxFuse/?wallbox=%d&value=%d" % (self.endpoint, self.id, value), timeout=1)


@dataclass
class HycubeSolar:
	p: float
	p1: float
	p2: float
	u1: float
	u2: float
	i1: float
	i2: float

	def __init__(self):
		return

	def parseData(self, getValues):
		self.p1 = getValues.get('Solar1_P')
		self.u1 = getValues.get('Solar1_V')
		self.i1 = getValues.get('Solar1_I')
		self.p2 = getValues.get('solar2_P')
		self.u2 = getValues.get('Solar2_V')
		self.i2 = getValues.get('Solar2_I')
		self.p = getValues.get('solar_total_P')

		return self

@dataclass
class Hycube:
	endpoint: str
	session: requests.Session

	machine: str
	serial: str
	type: str
	controller: str
	version_hyweb: str
	version_cubeconnect: str

	battery: HycubeBattery
	grid: HycubeGrid
	inverter: HycubeInverter
	home: HycubeHome
	# FIXME: multiple wallboxes!
	wallbox1: HycubeWallbox
	wallbox2: HycubeWallbox
	wallbox3: HycubeWallbox
	solar: HycubeSolar

	def __init__(self, endpoint):
		if (endpoint is None or endpoint == ''):
			raise ValueError("endpoint must be specified")
		self.endpoint = endpoint
		self.session = requests.Session()

	def __queryStatusApi(self):
		start = time.time()

		session = self.session

		request = session.get("http://%s/data_row/" % self.endpoint, timeout=1)
		self.__dataRow = request.json()

		request = session.get("http://%s/plantCheck/" % self.endpoint, timeout=1)
		self.__plantCheck = request.json()

		request = session.get("http://%s/info/" % self.endpoint, timeout=1)
		self.__info = request.json()

		request = session.get("http://%s/Wallbox/getSettings/" % self.endpoint, timeout=1)
		self.__wallboxGetSettings = request.json()

		request = session.get("http://%s/auth/" % self.endpoint, timeout=1, headers={"Authorization": base64.b64encode(b'Basic hycube:hycube')})
		auth = request.content

		request = session.get("http://%s/get_values/" % self.endpoint, timeout=1, headers={"Authorization": auth})
		self.__getValues = request.json()

		end = time.time()
		print("Requesting API took %.0fms" % round((end - start)*1000, 0))

	def requestStatus(self):
		response = {}

		# work around transient errors of the somewhat unreliable API
		retries = 5
		while True:
			try:
				self.__queryStatusApi()
				break
			except requests.exceptions.RequestException as e:
				if retries > 0:
					retries -= 1
					time.sleep(0.2)
					continue
				else:
					raise e

		# TODO: complete info parsing
		self.machine = self.__info.get('HYCUBE_MACHINE')
		self.serial = self.__info.get('HYCUBE_SERIAL')
		self.type = self.__info.get('HYCUBE_TYPE')
		self.controller = self.__info.get('HYCUBE_CONTROLLER')
		self.version_hyweb = self.__info.get('HyWeb_Version')
		self.version_cubeconnect = self.__info.get('CubeConnect_Version')

		self.battery = HycubeBattery().parseData(self.__dataRow, self.__getValues, self.__plantCheck)
		self.grid = HycubeGrid().parseData(self.__getValues)
		self.inverter = HycubeInverter().parseData(self.__getValues)
		self.home = HycubeHome().parseData(self.__getValues)
		self.wallbox1 = HycubeWallbox(self.endpoint).parseData(1, self.__dataRow, self.__wallboxGetSettings)
		self.wallbox2 = HycubeWallbox(self.endpoint).parseData(2, self.__dataRow, self.__wallboxGetSettings)
		self.wallbox3 = HycubeWallbox(self.endpoint).parseData(3, self.__dataRow, self.__wallboxGetSettings)
		self.solar = HycubeSolar().parseData(self.__getValues)

	def printStatus(self):
		print(self.inverter)
		print(self.battery)
		print(self.grid)
		print(self.home)
		print(self.wallbox1)
		print(self.wallbox2)
		print(self.wallbox3)
		print(self.solar)
