from werkzeug.security import generate_password_hash

print("OFFICER:")
print(generate_password_hash("Officer@123"))

print("\nCOUNSELLOR:")
print(generate_password_hash("Counsellor@123"))

print("\nVICTIM:")
print(generate_password_hash("Victim@123"))