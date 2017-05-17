import sys
import time
import random

# Constants.
DRIVER = -2
WALKER = -1

# This variable holds all trip vertices. This is our representation of
# the graph model.
graph = {}

# This variable keeps track of the maximum benefit achieved by any
# valid configuration.
max_benefit = -1

# Vertex: each trip is an instance of the vertex class.
class Vertex:
  trip_id = -1 # Valid values have to be positive.
  benefit = 0
  num_passengers = 0
  vacant_seats = 0
  occupied_seats = 0
  extra_passengers = []

  # True if this vertex is a driver but is not a passenger.
  is_exclusive_driver = False

  # The cursor holds the position of the current active edge in the adjacency list.
  cursor = 0

  # This variable holds the cursor position that achieved maximum benefit.
  saved_cursor = 0

  # Adjacency list for this vertex.
  adj_list = []

  def __init__(self, trip_id, passenger = True, driver = True, num_passengers = 1, vacant_seats = 2, benefit = 2):
    self.adj_list = []

    # Beyond all possible sharing combinations, passengers can still walk to
    # their destination and passenger-drivers can decide to drive. These possibilities are
    # represented by the global unique values DRIVER AND WALKER.
    if driver: self.adj_list.append(DRIVER)
    if passenger: self.adj_list.append(WALKER)

    self.trip_id = trip_id
    self.num_passengers = num_passengers
    self.vacant_seats = vacant_seats - num_passengers
    self.benefit = benefit
    self.occupied_seats = 0
    self.cursor = 0
    self.is_exclusive_driver = driver and not passenger
    self.extra_passengers = []

  # Any vertex can be a walker, a passenger or a driver. Positive values are
  # always passengers that are going to take a lift with someone else. Negative
  # values can represent a walker or a driver. For passengers, this function returns 
  # the trip id of the driver, for walkers or drivers it returts -2 or -1.
  def GetRole(self):
    return self.adj_list[self.cursor]

  # The cursor is incremented to create all possible combinations of
  # active edges.
  def IncreaseCursor(self):
    if self.cursor == len(self.adj_list) - 1:
      self.cursor = 0
      return False
    else:
      self.cursor += 1
      return True

  # A vertex is only valid if it is a walker, a driver with a feasible number of 
  # occupied seats, or a passenger in another trip with a valid driver.
  def IsValid(self):
    if self.GetRole() == DRIVER: return self.occupied_seats <= self.vacant_seats
    return self.GetRole() == WALKER or graph[self.GetRole()].GetRole() == DRIVER

  # Only passengers in other trips sum up to the total benefit.
  def GetBenefit(self):
    return self.benefit if self.GetRole() > 0 else 0

  # Saves the current cursor so we can know the configuration that achieved maximum
  # benefit.
  def SaveCursor(self):
    self.saved_cursor = self.cursor

  # Updates the number of occupied seats in every trip with a driver.
  def OccupySeats(self):
    if self.GetRole() >= 0:
      graph[self.GetRole()].occupied_seats += self.num_passengers

  # Adds an edge representing a sharing possibility.
  def AddSharing(self, sharing):
    if self.is_exclusive_driver: return
    self.adj_list.append(sharing)

  # Keeps track of which trips take which passengers. This is only used to properly print
  # the final result.
  def AddPassenger(self, passenger_id):
    self.extra_passengers.append(str(passenger_id))

# Active edges are incremented in a way to make every possible combination of active 
# vertices occur a single time.
def IncreaseCursor():
  for key in reversed(graph.keys()):
    if graph[key].IncreaseCursor(): return True
  return False

# Checks if a given configuration of active vertices is valid.
def CheckValidity():
  for i in graph.keys():
    if not graph[i].IsValid(): return False
  return True 

# Sums up the benefits of each trip to find the total benefit of this configuration.
def GetTotalBenefit():
  global max_benefit
  total_benefit = 0
  for i in graph.keys():
    total_benefit += graph[i].GetBenefit()
  if total_benefit > max_benefit: 
    max_benefit = total_benefit

    # Record the maximum benefit configuration.
    for i in graph.keys(): graph[i].SaveCursor()
  return total_benefit

# Activates the vertices with maximum benefit and keeps track of which passengers go
# in which trip to print the final result.
def LoadSavedCursors():
  for i in graph.keys(): 
    graph[i].cursor = graph[i].saved_cursor
    if graph[i].GetRole() >= 0:
      passenger_id = graph[i].trip_id
      driver_id = graph[i].GetRole()
      graph[driver_id].AddPassenger(passenger_id)

# This is the main function. It tries every possible configuration of active edges and
# records the one with the maximum benefit.
def CalculateMaxBenefit():
  while True:
    if CheckValidity():
      GetTotalBenefit()
    for i in graph.keys(): graph[i].occupied_seats = 0
    if not IncreaseCursor(): break;
    for i in graph.keys(): graph[i].OccupySeats()

# Reads input from file and creates the sharing graph.
def ReadInput(filename):
  txt = open(filename)
  lines = txt.readlines()

  num_trips = int(lines[0].split()[0])
  for i in range(num_trips):
    arr = lines[1 + i].split()
    trip_id = arr[0]
    passenger = arr[1] == "1"
    driver = arr[2] == "1"
    num_passengers = int(arr[3])
    vacant_seats = int(arr[4])
    benefit = float(arr[5])
    graph[trip_id] = Vertex(trip_id, passenger, driver, num_passengers, vacant_seats, benefit)

  num_sharings = int(lines[num_trips + 1].split()[0])
  for i in range(num_sharings):
    arr = lines[num_trips + 2 + i].split()

    trip_id = arr[0]
    shared_trip_id = arr[1]
    graph[trip_id].AddSharing(shared_trip_id)

# Writes the final result to an output file.
def WriteOutput(filename):
  out = open(filename, 'w+')

  LoadSavedCursors()
  drivers = []
  for i in graph.keys(): 
    if graph[i].GetRole() == DRIVER and len(graph[i].extra_passengers) > 0: 
      drivers.append(graph[i])

  out.write(str(len(drivers)) + " " + str(float(max_benefit)) + "\n")
  print len(drivers), float(max_benefit)
  for driver in drivers:
    driver.extra_passengers.sort()
    out.write(str(driver.trip_id) + " " + ' '.join(driver.extra_passengers) + "\n")
    print str(driver.trip_id), ' '.join(driver.extra_passengers)

# =================================
# Test method to measure complexity.
# =================================

# def GenerateGraph(n, m):
#   for i in range(n): 
#     passenger = True
#     driver = True
# 
#     num_passengers = 1
#     vacant_seats = 10
#     benefit = random.random() * 100
#     graph[i] = Vertex(i, passenger, driver, num_passengers, vacant_seats, benefit)
# 
#   # Generate edges.
#   counter = 0
#   for i in range(n): 
#     for j in range(n): 
#       if i == j: continue
#       if graph[i].is_exclusive_driver: continue
#       counter += 1
#       if counter <= m:
#         graph[i].AddSharing(j)
# 
# for n in range(30):
#   for m in range(30):
#     avg = 0
#     for i in range(1):
#       GenerateGraph(n + 1, m + 1)
#       t0 = time.time()
#       CalculateMaxBenefit() 
#       ms = (time.time() - t0) * 1000
#       avg += ms
#     avg /= 10
#     print "n:", n + 1, "m:", m + 1, "ms:", avg

# =================================
# Main
# =================================

# The program takes 2 arguments. One input file and one output file.
if len(sys.argv) != 3:
  print "Wrong number of arguments"
  sys.exit()

ReadInput(sys.argv[1])
CalculateMaxBenefit() 
WriteOutput(sys.argv[2])
