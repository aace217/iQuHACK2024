# okay let's go

#import qiskit as qk
from qiskit.quantum_info import Statevector as sv
from enum import Enum
import numpy as np
import random

CHAR_COUNT = 1

TRAIT_COUNT = 3
class Trait(Enum):
	HAIR_COLOR = 0
	EYE_COLOR = 1
	HAIR_LENGTH = 2
# https://quantumcomputing.stackexchange.com/questions/14305/partial-measurement-of-quantum-circuit-in-qiskit
	
class BoardState:
	def __init__(self, char_count = CHAR_COUNT, who = -1, is_alive = None, chars = None, turn = 0):
		self.char_count = char_count
		self.who = who if who+1 else random.randrange(char_count)
		self.is_alive = np.ones(char_count,dtype=bool) if is_alive is None else np.copy(is_alive)
		if chars:
			#self.chars = [c.copy() for c in chars]
			self.chars = chars.copy()
		else:
			self.chars = sv.from_label("+"*(char_count*TRAIT_COUNT)) # qubits are c0t0, c0t1, etc.
			#TODO: entangle them or something idc

	def copy(self): return BoardState(self.char_count, self.who, self.is_alive, self.chars)
	def is_done(self): return np.unique(self.is_alive,return_counts=True)[1][1] == 1
	def __str__(self):
		return f"BoardState\n  who: {self.who}\n  is_alive: {self.is_alive}\n  statevector: {self.chars}"

	def measure(self, t:Trait):
		outcome, new_c = self.chars.measure(range(t,len(self.chars.dims()),TRAIT_COUNT))
		outcome = np.array([int(x) for x in outcome])
		print(f"bits {range(t,len(self.chars.dims()),TRAIT_COUNT)} measured!")
		print(f"outcome: {outcome}")
		print(f"new statevector: {new_c}")
		new_state = self.copy()
		new_state.chars = new_c
		print(self.is_alive, (outcome ^ outcome[self.who]))
		new_state.is_alive = self.is_alive & (outcome ^ outcome[self.who])
		return new_state
	

bs = BoardState()
print(bs)
bs = bs.measure(0)
print(bs)
bs = bs.measure(2)
print(bs)
bs = bs.measure(1)
print(bs)









