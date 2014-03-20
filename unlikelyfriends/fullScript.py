#!/usr/bin python

import facebook
import bitarray
import sys
import ast
import heapq
import math
import threading
import json

if (len(sys.argv) > 1):
  oauth = sys.argv[1]
  # Holds the indeces of each FB friend
  indeces = {}
  # Remembers which mutual friendships have already been checked
  checked = {}
  # Stores who is friends with who else!
  lock = threading.Lock()
  mutual_friendships = {}
  # Stores bitarrays with that same data
  mutual_friendships_bit = {}
  # Stores the list of friends, ordered by friend id
  raw_friends = []
  # Number of mutual friends for any given friend
  num_mutual = {}
  heap_stl = []

  #  # Prevent the program from downloading the mutual friendlist repeated, as this
  # takes forever
  graph = facebook.GraphAPI(oauth)
  profile = graph.get_object("me")
  friends = graph.get_connections("me", "friends")
  raw_friends = friends['data']

  #Calls the graph API for mutual friends
  # Written in a seperate method to allow multithreading
  def get_mutual(friend, counter):
    # Init a bit array to store mutual friendships
    friend_id = friend['id']
    # Get mutual friends
    mutual = graph.get_connections(friend_id, "mutualfriends")
    raw_mutual = mutual['data']
    raw_mutual_list = []
    for mutual_friend in raw_mutual:
      mutual_friend_id = mutual_friend['id']
      raw_mutual_list.append(mutual_friend_id)
    lock.acquire()
    mutual_friendships[friend_id] = raw_mutual_list
    lock.release()
    #print "Done one!" + str(counter)
    counter = counter + 1

  # init the data structures
  counter = 0
  for friend in raw_friends:
    friend_id = friend['id']
    indeces[friend_id] = counter
    counter = counter + 1

  length = len(raw_friends)

  counter = 0
  threads = []

  for friend in raw_friends:
    t = threading.Thread(target=get_mutual, args=(friend,counter))
    t.daemon = True
    threads.append(t)
    counter = counter + 1

  [x.start() for x in threads]
  [x.join() for x in threads]

  # Convert the mutual friendships into bit arrays
  for friend in raw_friends:
    friend_id = friend['id']
    mutual_friends = mutual_friendships[friend_id]
    # Calculate a bit array where 1's represent mutual friendships
    bits = length * bitarray.bitarray('0')
    for mutual in mutual_friends:
      index = indeces[mutual]
      bits[index - 1] = 1
    mutual_friendships_bit[friend_id] = bits

  for friend in raw_friends:
    friend_id = friend['id']
    friend_bits = mutual_friendships_bit[friend_id]

    num_mutual_friends = friend_bits.count()

    # Count the number of mutual friends the current friend has
    if friend_id not in num_mutual:
      num_mutual[friend_id] = friend_bits.count()

    for mutual_friend in mutual_friendships[friend_id]:
      # Count the number of mutual friends the current friend has
      if mutual_friend in mutual_friendships_bit:
        mutual_bits = mutual_friendships_bit[mutual_friend]
        if mutual_friend not in num_mutual:
          num_mutual[mutual_friend] = mutual_bits.count()

        if (mutual_friend, friend_id) not in checked:
          # And 'em
          and_bits = friend_bits & mutual_bits
          # Count shared friends an no of mutual friends
          counter = 0
          # Count the number of shared mutual friends
          and_bit_count = and_bits.count()
          # Calculate the metric:
          unique_a = num_mutual[friend_id] - and_bit_count
          unique_b = num_mutual[mutual_friend] - and_bit_count

          metric = float(and_bit_count + 1) / (unique_a + unique_b)
          to_push = (metric, (friend_id, mutual_friend))

          heapq.heappush(heap_stl, to_push)
          checked[(friend_id, mutual_friend)] = 1

  least = {}
  for i in range(1,100):
    (c, (f1,f2)) =  heapq.heappop(heap_stl)
    info = {}
    info['coefficient'] = c
    info['friend_one'] = f1
    info['friend_two'] = f2
    least[i] = info

  print json.dumps({'matches': least})
else:
  print "Need to pass in an auth token!"
