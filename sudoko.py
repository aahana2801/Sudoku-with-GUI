import tkinter as tk  # Import Tkinter library for GUI
from tkinter import messagebox  # Import messagebox to show popups
from itertools import product  # Import product to iterate over row-column pairs

# ---------------- Sudoku Logic ----------------

def get_possible_numbers(grid):
    """Compute the possible numbers for each row, column, and 3x3 box."""
    all_numbers = set(range(1, 10))  # Set of all Sudoku numbers 1-9
    rows_possible = [all_numbers - set(row) for row in grid]  # Numbers not in each row
    cols_possible = [all_numbers - set(grid[i][j] for i in range(9)) for j in range(9)]  # Numbers not in each column
    boxes_possible = []  # List to store numbers not in each 3x3 box
    for br, bc in product(range(3), repeat=2):  # Loop through 3x3 boxes
        nums = set()  # Numbers already in this box
        for i, j in product(range(3), repeat=2):  # Loop through cells in box
            nums.add(grid[br*3 + i][bc*3 + j])  # Add number in box cell
        boxes_possible.append(all_numbers - nums)  # Possible numbers in this box
    return rows_possible, cols_possible, boxes_possible  # Return possibilities

def solve_sudoku(grid):
    """Solve Sudoku using backtracking with precomputed possibilities."""
    rows_possible, cols_possible, boxes_possible = get_possible_numbers(grid)  # Compute possibilities
    
    def backtrack():  # Inner recursive function
        for row, col in product(range(9), repeat=2):  # Loop through all cells
            if grid[row][col] == 0:  # If cell is empty
                box_index = (row // 3) * 3 + (col // 3)  # Find corresponding 3x3 box
                candidates = rows_possible[row] & cols_possible[col] & boxes_possible[box_index]  # Valid numbers for this cell
                if not candidates:  # If no valid numbers, backtrack
                    return False
                for num in candidates:  # Try each valid number
                    grid[row][col] = num  # Place number in cell
                    rows_possible[row].remove(num)  # Remove from row possibilities
                    cols_possible[col].remove(num)  # Remove from column possibilities
                    boxes_possible[box_index].remove(num)  # Remove from box possibilities
                    
                    if backtrack():  # Recursively try next cells
                        return True
                    
                    grid[row][col] = 0  # Backtrack: remove number
                    rows_possible[row].add(num)  # Add back to row possibilities
                    cols_possible[col].add(num)  # Add back to column possibilities
                    boxes_possible[box_index].add(num)  # Add back to box possibilities
                return False  # Return False if no candidates work
        return True  # Return True if all cells filled
    
    return backtrack()  # Start recursion

def is_valid_initial_sudoku(grid):
    """Check if the initial Sudoku has duplicates in rows, columns, or boxes."""
    for i in range(9):  # Check rows
        row_nums = [n for n in grid[i] if n != 0]  # Numbers in row excluding 0
        if len(row_nums) != len(set(row_nums)):  # If duplicates exist
            return False
    for j in range(9):  # Check columns
        col_nums = [grid[i][j] for i in range(9) if grid[i][j] != 0]  # Numbers in column
        if len(col_nums) != len(set(col_nums)):  # If duplicates exist
            return False
    for br, bc in product(range(3), repeat=2):  # Check 3x3 boxes
        nums = []
        for i, j in product(range(3), repeat=2):
            n = grid[br*3 + i][bc*3 + j]
            if n != 0:
                nums.append(n)  # Add number to list
        if len(nums) != len(set(nums)):  # If duplicates exist
            return False
    return True  # Sudoku is valid

# ---------------- GUI Functions ----------------

def get_grid_from_entries():
    """Read the numbers entered in the Tkinter grid and return as a 2D list."""
    grid = []
    for i in range(9):  # Loop through rows
        row = []
        for j in range(9):  # Loop through columns
            val = entries[i][j].get()  # Get value from Entry widget
            if val == "":
                row.append(0)  # Empty cell is 0
            else:
                try:
                    num = int(val)  # Convert to integer
                    if 1 <= num <= 9:  # Check valid number
                        row.append(num)
                    else:
                        messagebox.showerror("Invalid Input", "Enter numbers 1-9 only.")  # Error for invalid number
                        return None
                except ValueError:  # Non-integer input
                    messagebox.showerror("Invalid Input", "Enter numbers 1-9 only.")
                    return None
        grid.append(row)  # Add row to grid
    return grid  # Return full 9x9 grid

def fill_grid_to_entries(grid):
    """Fill the solved Sudoku grid back into the Tkinter Entry widgets."""
    for i in range(9):
        for j in range(9):
            entries[i][j].delete(0, tk.END)  # Clear existing value
            entries[i][j].insert(0, str(grid[i][j]))  # Insert solved number

def reset_grid():
    """Clear the grid and reset heading/button after solution."""
    for i in range(9):
        for j in range(9):
            entries[i][j].delete(0, tk.END)  # Clear each cell
    heading_label.grid()  # Show heading again
    solve_btn.config(text="Solve Sudoku", command=solve_button_click)  # Change button back to Solve

def solve_button_click():
    """Triggered when Solve button is clicked."""
    grid = get_grid_from_entries()  # Read grid from GUI
    if grid is None:
        return  # Invalid input
    if not is_valid_initial_sudoku(grid):  # Check if Sudoku is correct
        messagebox.showinfo("Sudoku", "Sudoku is incorrect")
        return
    if solve_sudoku(grid):  # Try to solve Sudoku
        fill_grid_to_entries(grid)  # Fill solution
        heading_label.grid_remove()  # Hide heading
        solve_btn.config(text="Reset", command=reset_grid)  # Change button to Reset
    else:
        messagebox.showinfo("Sudoku", "Sudoku is incorrect")  # No solution exists

# ---------------- GUI ----------------

root = tk.Tk()  # Create main window
root.title("Sudoku Solver")  # Set window title

heading_label = tk.Label(root, text="Enter a Sudoku", font=('Arial', 20))  # Heading label
heading_label.grid(row=0, column=0, columnspan=9, pady=10)  # Place heading

entries = []  # List to hold Entry widgets

# Create 9x9 Sudoku grid
for i in range(9):
    row_entries = []
    for j in range(9):
        # Set thicker borders for 3x3 subgrids
        top = 4 if i % 3 == 0 else 1
        left = 4 if j % 3 == 0 else 1
        bottom = 4 if i == 8 else 1
        right = 4 if j == 8 else 1

        e = tk.Entry(root, width=3, font=('Arial', 18), justify='center',
                     borderwidth=1, relief='solid')  # Create Entry widget
        e.grid(row=i+1, column=j, ipadx=5, ipady=5, padx=(left//2, right//2), pady=(top//2, bottom//2))  # Place Entry with padding
        row_entries.append(e)  # Add to row list
    entries.append(row_entries)  # Add row to entries list

solve_btn = tk.Button(root, text="Solve Sudoku", command=solve_button_click, font=('Arial', 14))  # Solve button
solve_btn.grid(row=10, column=0, columnspan=9, pady=10)  # Place button

root.mainloop()  # Start the GUI event loop


