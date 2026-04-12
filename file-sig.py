def generate_file_adapter_signature(columns, file_type):
    sig = ""
    for c in columns:
        sig += c
    sig +=file_type
    return sig

print(generate_file_adapter_signature(["the_date", "the_place", "yay_oh"], "pdf"))

