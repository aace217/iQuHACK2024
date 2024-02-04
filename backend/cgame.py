# okay let's go

from qiskit import QuantumCircuit as qc
import qiskit.circuit.library as qlib
from qiskit.quantum_info import Statevector as sv
from enum import Enum
import numpy as np
import random

CHAR_COUNT = 1

TRAIT_COUNT = 5
class Trait(Enum):
	HAIR_COLOR = 0
	EYE_COLOR = 1
	HAIR_LENGTH = 2
# https://quantumcomputing.stackexchange.com/questions/14305/partial-measurement-of-quantum-circuit-in-qiskit
	
class Gate(Enum):
	X = 0
	Z = 1
	H = 4

class CGate(Enum):
	CX = 2
	CZ = 3

Q_GATES = {
	Gate.X: qlib.XGate,
	Gate.Z: qlib.ZGate,
	CGate.CX: qlib.CXGate,
	CGate.CZ: qlib.CZGate,
	Gate.H: qlib.HGate
}

class Ops(Gate, CGate, Enum):
	Measure = -1

	
class BoardState:
	def __init__(self, char_count = CHAR_COUNT, trait_count = TRAIT_COUNT, who = -1, is_alive = None, statevec = None, remaining = None, circuit = None):
		self.char_count = char_count
		self.trait_count = trait_count
		self.who = who if who+1 else random.randrange(char_count)
		self.remaining = {k:v for k,v in remaining.items()} if remaining else {Ops.Measure:trait_count-1}
		self.is_alive = np.ones(char_count,dtype=bool) if is_alive is None else np.copy(is_alive)
		self.circuit = circuit.copy() if circuit else qc(trait_count)
		if statevec:
			#self.chars = [c.copy() for c in chars]
			self.statevec = statevec.copy()
		else:
			self.statevec = sv.from_label("+"*(char_count*trait_count)) # qubits are c0t0, c0t1, etc.
			#TODO: entangle them or something idc

	def copy(self): return BoardState(self.char_count, self.trait_count, self.who, self.is_alive, self.statevec, self.remaining, self.circuit)
	def is_done(self): return np.unique(self.is_alive,return_counts=True)[1][1] == 1
	def __str__(self):
		return f"BoardState\n  who: {self.who}\n  is_alive: {self.is_alive}\n  statevector: {self.statevec}\n  probabilities: {self.render_probs()}"

	def measure(self, t:Trait):
		assert self.legal(Ops.Measure)
		tc = self.trait_count
		outcome, new_c = self.statevec.measure((t+self.who*tc,))#self.chars.measure(range(t,len(self.chars.dims()),TRAIT_COUNT))
		outcome = np.array([int(x) for x in outcome])
		print(f"bits {range(t,len(self.statevec.dims()),tc)} measured!")
		print(f"outcome: {outcome}")
		print(f"new statevector: {new_c}")
		new_state = self.copy()
		new_state.statevec = new_c
		print(self.is_alive, (outcome ^ outcome[self.who]))
		new_state.is_alive = self.is_alive & (outcome ^ outcome[self.who])
		new_state.remaining = self.remaining | {Ops.Measure: self.remaining[Ops.Measure]-1}
		new_state.circuit = self.circuit.copy().measure(t)
		return new_state
	
	def legal(self, op:Ops):
		return op in self.remaining and op[self.remaining]

	# def query(self, ):
	# 	tc = self.trait_count
	
	def gate(self, gate: Gate, source: Trait):
		assert self.legal(gate)
		tc = self.trait_count
		source_bit = source[0]*tc+source[1]
		new_state = self.copy()
		new_state.statevec = self.statevec.evolve(Q_GATES[gate](), qargs=(source_bit,))
		new_state.remaining = self.remaining | {gate: self.remaining[gate]-1}
		return new_state

	def c_gate(self, c_gate: CGate, source: Trait, target: Trait):
		assert self.legal(c_gate)
		tc = self.trait_count
		source_bit = source[0]*tc+source[1]
		target_bit = target[0]*tc+target[1]
		new_state = self.copy()
		new_state.statevec = self.statevec.evolve(Q_GATES[c_gate](),qargs=(source_bit,target_bit))
		new_state.remaining = self.remaining | {c_gate: self.remaining[c_gate]-1}
		return new_state

	def render_probs(self):
		cc, tc = self.char_count, self.trait_count
		bzzt = [self.statevec.probabilities([i])[1] for i in range(cc*tc)]
		bzzt = [2 if j==1 else 0 if j==0 else 1 for j in bzzt]
		return [bzzt[i*tc:(i+1)*tc] for i in range(cc)]

if __name__ == "__main__":
	bs = BoardState()
	print(bs)
	bs = bs.measure(0)
	print(bs)
	bs = bs.measure(2)
	print(bs)
	bs = bs.gate(Gate.X, (0,0))
	print(bs)
	bs = bs.measure(1)
	print(bs)