with open('quantum_trader_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova e sostituisci la sezione signal
old_code = '''            # Signal
            signal = "HOLD"
            if confluence >= 1.5:
                if tech_score > 0.15 and macro_score > -0.1:
                    signal = "BUY"
                elif tech_score < -0.15 and macro_score < 0.1:
                    signal = "SELL"'''

new_code = '''            # Signal
            signal = "HOLD"
            print(f"🔍 TF {timeframe}: conf={confluence:.2f}, tech={tech_score:.2f}, macro={macro_score:.2f}")
            if confluence >= 1.5:
                print(f"✅ Confluence >= 1.5! Checking scores...")
                if tech_score > 0.15 and macro_score > -0.1:
                    signal = "BUY"
                    print(f"🟢 BUY: tech={tech_score:.2f} > 0.15, macro={macro_score:.2f} > -0.1")
                elif tech_score < -0.15 and macro_score < 0.1:
                    signal = "SELL"
                    print(f"🔴 SELL: tech={tech_score:.2f} < -0.15, macro={macro_score:.2f} < 0.1")
                else:
                    print(f"⚪ HOLD: scores non soddisfano condizioni")
            else:
                print(f"❌ Confluence {confluence:.2f} < 1.5")'''

content = content.replace(old_code, new_code)

with open('quantum_trader_ultimate_final.py', 'w') as f:
    f.write(content)

print("✅ Debug aggiunto!")
