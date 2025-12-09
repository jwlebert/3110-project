def calculate_sum(a, b):
    # Bug: should be addition, not subtraction
    return a - b

def main():
    result = calculate_sum(5, 3)
    print(f"Sum: {result}")

if __name__ == "__main__":
    main()
