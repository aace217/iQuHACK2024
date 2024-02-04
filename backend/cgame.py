# okay let's go

from qiskit import QuantumCircuit as qc, ClassicalRegister as cr
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
	
class Ops(Enum):
	Measure = -1
	H = 0
	X = 1
	Z = 2
	CX = 3
	CZ = 4

class Gate(Enum):
	H = 0
	X = 1
	Z = 2

class CGate(Enum):
	CX = 3
	CZ = 4

Q_GATES = {
	Gate.H: qlib.HGate,
	Gate.X: qlib.XGate,
	Gate.Z: qlib.ZGate,
	CGate.CX: qlib.CXGate,
	CGate.CZ: qlib.CZGate,
}



	
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
		return f"BoardState\n  who: {self.who}\n  is_alive: {self.is_alive}\n  statevector: {self.statevec}\n  probabilities: {self.render_probs()}\n  circuit: \n{self.circuit}"
	def draw(self):
		return self.circuit.draw(output="mpl")
	def measure(self, t:Trait):
		assert self.legal(Ops.Measure)
		tc = self.trait_count
		assert 0<=t<tc
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
		new_state.circuit = self.circuit.copy()
		new_state.circuit.add_register(cr(1))
		new_state.circuit.measure(t,-1)
		return new_state
	
	def legal(self, op:Ops):
		return op in self.remaining and self.remaining[op]

	# def query(self, ):
	# 	tc = self.trait_count
	
	def gate(self, gate: Gate, target: Trait):
		assert self.legal(gate)
		tc, cc = self.trait_count, self.char_count
		assert 0<=target<tc
		new_state = self.copy()
		for t_bit in range(target,tc*cc,tc):
			new_state.statevec = new_state.statevec.evolve(Q_GATES[gate](), qargs=(t_bit,))
		new_state.remaining = self.remaining | {gate: self.remaining[gate]-1}
		new_state.circuit = self.circuit.copy()
		new_state.circuit.append(Q_GATES[gate](),qargs=(target,))
		return new_state

	def c_gate(self, c_gate: CGate, source: Trait, target: Trait):
		assert self.legal(c_gate)
		tc, cc = self.trait_count, self.char_count
		assert 0<=source<tc and 0<=target<tc
		new_state = self.copy()
		for i in range(0,tc*cc,tc):
			new_state.statevec = new_state.statevec.evolve(Q_GATES[c_gate](), qargs=(i+source,i+target,))
		new_state.remaining = self.remaining | {c_gate: self.remaining[c_gate]-1}
		new_state.circuit = self.circuit.copy()
		new_state.circuit.append(Q_GATES[c_gate](),qargs=(source,target))
		return new_state

	def render_probs(self):
		cc, tc = self.char_count, self.trait_count
		bzzt = [self.statevec.probabilities([i])[1] for i in range(cc*tc)]
		bzzt = [2 if j==1 else 0 if j==0 else 1 for j in bzzt]
		return [bzzt[i*tc:(i+1)*tc] for i in range(cc)]

if __name__ == "__main__":
	bs = BoardState(remaining={Ops.Measure:99,Gate.X:99,CGate.CX:99})
	print(bs)
	bs = bs.measure(0)
	print(bs)
	bs = bs.measure(2)
	print(bs)
	bs = bs.gate(Gate.X, 0)
	print(bs)
	bs = bs.c_gate(CGate.CX,4,3)
	print(bs)
	bs = bs.measure(1)
	print(bs)