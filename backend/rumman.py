from qiskit import QuantumCircuit, Aer, execute
import random

def measure_qubit(qc, qubit_to_measure, cbit):
    
    qc.measure(qubit_to_measure, cbit)
    
    simulator = Aer.get_backend('qasm_simulator')
    result = execute(qc, simulator, shots=1).result()
    
    measurement_result = result.get_counts(qc)
    measured_value = list(measurement_result.keys())[0][cbit]
    return measured_value

def create_game_circuit(num_characters):
    
    num_qubits = num_characters * 3
    qc = QuantumCircuit(num_qubits, num_qubits)

    for i in range(num_qubits):
        qc.h(i)

    pairs = []
    used_qubits = set()
    while len(pairs) < num_characters * 3 // 2: 
        alice_qubit = random.choice([q for q in range(num_qubits) if q not in used_qubits])
        bob_qubit = random.choice([q for q in range(num_qubits) if q not in used_qubits and q // 3 != alice_qubit // 3])
        pairs.append((alice_qubit, bob_qubit))
        used_qubits.update([alice_qubit, bob_qubit])

    for alice_qubit, bob_qubit in pairs:
        qc.cx(alice_qubit, bob_qubit)
    
    return qc, pairs

num_characters = int(input("Enter the number of characters (up to 10): "))
num_characters = min(num_characters, 20)  

qc, pairs = create_game_circuit(num_characters)

print("Circuit:")
print(qc)

qubit_to_measure = int(input(f"Which qubit would you like to measure (0-{num_characters*3-1})? "))
measured_value = measure_qubit(qc, qubit_to_measure, qubit_to_measure)
print(f"Measurement result for qubit {qubit_to_measure}: {measured_value}")