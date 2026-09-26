from werkzeug.security import generate_password_hash

passwords = [
    "Victim@22026",
    "Victim@32026",
    "Victim@42026",
    "Victim@52026",
    "Victim@62026"
]

for password in passwords:
    print(password)
    print(generate_password_hash(password))
    print()