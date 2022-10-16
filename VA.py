import math
import time
import random
from colour import Color
import numpy as np

import tkinter as tk
from tkinter import colorchooser
from tkinter import messagebox

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#141414")
        self.master = master
        self.pack(side="right", fill="both", expand=False)
        self.canvas = tk.Canvas(bg="#141414", bd=-2)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.color = "darkred"
        self.canvas.bind("<Configure>", self._draw_gradient)
        
        self.maxBalls, self.maxSpeed = 1000, 10
        self.padx, self.pady = 0, 0
            
        def bttn(origin, text, bcolor, fcolor, cmd=None):
            def on_enter(e): mybutton['bg'], mybutton['fg'] = bcolor, fcolor
            def on_leave(e): mybutton['bg'], mybutton['fg'] = fcolor, bcolor
            mybutton = tk.Button(origin, width=35, height=2, text=text,fg=bcolor,bg=fcolor,border=0,activeforeground=fcolor,activebackground=bcolor,command=cmd)
            mybutton.bind("<Enter>", on_enter)
            mybutton.bind("<Leave>", on_leave)
            return mybutton
        
        # The inputs for n balls and speed
        self.antal = tk.Entry(self, bd=1)
        self.hastighet = tk.Entry(self, bd=1)
        
        # Buttons
        self.initiera = bttn(self, "I N I T I A T E", "#a0c4ff", "#141414", self.spawn_balls)
        self.starta = bttn(self, "S T A R T", "#caffbf", "#141414", self.run)
        self.pausa = bttn(self, "P A U S E", "#ffd6a5", "#141414", self.pause)
        self.rensa = bttn(self, "C L E A R", "#ffc6ff", "#141414", self.clear)
        self.avsluta = bttn(self, "E X I T", "#ffadad", "#141414", self.end)
        self.avsluta = bttn(self, "G R A V I T Y", "#fdffb6", "#141414", self.gravity)
        self.colorPicker = bttn(self, "S E L E C T   C O L O R", "white", "#141414", self.choose_color)
        
        # Formating widgets with for-loop
        self.widgets = self.winfo_children()
        for w in range(0, len(self.widgets)):
            self.widgets[w].grid(column=2, row=w, sticky="e", padx=self.padx, pady=self.pady)
        
        self.antal_t = tk.Label(self, text="A M O U N T", fg="#d4a373",bg="#141414",border=0)
        self.antal_t.grid(column=2, row=0, sticky="w", padx=10)
        
        self.hastighet_t = tk.Label(self, text="V E L O C I T Y",fg="#d4a373",bg="#141414",border=0)
        self.hastighet_t.grid(column=2, row=1, sticky="w", padx=10)
        
        self.gravitySwitch, self.running, self.balls, self.n_balls = False, False, [], 0
        
    def _draw_gradient(self, event=None):
        self.canvas.delete("gradient")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        limit = width
        (r1,g1,b1) = self.canvas.winfo_rgb(self.color)
        (r2,g2,b2) = self.canvas.winfo_rgb("#141414")
        r_ratio = float(r2-r1) / limit
        g_ratio = float(g2-g1) / limit
        b_ratio = float(b2-b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%4.4x%4.4x%4.4x" % (nr,ng,nb)
            self.canvas.create_line(i,0,i,height, tags=("gradient",), fill=color)
        self.canvas.lower("gradient")  
    
    def choose_color(self):
        self.color = tk.colorchooser.askcolor(title = "Choose color")[1] # we choose the hex value
        self.clear()
        self.spawn_balls()
        return self.color
    
    def clear(self):
        self.canvas.delete("all")
        self._draw_gradient()
        self.balls = []
        
    def run(self):
        self.running = True
        
    def pause(self):
        self.running = False
    
    def end(self):
        self.master.destroy()
        
    def gravity(self):
        if self.gravitySwitch:
            self.gravitySwitch = False
        else:
            self.gravitySwitch = True
        
    def spawn_balls(self):
        try:
            self.n_balls = int(self.antal.get())
            if self.n_balls > self.maxBalls:
                tk.messagebox.showinfo("Warning", f"{self.n_balls} is too many balls, setting the max balls to {self.maxBalls}")
                self.n_balls = self.maxBalls
        except ValueError:
            self.n_balls = 0
            
        try:
            speed = float(self.hastighet.get())
            if speed > self.maxSpeed:
                tk.messagebox.showinfo("Warning", f"{speed} is too high, setting the speed to {self.maxSpeed}")
                speed = self.maxSpeed   
        except ValueError: speed = 0
        
        self.clear()
        
        while len(self.balls) < self.n_balls:
            ball_size = random.randint(20, 40)
            xLocation = random.randint(0+ball_size, self.canvas.winfo_width()-ball_size)
            yLocation = random.randint(0+ball_size, self.canvas.winfo_height()-ball_size)
            j, n = 0, 0
            while j < len(self.balls):
                d = dist(xLocation, self.balls[j].center[0], yLocation, self.balls[j].center[1])
                if d <= (ball_size + self.balls[j].r + 4): # 4 pixel offset
                    xLocation = random.randint(0+ball_size, self.canvas.winfo_width()-ball_size)
                    yLocation = random.randint(0+ball_size, self.canvas.winfo_height()-ball_size)
                    j = 0
                    n += 1
                else:
                    j += 1
                if n >= 80000:
                    break
            if n >= 80000:
                tk.messagebox.showinfo("Warning", f"too cramped, only added {len(self.balls)} balls")
                break        
            new_ball = Ball(self, xLocation-ball_size, yLocation-ball_size, ball_size, speed)
            self.balls.append(new_ball)
        
         
class Ball:
    def __init__(self, app, x, y, d, userSpeed):
        self.myapp = app
        self.canvas = self.myapp.canvas
        self.x, self.y, self.d, self.r = x, y, d, d/2
        self.phi = 2 * math.pi * random.random()
        self.collideFactor = 0.95
        self.vx, self.vy = np.random.random() * math.cos(self.phi) * userSpeed, np.random.random() * math.sin(self.phi) * userSpeed
        self.originalvy = self.vy
        self.color = random.choice(list(Color("black").range_to(Color(self.myapp.color), self.myapp.n_balls)))
        self.maxSpeed = 5
        self.ball = self.canvas.create_oval(self.x, self.y, self.x + self.d, self.y + self.d, fill=self.color)
        
        self.pos = [self.x, self.y, self.x + self.d, self.y + self.d]
        self.center = [self.x + self.r, self.y + self.r]
    
    def collide(self):
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        if self.pos[0] < 0:
            self.x = 0
            self.vx = -self.vx * self.collideFactor
            
        if self.pos[2] >= width:
            self.x = width - self.d
            self.vx = -self.vx * self.collideFactor
            
        if self.pos[1] < 0:
            self.y = 0
            self.vy = -self.vy * self.collideFactor
            
        if self.pos[3] >= height:
            self.y = height - self.d
            self.vy = -self.vy * self.collideFactor
        
    def step(self):
        if self.myapp.gravitySwitch: self.vy += 0.0982
        
        if self.vx > self.maxSpeed:
            self.vx = self.maxSpeed
            
        if self.vy > self.maxSpeed:
            self.vy = self.maxSpeed
            
        self.collide()    
        self.x += self.vx
        self.y += self.vy
        
        self.canvas.coords(self.ball, self.x, self.y, self.x+self.d, self.y+self.d)
        
        self.pos = self.canvas.coords(self.ball)
        self.center = [self.x+self.r, self.y+self.r]
        
    def circlecollide(self, ball2):
        if self.pos[0] < ball2.pos[0] + ball2.vx < self.pos[2] or self.pos[0] < ball2.pos[2] + ball2.vx < self.pos[2]:
            
            r1, r2 = self.r, ball2.r
            p1, p2 = self.center, ball2.center
            d = dist(p1[0], p2[0], p1[1], p2[1])
              
            if d < r1 + r2:
                nx, ny = (p2[0] - p1[0]) / d, (p2[1] - p1[1]) / d
                p = 2*(self.vx * nx + self.vy * ny - ball2.vx * nx - ball2.vy * ny) / (r1+r2)
                
                midpointx = (p1[0] + p2[0]) / 2
                midpointy = (p1[1] + p2[1]) / 2
                
                newx1 = midpointx + r1 * (p1[0] - p2[0]) / d
                newy1 = midpointy + r1 * (p1[1] - p2[1]) / d
                newx2 = midpointx + r2 * (p2[0] - p1[0]) / d
                newy2 = midpointy + r2 * (p2[1] - p1[1]) / d
                
                
                self.x = newx1 - self.r
                self.y = newy1 - self.r
                ball2.x = newx2 - ball2.r
                ball2.y = newy2 - ball2.r
                
                self.collide()
                ball2.collide()
                
                self.vx += - p * r1 * nx * self.collideFactor
                self.vy += - p * r1 * ny * self.collideFactor
                ball2.vx +=  p * r2 * nx * self.collideFactor
                ball2.vy +=  p * r2 * ny * self.collideFactor
                
def dist(x1, x2, y1, y2):
    return ((x1 - x2)**2 + (y1 - y2)**2)**(1/2)
  
def main():
    root = tk.Tk()
    root.title("Ball Simulator 2022")
    root.geometry("800x800")
    myapp = App(root)
    
    while True:
        if myapp.running:
            for i in range(0, len(myapp.balls)):
                for j in range(i+1, len(myapp.balls)):
                    # If the balls are in the same domain, we check for collision
                    myapp.balls[i].circlecollide(myapp.balls[j]) 
                myapp.balls[i].step()
        myapp.update()
        time.sleep(0.01)
        
if __name__ == "__main__":
    main()