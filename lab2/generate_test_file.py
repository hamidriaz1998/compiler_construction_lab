code = """int main() {
        int counter = 0;
        float result = 3.14159;

        while (counter < 1000000) {
            result = result + 0.001;
            counter = counter + 1;
        }

        return 0;
    }"""

for i in range(100000): 
    with open("test_program.txt", "a") as file:
        file.write(code)
