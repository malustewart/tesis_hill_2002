def give_instruction(prompt : str):
    input(f"{prompt}\nPress enter when done...")

def ask_for_input(prompt : str):
    response = input(f"{prompt}")
    if response:
        return response
    for _ in range(5):
        print("Error: No input was received")
        response = input(f"{prompt}")
        if response:
            return response
    return None
