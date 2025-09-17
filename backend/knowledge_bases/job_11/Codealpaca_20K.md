# Codealpaca 20K

**Description:** Dataset loaded from Hugging Face: sahil2801/CodeAlpaca-20k

**Type:** Text

**Samples:** 20022

## Training Examples

### Example 1
**Instruction:** Create an array of length 5 which contains all even numbers between 1 and 10.

**Output:** arr = [2, 4, 6, 8, 10]

---

### Example 2
**Instruction:** Formulate an equation to calculate the height of a triangle given the angle, side lengths and opposite side length.

**Output:** Height of triangle = opposite side length * sin (angle) / side length

---

### Example 3
**Instruction:** Write a replace method for a string class which replaces the given string with a given set of characters.

**Output:** def replace(self, replace_with):
    new_string = ""
    for char in self:
        if char == " ":
            new_string += replace_with
        else:
            new_string += char
    return new_string

---

### Example 4
**Instruction:** Create an array of length 15 containing numbers divisible by 3 up to 45.

**Output:** arr = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45]

---

### Example 5
**Instruction:** Write a function to find the number of distinct states in a given matrix.

**Output:** def find_num_distinct_states(matrix):
    states = set()
    for row in matrix:
        state = "".join([str(x) for x in row])
        states.add(state)
    return len(states)

---

### Example 6
**Instruction:** Create a nested loop to print every combination of numbers between 0-9

**Output:** for i in range(10):
    for j in range(10):
        print(i, j)

---

### Example 7
**Instruction:** Write a function to find the maximum difference between two numbers in a given array.

**Output:** def max_difference(arr):
    max_diff = 0
    for i in range(len(arr)-1):
        diff = arr[i+1] - arr[i]
        if diff > max_diff:
            max_diff = diff
    return max_diff

---

### Example 8
**Instruction:** Write a function to generate the nth Fibonacci number.

**Output:** def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-2) + fib(n-1)

---

### Example 9
**Instruction:** Write a class to represent a 2D point with x and y coordinates.

**Output:** class Point:
    def __init__(self, x, y):
        self.x = x 
        self.y = y 
   
    def __str__(self): 
        return "({0},{1})".format(self.x, self.y)

---

### Example 10
**Instruction:** Write code that removes spaces from a given string.

**Output:** def remove_spaces(string): 
    return "".join(string.split())

---

