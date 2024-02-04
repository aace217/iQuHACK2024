# okay let's go

from qiskit import QuantumCircuit as qc, ClassicalRegister as cr
import qiskit.circuit.library as qlib
from qiskit.quantum_info import Statevector as sv
import matplotlib as mpl
import matplotlib.pyplot as plt
from enum import Enum
import numpy as np
import random


CHAR_COUNT = 6
EPS = 1e-10

TRAIT_COUNT = 5
class Trait(Enum):
	HAIR_COLOR = 0
	EYE_COLOR = 1
	HAIR_LENGTH = 2
# https://quantumcomputing.stackexchange.com/questions/14305/partial-measurement-of-quantum-circuit-in-qiskit
	
class Ops(Enum):
	Measure = -1

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
		self.is_alive = [] if is_alive is None else [np.copy(x) for x in is_alive]
		self.circuit = circuit.copy() if circuit else qc(trait_count)
		if statevec:
			#self.chars = [c.copy() for c in chars]
			self.statevec = [s.copy() for s in statevec]
		else:
			self.statevec = [sv.from_label("0"*trait_count) for _ in range(char_count)] # qubits are c0t0, c0t1, etc.
			#TODO: entangle them or something idc

	def copy(self): return BoardState(self.char_count, self.trait_count, self.who, self.is_alive, self.statevec, self.remaining, self.circuit)
	def is_done(self): return len(np.unique(np.array(self.is_alive).T,return_counts=True,axis=0)[1]) == self.char_count
	def is_lost(self): return not self.remaining[Ops.Measure]
	def __str__(self):
		return f"BoardState\n  who: {self.who}\n  is_alive: {self.is_alive}\n  statevector: {self.statevec}\n  probabilities: {self.render_probs()}\n  circuit: \n{self.circuit}"
	def draw(self,filename):
		mpl.use("agg")
		img = self.circuit.draw(output="mpl", interactive=False)
		plt.savefig(filename)
		plt.close()
		# return img
	def print_chars(self):
		return [s.draw(output="latex_source",max_size=1024) for s in self.statevec]
	def print_alive(self):
		return [",".join(str(i) for i in x) for x in np.array(self.is_alive).T]
		
	def measure(self, t:Trait):
		assert self.legal(Ops.Measure)
		tc,cc = self.trait_count,self.char_count
		assert 0<=t<tc
		outcome, new_c = list(zip(*[s.measure([t]) for s in self.statevec])) #self.statevec.measure((t+self.who*tc,))#
		outcome = np.array([int(x) for x in outcome])
		print(f"{t}-th bits measured!")
		print(f"outcome: {outcome}")
		print(f"new statevector: {new_c}")
		new_state = self.copy()
		new_state.statevec = list(new_c)
		print(self.is_alive, (outcome ^ outcome[self.who]))
		new_state.is_alive.append(outcome)
		new_state.remaining = self.remaining | {Ops.Measure: self.remaining[Ops.Measure]-1}
		# if not new_state.remaining[Ops.Measure]: del new_state.remaining[Ops.Measure]
		new_state.circuit = self.circuit.copy()
		new_state.circuit.add_register(cr(1))
		new_state.circuit.measure(t,-1)
		return new_state
	
	def legal(self, op:Ops):
		return True#op in self.remaining and self.remaining[op]

	# def query(self, ):
	# 	tc = self.trait_count
	
	def gate(self, gate: Gate, target: Trait):
		assert self.legal(gate)
		tc, cc = self.trait_count, self.char_count
		assert 0<=target<tc
		new_state = self.copy()
		for c in range(cc):
			new_state.statevec[c] = self.statevec[c].evolve(Q_GATES[gate](), qargs=(target,))
		new_state.remaining = self.remaining | {gate: self.remaining[gate]-1}
		# if not new_state.remaining[gate]: del new_state.remaining[gate]
		new_state.circuit = self.circuit.copy()
		new_state.circuit.append(Q_GATES[gate](),qargs=(target,))
		return new_state

	def c_gate(self, c_gate: CGate, source: Trait, target: Trait):
		assert self.legal(c_gate)
		tc, cc = self.trait_count, self.char_count
		assert 0<=source<tc and 0<=target<tc and source != target
		new_state = self.copy()
		for c in range(cc):
			new_state.statevec[c] = new_state.statevec[c].evolve(Q_GATES[c_gate](), qargs=(source,target,))
		new_state.remaining = self.remaining | {c_gate: self.remaining[c_gate]-1}
		new_state.circuit = self.circuit.copy()
		new_state.circuit.append(Q_GATES[c_gate](),qargs=(source,target))
		# if not new_state.remaining[c_gate]: del new_state.remaining[c_gate]
		return new_state

	def render_probs(self):
		cc, tc = self.char_count, self.trait_count
		b = []
		for i in range(cc):
			bzzt = [self.statevec[i].probabilities([j])[1] for j in range(tc)]
			b.append([2 if j>1-EPS else 0 if j<0+EPS else 1 for j in bzzt])
		return b

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
	bs.draw("out.png")