with open("main.py", "rb") as file:
    data = file.read()

for byte in data[:200]:   # first 200 bytes
    print(format(byte, "08b"))