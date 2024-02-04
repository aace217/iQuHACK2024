from qiskit import QuantumCircuit, Aer, execute
import random
import numpy as np

NUM_CHARACTERS = 4
TRAITS_PER_CHARACTER = 5
NUM_QUBITS = NUM_CHARACTERS * TRAITS_PER_CHARACTER

colors = ['red', 'blue', 'orange', 'green', 'black']
trait_color_pairs = {}

def generate_color_pairs():
    all_color_pairs = [(colors[i], colors[j]) for i in range(len(colors)) for j in range(i+1, len(colors))]
    random.shuffle(all_color_pairs)
    for trait in range(TRAITS_PER_CHARACTER):
        trait_color_pairs[trait] = all_color_pairs.pop()

def entangle_corresponding_qubits_correctly(qc, num_characters, traits_per_character):
    generate_color_pairs()  
    for trait in range(traits_per_character):
        qubit_indices = [trait + i*traits_per_character for i in range(num_characters)]
        random.shuffle(qubit_indices)
        while qubit_indices:
            qubit1 = qubit_indices.pop()
            if qubit_indices:
                qubit2 = qubit_indices.pop()
                qc.cx(qubit1, qubit2)

def create_game_circuit():
    qc = QuantumCircuit(NUM_QUBITS, NUM_QUBITS)
    for i in range(NUM_QUBITS):
        qc.h(i)
    entangle_corresponding_qubits_correctly(qc, NUM_CHARACTERS, TRAITS_PER_CHARACTER)
    return qc
determinedTraits = {}
for i in range(20):
    determinedTraits[i] = None
def measure_trait(qc, trait_index):
    if determinedTraits[trait_index] != None:
        return determinedTraits[trait_index],None,trait_index,None
    group = trait_index % TRAITS_PER_CHARACTER
    color_pair = trait_color_pairs[group]

    entangled_trait_index = None
    for instruction in qc.data:
        if instruction[0].name == 'cx':
            qubits = [q.index for q in instruction[1]]
            if trait_index in qubits:
                entangled_trait_index = qubits[1] if qubits[0] == trait_index else qubits[0]
                break
    
    if entangled_trait_index is None:
        raise ValueError(f"Qubit {trait_index} is not entangled with any other qubit.")
    
    qc.measure(trait_index, trait_index)
    qc.measure(entangled_trait_index, entangled_trait_index)
    
    simulator = Aer.get_backend('qasm_simulator')
    result = execute(qc, simulator, shots=1).result()
    measurement_result = result.get_counts(qc)
    outcome = list(measurement_result.keys())[0]

    measured_binary = outcome[::-1][trait_index] 
    entangled_binary = outcome[::-1][entangled_trait_index]

    trait_color = color_pair[int(measured_binary)]
    entangled_color = color_pair[1 - int(measured_binary)] 
    determinedTraits[trait_index] = trait_color
    determinedTraits[entangled_trait_index] = entangled_color
    return trait_color, entangled_color, trait_index, entangled_trait_index

turn = 0
peopleNumber = 4
traitNumber = 5
players = random.sample(range(1, 5), 2)

class BoardState:
    def __init__(self,turn = random.randrange(0,1),player1Number = players[0], player2Number = players[1]):
        self.qc = create_game_circuit()
        self.player1Matrix = np.full((traitNumber,peopleNumber),None)
        self.player2Matrix = np.full((traitNumber,peopleNumber),None)
    def setMatrix(self):
        if turn%2 == 0:
            self.currentMatrix = self.player1Matrix
        else:
            self.currentMatrix = self.player2Matrix
    def updateMatrix(self,inputIndex):
        trait_color, entangled_color, trait_index, entangled_trait_index = measure_trait(self.qc,inputIndex)
        if((entangled_color != None) and (entangled_trait_index != None)):
            self.currentMatrix[entangled_trait_index % 5][entangled_trait_index//5 + 1] = entangled_color
        if self.currentMatrix[trait_index % 5][trait_index//5 + 1] == None:
            self.currentMatrix[trait_index % 5][trait_index//5 + 1] = trait_color
        self.turn = self.turn + 1
        return self.currentMatrix  ##TODO:send currentMatrix to front end
    #TODO: check if game is over
    #def isOver(self):
        #if all revealed or all things correct

