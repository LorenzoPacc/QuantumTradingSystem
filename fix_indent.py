with open("quantum_v33_ultimate_final.py", "r") as f:
    lines = f.readlines()

# La riga 957 (indice 956) deve essere indentata di 4 spazi in più
# Attualmente: "    time.sleep(120)"
# Dovrebbe essere: "        time.sleep(120)" (dentro il while)

# OPPURE meglio ancora: metterla DENTRO il try interno dopo trader.step()

# Trova e correggi
for i, line in enumerate(lines):
    # Se è la riga del sleep dopo il loop exception
    if i == 956 and "time.sleep(120)" in line:
        # Aggiungi 4 spazi di indentazione
        lines[i] = "        " + line.strip() + "\n"
        print(f"✅ Riga {i+1} corretta: indentazione aumentata")

# Salva
with open("quantum_v33_ultimate_final.py", "w") as f:
    f.writelines(lines)

print("✅ Fix applicato!")
