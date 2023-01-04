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
		self.soc = getValues.get('Battery_C')
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
	block: bool
	booster: bool

	def __init__(self):
		return

	def parseData(self, id, dataRow):
		self.id = id

		self.p = dataRow.get('wallbox' + str(id) + '_power')
		self.connection = dataRow.get('wallbox' + str(id) + '_connection')
		self.block = dataRow.get('wallbox' + str(id) + '_blockCharging')
		self.booster = dataRow.get('wallbox' + str(id) + '_boosterState')

		return self

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

	machine: str
	serial: str
	type: str

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

	def __queryStatusApi(self):
		start = time.time()

		request = requests.get("http://%s/data_row/" % self.endpoint, timeout=1)
		self.__dataRow = request.json()

		request = requests.get("http://%s/plantCheck/" % self.endpoint, timeout=1)
		self.__plantCheck = request.json()

		request = requests.get("http://%s/info/" % self.endpoint, timeout=1)
		self.__info = request.json()

		request = requests.get("http://%s/info/" % self.endpoint, timeout=1)
		self.__info = request.json()

		request = requests.get("http://%s/auth/" % self.endpoint, timeout=1, headers={"Authorization": base64.b64encode(b'Basic hycube:hycube')})
		auth = request.content

		request = requests.get("http://%s/get_values/" % self.endpoint, timeout=1, headers={"Authorization": auth})
		self.__getValues = request.json()

		end = time.time()
		print("Requesting API took %.0fms" % round((end - start)*1000, 0))

	def requestStatus(self):
		response = {}
		try:
			self.__queryStatusApi()
		except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
			return

		# TODO: complete info parsing
		self.machine = self.__info.get('HYCUBE_MACHINE')
		self.serial = self.__info.get('HYCUBE_SERIAL')
		self.type = self.__info.get('HYCUBE_TYPE')

		self.battery = HycubeBattery().parseData(self.__dataRow, self.__getValues, self.__plantCheck)
		self.grid = HycubeGrid().parseData(self.__getValues)
		self.inverter = HycubeInverter().parseData(self.__getValues)
		self.home = HycubeHome().parseData(self.__getValues)
		self.wallbox1 = HycubeWallbox().parseData(1, self.__dataRow)
		self.wallbox2 = HycubeWallbox().parseData(2, self.__dataRow)
		self.wallbox3 = HycubeWallbox().parseData(3, self.__dataRow)
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
