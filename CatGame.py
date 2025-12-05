import tkinter as tk
from tkinter import PhotoImage
import random

import os
import sys


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def rgb(r, g, b): return f"#{r:02x}{g:02x}{b:02x}"


WIN_W, WIN_H = 1280, 720
GROUND_Y = 643
CAT_STEP = 8
BULLET_VY = -8
START_ROCK_VY = 3
MAX_ROCK_VY = 12
SPEED_UP_RATE = 0.005
TICK_MS = 16
MAX_BULLETS = 90
CAT_LIMIT_L, CAT_LIMIT_R = 60, WIN_W - 60


class GameApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("The Cat Game")
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.resizable(False, False)


        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_c = int((screen_width - WIN_W) / 2)
        y_c = int((screen_height - WIN_H) / 2)
        self.root.geometry(f"{WIN_W}x{WIN_H}+{x_c}+{y_c}")

        # icon
        try:
            icon_path = resource_path(os.path.join("textures", "Icon.ico"))
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon error: {e}")

        # textures load
        try:
            self.img_menu = PhotoImage(file=resource_path(os.path.join("textures", "Menu2.png")))
            self.img_bg = PhotoImage(file=resource_path(os.path.join("textures", "fonG.png")))
            self.img_cat = PhotoImage(file=resource_path(os.path.join("textures", "kotik.png"))).subsample(3, 3)
            self.img_bullet = PhotoImage(file=resource_path(os.path.join("textures", "Heart.png")))
            self.img_rock = PhotoImage(file=resource_path(os.path.join("textures", "stone.png"))).subsample(2, 2)

            # Explosion animation
            self.anim_expl = []
            for i in range(1, 12):
                path = resource_path(os.path.join("textures", f"exp{i}.png"))
                img = PhotoImage(file=path)
                self.anim_expl.append(img)
        except Exception as e:
            print(f"Error loading images: {e}")
            return

        self.bullets = []
        self.rocks = []
        self.keys = set()

        # statistic
        self.hCount = 0
        self.rock_score = 0

        self.hCount_var = tk.StringVar(value="Hearts: 0")
        self.score_var = tk.StringVar(value="Score: 0")

        self.cat_x = WIN_W // 2
        self.running = False
        self.current_rock_speed = START_ROCK_VY

        self.show_main_menu()
        self.root.mainloop()


    # in menu
    def show_main_menu(self):
        self.bg_label = tk.Label(self.root, image=self.img_menu, border=0)
        self.bg_label.place(x=0, y=0)

        self.btn_start = tk.Button(self.root, text='Start', bg=rgb(131, 94, 156), command=self.start_game)
        self.btn_start.place(height=100, width=300, y=280, x=490)

        self.btn_exit = tk.Button(self.root, text='Exit', bg=rgb(54, 3, 102), command=self.root.destroy)
        self.btn_exit.place(height=50, width=200, y=399, x=540)

    # in game
    def start_game(self):
        if hasattr(self, 'btn_start'): self.btn_start.destroy()
        if hasattr(self, 'btn_exit'): self.btn_exit.destroy()
        if hasattr(self, 'bg_label'): self.bg_label.destroy()

        self.canvas = tk.Canvas(self.root, width=WIN_W, height=WIN_H, bd=0, highlightthickness=0, bg=rgb(85, 107, 47))
        self.canvas.pack(anchor='w', side=tk.BOTTOM)
        self.canvas.create_image(WIN_W // 2 + 1, WIN_H // 2 - 1, image=self.img_bg)

        self.cat_x = WIN_W // 2
        self.cat_id = self.canvas.create_image(self.cat_x, GROUND_Y, image=self.img_cat)

        # statistic
        self.hCount = 0
        self.rock_score = 0

        self.hCount_var.set("Hearts: 0")
        self.score_var.set("Score: 0")

        # lable hearts
        self.label_counter = tk.Label(self.root, textvariable=self.hCount_var, bg=rgb(147, 3, 90), fg="white")
        self.label_counter.place(x=WIN_W - 100, y=35)

        # lable score
        self.label_score = tk.Label(self.root, textvariable=self.score_var, bg=rgb(147, 3, 90), fg="white", font=("Arial", 12, "bold"))
        self.label_score.place(x=WIN_W - 100, y=5)
        self.btn_back = tk.Button(self.root, text='Back', bg=rgb(147, 3, 90), height=2, width=10, command=self.back_to_main_menu)
        self.btn_back.place(x=3, y=3)

        self.root.bind("<KeyPress>", self.on_key_down)
        self.root.bind("<KeyRelease>", self.on_key_up)

        self.current_rock_speed = START_ROCK_VY
        self.running = True
        self.game_loop()

    def back_to_main_menu(self):
        self.running = False
        self.root.unbind("<KeyPress>")
        self.root.unbind("<KeyRelease>")
        if hasattr(self, "canvas"): self.canvas.destroy()
        if hasattr(self, "btn_back"): self.btn_back.destroy()

        # Statistic lables remove
        if hasattr(self, "label_counter"): self.label_counter.destroy()
        if hasattr(self, "label_score"): self.label_score.destroy()

        # Game Over elements remove
        if hasattr(self, "label_go"): self.label_go.destroy()
        if hasattr(self, "label_go_score"): self.label_go_score.destroy()
        if hasattr(self, "btn_go_back"): self.btn_go_back.destroy()

        self.bullets.clear()
        self.keys.clear()
        self.rocks.clear()
        self.show_main_menu()

    #GAME OVER SCREEN
    def game_over(self):
        self.running = False
        self.root.unbind("<KeyPress>")
        self.root.unbind("<KeyRelease>")

        self.label_go = tk.Label(self.root, text="GAME OVER", font=("Arial", 40, "bold"), fg="black", bg=rgb(147, 3, 90))
        self.label_go.place(relx=0.5, rely=0.4, anchor="center")

        # rock_score
        self.label_go_score = tk.Label(self.root, text=f"Final Score: {self.rock_score}", font=("Arial", 20),
                                       fg="black",
                                       bg=rgb(147, 3, 90))
        self.label_go_score.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_go_back = tk.Button(self.root, text="Back to Main Menu", font=("Arial", 15), bg=rgb(147, 3, 90),
                                     fg="black", command=self.back_to_main_menu)
        self.btn_go_back.place(relx=0.5, rely=0.6, anchor="center")

    # input
    def on_key_down(self, e):
        k = e.keysym
        if k == "Escape": return self.back_to_main_menu()
        self.keys.add(k)
        if k == "space": self.shoot()

    def on_key_up(self, e):
        self.keys.discard(e.keysym)

    # logic
    def shoot(self):
        bid = self.canvas.create_image(self.cat_x + 20, GROUND_Y - 80, image=self.img_bullet)
        self.bullets.append(bid)
        self.hCount += 1
        self.hCount_var.set(f"Hearts: {self.hCount}")
        if len(self.bullets) > MAX_BULLETS:
            self.canvas.delete(self.bullets.pop(0))

    def spawn_rock(self):
        chance = 2 + int(self.current_rock_speed / 4)
        if random.randint(1, 100) <= chance:
            x_pos = random.randint(50, WIN_W - 50)
            rid = self.canvas.create_image(x_pos, -50, image=self.img_rock)
            self.rocks.append(rid)

    def explode(self, x, y):
        if not self.anim_expl: return
        exp_id = self.canvas.create_image(x, y, image=self.anim_expl[0])
        self.animate_explosion(exp_id, 0)

    def animate_explosion(self, exp_id, frame_idx):
        frame_idx += 1
        if frame_idx < len(self.anim_expl):
            self.canvas.itemconfig(exp_id, image=self.anim_expl[frame_idx])
            self.root.after(40, lambda: self.animate_explosion(exp_id, frame_idx))
        else:
            self.canvas.delete(exp_id)

    # COLLISIONS
    def check_collisions(self):
        cat_hit = False

        for rock_id in list(self.rocks):
            rx, ry = self.canvas.coords(rock_id)

            # cat hit?
            if abs(rx - self.cat_x) < 120 and abs(ry - GROUND_Y) < 120:
                self.explode(rx, ry)
                cat_hit = True
                break

            # Stone hit?
            if ry > (GROUND_Y - 80):
                continue

            hit = False
            for bull_id in self.bullets:
                bx, by = self.canvas.coords(bull_id)
                if abs(rx - bx) < 70 and abs(ry - by) < 70:
                    hit = True
                    break

            if hit:
                self.explode(rx, ry)
                self.canvas.delete(rock_id)
                if rock_id in self.rocks: self.rocks.remove(rock_id)

                # Score update
                self.rock_score += 1
                self.score_var.set(f"Score: {self.rock_score}")

        if cat_hit:
            self.game_over()

    def game_loop(self):
        if not self.running: return

        if self.current_rock_speed < MAX_ROCK_VY:
            self.current_rock_speed += SPEED_UP_RATE

        # Cat movement
        dx = (-CAT_STEP if "Left" in self.keys else 0) + (CAT_STEP if "Right" in self.keys else 0)
        if dx:
            self.cat_x = max(CAT_LIMIT_L, min(CAT_LIMIT_R, self.cat_x + dx))
            self.canvas.coords(self.cat_id, self.cat_x, GROUND_Y)

        # Spawn Logic
        self.spawn_rock()

        # Bullet movement
        for bid in list(self.bullets):
            self.canvas.move(bid, 0, BULLET_VY)
            _, y = self.canvas.coords(bid)
            if y < -50:
                self.canvas.delete(bid)
                self.bullets.remove(bid)

        # Stone movement
        for rid in list(self.rocks):
            self.canvas.move(rid, 0, self.current_rock_speed)
            _, y = self.canvas.coords(rid)
            if y > WIN_H + 50:
                self.canvas.delete(rid)
                self.rocks.remove(rid)

        # Check Collisions
        self.check_collisions()

        self.root.after(TICK_MS, self.game_loop)


if __name__ == "__main__":
    GameApp()