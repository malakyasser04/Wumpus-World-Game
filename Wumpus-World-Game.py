#!/usr/bin/env python
# coding: utf-8

# In[1]:


import random
import tkinter as tk
from tkinter import messagebox

class WumpusWorld:
    def __init__(self, size=4):
        self.size = size
        self.agent_location = (0, 0)
        self.wumpus_location = self.generate_random_location(exclude=[self.agent_location])
        self.pit_locations = [self.generate_random_location(exclude=[self.agent_location, self.wumpus_location]) for _ in range(3)]
        self.gold_location = self.generate_random_location(exclude=[self.agent_location, self.wumpus_location] + self.pit_locations)
        self.arrows = 1
        self.has_gold = False
        self.is_alive = True
        self.score = 0
        self.action_count = 0

    def generate_random_location(self, exclude=None):
        while True:
            location = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
            if exclude is None or location not in exclude:
                return location

    def get_adjacent_locations(self, location):
        x, y = location
        adjacent_locations = []
        if x > 0:
            adjacent_locations.append((x - 1, y))
        if x < self.size - 1:
            adjacent_locations.append((x + 1, y)) 
        if y > 0:
            adjacent_locations.append((x, y - 1))
        if y < self.size - 1:
            adjacent_locations.append((x, y + 1)) 
        return adjacent_locations

    def move(self, direction):
        if not self.is_alive:
            messagebox.showinfo("Game Over", "You are dead. Game over!")
            return

        x, y = self.agent_location
        if direction == "left" and y > 0:
            y -= 1
        elif direction == "right" and y < self.size - 1:
            y += 1
        elif direction == "up" and x > 0:
            x -= 1
        elif direction == "down" and x < self.size - 1:
            x += 1
        else:
            messagebox.showinfo("Invalid Move", "Invalid move!")
            return

        self.agent_location = (x, y)
        self.score -= 1  
        self.action_count += 1  
        self.check_encounter()
        

    def shoot_arrow(self, row, col):
        if not self.is_alive:
            messagebox.showinfo("Game Over", "You are dead. Game over!")
            return

        if self.arrows > 0:
            self.arrows -= 1
            if (row, col) == self.wumpus_location:
                self.wumpus_location = None
                messagebox.showinfo("Shot Successful", "You shot the Wumpus!")
                self.score += 50 
                if self.wumpus_location is None:
                    self.check_encounter() 
            else:
                messagebox.showinfo("Missed Shot", "You missed the Wumpus!")
                self.score -= 10  
        else:
            messagebox.showinfo("Out of Arrows", "You don't have any arrows left!")

    def check_encounter(self):
        if self.agent_location == self.wumpus_location:
            messagebox.showinfo("Game Over", "You have been eaten by the Wumpus! Game over!")
            self.is_alive = False
            self.score -= 1000
        elif self.agent_location in self.pit_locations:
            messagebox.showinfo("Game Over", "You fell into a pit! Game over!")
            self.is_alive = False
            self.score -= 1000
        else:
            if self.agent_location == self.gold_location and not self.has_gold:
                messagebox.showinfo("Found Gold", "You found the gold! Now head back to the starting point to win!")
                self.has_gold = True
                self.score += 1000  
            if self.agent_location == (0, 0) and self.has_gold:
                messagebox.showinfo("Game Over", "You escaped with the gold! Congratulations, you won the game!")
                self.is_alive = False
                self.score += 1000  
        if not self.is_alive:
            self.score -= self.action_count  
            self.score -= 10 * (1 - self.arrows)
    def get_perceptions(self):
        perceptions = []
        x, y = self.agent_location
        adjacent_locations = self.get_adjacent_locations((x, y))

        if self.wumpus_location in adjacent_locations:
            perceptions.append("Stench")
        if any(pit_location in adjacent_locations for pit_location in self.pit_locations):
            perceptions.append("Breeze")

        return perceptions            

class WumpusGameGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wumpus World")
        self.geometry("400x400")

        self.world = WumpusWorld()
        self.create_grid()
        self.create_buttons()
        self.create_score_label()
        self.create_perceptions_label() 
        self.update_perceptions_label()  

    def create_grid(self):
        self.buttons = []
        for row in range(self.world.size):
            button_row = []
            for col in range(self.world.size):
                button = tk.Button(self, text=" ", width=3, height=1,
                                   command=lambda r=row, c=col: self.handle_click(r, c))
                button.grid(row=row, column=col, padx=2, pady=2)
                button_row.append(button)
            self.buttons.append(button_row)
    
    def update_grid(self):
        for row in range(self.world.size):
            for col in range(self.world.size):
                if (row, col) == self.world.agent_location:
                    if self.world.has_gold:
                        self.buttons[row][col].config(text="A (G)", bg="lightgreen")  # Update the button text to indicate the player has the gold
                    else:
                        self.buttons[row][col].config(text="A", bg="lightblue")
                
                else:
                    self.buttons[row][col].config(text=" ", bg="white")
                    
       
        self.update_score_label()
        
    def create_perceptions_label(self):
        self.perceptions_label = tk.Label(self, text="", font=("Arial", 12), justify="left", anchor="w")
        self.perceptions_label.grid(row=self.world.size + 1, columnspan=self.world.size, padx=10, sticky="w")
    
    def update_perceptions_label(self):
        perceptions = self.world.get_perceptions()
        if perceptions:
            self.perceptions_label.config(text=" " + ", ".join(perceptions))
        else:
            self.perceptions_label.config(text=" None")    

    def create_buttons(self):
        self.move_buttons_frame = tk.Frame(self)
        self.move_buttons_frame.grid(row=self.world.size, columnspan=self.world.size)

        directions = ["up", "down", "left", "right"]
        for idx, direction in enumerate(directions):
            button = tk.Button(self.move_buttons_frame, text=direction.capitalize(), command=lambda d=direction: self.handle_move(d))
            button.grid(row=0, column=idx)

        self.shoot_button = tk.Button(self.move_buttons_frame, text="Shoot", command=self.handle_shoot)
        self.shoot_button.grid(row=1, column=0, columnspan=len(directions))
    def create_score_label(self):
        self.score_label = tk.Label(self, text="Score: 0", font=("Arial", 16))  # Create a label for the score
        self.score_label.grid(row=self.world.size + 2, columnspan=self.world.size, pady=10)  # Adjust the row and padding

    def update_score_label(self):
        self.score_label.config(text=f"Score: {self.world.score}")    

    def handle_click(self, row, col):
        if self.world.is_alive:
            if (row, col) == self.world.agent_location:
                messagebox.showinfo("Invalid Move", "You are already in this room!")
            elif (abs(row - self.world.agent_location[0]) == 1 and col == self.world.agent_location[1]) \
                    or (abs(col - self.world.agent_location[1]) == 1 and row == self.world.agent_location[0]):
                direction = "down" if row > self.world.agent_location[0] else "up" \
                    if row < self.world.agent_location[0] else "right" if col > self.world.agent_location[1] else "left"

                if direction:
                    if direction in ["up", "down", "left", "right"]:
                        self.world.move(direction)
                        self.update_grid()
                        self.update_perceptions_label()
                        self.update_score_label()
            else:
                messagebox.showinfo("Invalid Move", "You can only move to adjacent rooms!")

    def handle_move(self, direction):
        if self.world.is_alive:
            self.world.move(direction)
            self.update_grid()
            self.update_perceptions_label()
            self.update_score_label()

    def handle_shoot(self):
        if self.world.is_alive:
            
            target_window = tk.Toplevel(self)
            target_window.title("Select Target")
            target_window.geometry("200x200")
            self.update_perceptions_label()
            self.update_score_label()

            
            for row in range(self.world.size):
                for col in range(self.world.size):
                    button = tk.Button(target_window, text=f"{row},{col}", width=3, height=1,
                                       command=lambda r=row, c=col: self.handle_target_click(r, c))
                    button.grid(row=row, column=col, padx=2, pady=2)

    def handle_target_click(self, row, col):
        
        if (row, col) in self.world.get_adjacent_locations(self.world.agent_location):
            self.world.shoot_arrow(row, col)
            self.update_grid()
            self.update_score_label()
        else:
            messagebox.showinfo("Invalid Target", "You can only shoot at adjacent rooms!")

if __name__ == "__main__":
    game_gui = WumpusGameGUI()
    game_gui.update_grid()
    game_gui.update_score_label()
    game_gui.update_perceptions_label()
    game_gui.mainloop()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




