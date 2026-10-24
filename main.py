"""
Snek Volt - Electromagnetic Circuit Snake written in Python & Pygame.

Custom Gameplay Mechanics:
1. Polarity Reversal (SPACE): Toggle between Positive (+, Cyan) and Negative (-, Amber)
   charge. Opposite-polarity Capacitor Orbs attract toward the head within 3 tiles.
2. Overclock Dash (LEFT SHIFT): Consume stored charge to sprint at 2x speed and
   lay down conductive copper traces across dead zones.
3. Phase Relay Portals: Paired circuit vias that teleport the snake across the board
   while preserving velocity and polarity.
4. EMP Surge Pulses: Expanding ring hazards emitted by overloaded inductors; absorb
   them with matching polarity for bonus score or dodge them to avoid tail loss.
"""

import math
import os
import random
import sys
import pygame

GRID_W, GRID_H = 32, 22
CELL = 28
HUD_H = 68
WIDTH = GRID_W * CELL
HEIGHT = GRID_H * CELL + HUD_H
FPS = 60

BG_DARK = (10, 14, 22)
GRID_LINE = (20, 28, 44)
POS_COLOR = (56, 189, 248)   # Positive (+) Cyan
NEG_COLOR = (251, 191, 36)   # Negative (-) Amber
PORTAL_A = (168, 85, 247)
PORTAL_B = (236, 72, 153)
EMP_COLOR = (239, 68, 68)
TRACE_COLOR = (16, 185, 129)


def load_or_build_sprite(name, color, size=CELL):
    path = os.path.join(os.path.dirname(__file__), "assets", name)
    if os.path.exists(path):
        try:
            return pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), (size, size))
        except Exception:
            pass
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (size // 2, size // 2), size // 2 - 2)
    pygame.draw.circle(surf, (255, 255, 255), (size // 2, size // 2), size // 4)
    return surf


class SnekVoltGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snek Volt - Electromagnetic Circuit Snake")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("menlo,consolas,monospace", 18, bold=True)
        self.big_font = pygame.font.SysFont("menlo,consolas,monospace", 34, bold=True)
        self.reset()

    def reset(self):
        cx, cy = GRID_W // 2, GRID_H // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy), (cx - 3, cy)]
        self.direction = (1, 0)
        self.next_dir = (1, 0)
        self.polarity = 1  # +1 = Positive (Cyan), -1 = Negative (Amber)
        self.score = 0
        self.charge = 60.0
        self.overclock = False
        self.game_over = False
        self.tick_accum = 0.0
        self.traces = set()
        self.portals = [(5, 5), (GRID_W - 6, GRID_H - 6)]
        self.orbs = []
        self.emp_rings = []
        for _ in range(4):
            self.spawn_orb()

    def spawn_orb(self):
        occupied = set(self.snake) | set(self.portals) | {(o["x"], o["y"]) for o in self.orbs}
        while True:
            x = random.randint(1, GRID_W - 2)
            y = random.randint(1, GRID_H - 2)
            if (x, y) not in occupied:
                self.orbs.append({
                    "x": x,
                    "y": y,
                    "polarity": random.choice([1, -1]),
                    "value": random.choice([10, 15, 25]),
                })
                break

    def spawn_emp(self):
        x = random.randint(4, GRID_W - 5)
        y = random.randint(4, GRID_H - 5)
        self.emp_rings.append({
            "x": x,
            "y": y,
            "radius": 0.4,
            "max_r": 4.8,
            "polarity": random.choice([1, -1]),
        })

    def apply_magnetic_pull(self):
        hx, hy = self.snake[0]
        for orb in self.orbs:
            dx = hx - orb["x"]
            dy = hy - orb["y"]
            dist = abs(dx) + abs(dy)
            # Opposite polarity attracts within Manhattan distance 3
            if dist <= 3 and dist > 0 and orb["polarity"] != self.polarity:
                step_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
                step_y = 1 if dy > 0 else (-1 if dy < 0 else 0)
                orb["x"] = max(0, min(GRID_W - 1, orb["x"] + step_x))
                orb["y"] = max(0, min(GRID_H - 1, orb["y"] + step_y))

    def step_grid(self):
        if self.game_over:
            return
        self.direction = self.next_dir
        hx, hy = self.snake[0]
        nx = (hx + self.direction[0]) % GRID_W
        ny = (hy + self.direction[1]) % GRID_H

        # Phase Relay Portal teleportation
        if (nx, ny) == self.portals[0]:
            nx, ny = self.portals[1][0] + self.direction[0], self.portals[1][1] + self.direction[1]
            self.score += 5
        elif (nx, ny) == self.portals[1]:
            nx, ny = self.portals[0][0] + self.direction[0], self.portals[0][1] + self.direction[1]
            self.score += 5

        nx %= GRID_W
        ny %= GRID_H

        if (nx, ny) in self.snake[:-1]:
            self.game_over = True
            return

        self.snake.insert(0, (nx, ny))
        if self.overclock and self.charge > 0:
            self.traces.add((hx, hy))

        self.apply_magnetic_pull()

        ate = False
        for orb in list(self.orbs):
            if (orb["x"], orb["y"]) == (nx, ny):
                ate = True
                mult = 2 if orb["polarity"] != self.polarity else 1
                self.score += orb["value"] * mult
                self.charge = min(100.0, self.charge + 22.0)
                self.orbs.remove(orb)
                self.spawn_orb()
                if random.random() < 0.45:
                    self.spawn_emp()
                break

        if not ate:
            self.snake.pop()

    def update(self, dt):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()
        self.overclock = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.charge > 2.0
        if self.overclock:
            self.charge = max(0.0, self.charge - 26.0 * dt)
        else:
            self.charge = min(100.0, self.charge + 4.5 * dt)

        speed = 15.0 if self.overclock else 8.5
        self.tick_accum += dt * speed
        while self.tick_accum >= 1.0:
            self.tick_accum -= 1.0
            self.step_grid()

        hx, hy = self.snake[0]
        for ring in list(self.emp_rings):
            ring["radius"] += dt * 3.4
            dist = math.hypot(hx - ring["x"], hy - ring["y"])
            if abs(dist - ring["radius"]) < 0.55:
                if ring["polarity"] == self.polarity:
                    self.score += 20
                    self.charge = min(100.0, self.charge + 15.0)
                    self.emp_rings.remove(ring)
                    continue
                else:
                    if len(self.snake) > 3:
                        self.snake.pop()
                    else:
                        self.game_over = True
                    self.emp_rings.remove(ring)
                    continue
            if ring["radius"] >= ring["max_r"]:
                self.emp_rings.remove(ring)

    def draw(self):
        self.screen.fill(BG_DARK)
        # Draw circuit grid
        for x in range(GRID_W):
            for y in range(GRID_H):
                rect = pygame.Rect(x * CELL, HUD_H + y * CELL, CELL, CELL)
                pygame.draw.rect(self.screen, GRID_LINE, rect, 1)

        # Draw conductive overclock traces
        for tx, ty in self.traces:
            r = pygame.Rect(tx * CELL + 6, HUD_H + ty * CELL + 6, CELL - 12, CELL - 12)
            pygame.draw.rect(self.screen, TRACE_COLOR, r, border_radius=4)

        # Draw Phase Relay Portals
        for idx, (px, py) in enumerate(self.portals):
            col = PORTAL_A if idx == 0 else PORTAL_B
            center = (px * CELL + CELL // 2, HUD_H + py * CELL + CELL // 2)
            pygame.draw.circle(self.screen, col, center, CELL // 2 - 1, 3)
            pygame.draw.circle(self.screen, (255, 255, 255), center, 5)

        # Draw Capacitor Orbs
        for orb in self.orbs:
            col = POS_COLOR if orb["polarity"] > 0 else NEG_COLOR
            center = (orb["x"] * CELL + CELL // 2, HUD_H + orb["y"] * CELL + CELL // 2)
            pygame.draw.circle(self.screen, col, center, CELL // 2 - 3)
            sign = "+" if orb["polarity"] > 0 else "-"
            lbl = self.font.render(sign, True, BG_DARK)
            self.screen.blit(lbl, lbl.get_rect(center=center))

        # Draw EMP Surge Rings
        for ring in self.emp_rings:
            col = POS_COLOR if ring["polarity"] > 0 else EMP_COLOR
            center = (int(ring["x"] * CELL + CELL // 2), int(HUD_H + ring["y"] * CELL + CELL // 2))
            pygame.draw.circle(self.screen, col, center, int(ring["radius"] * CELL), 2)

        # Draw Snake
        active_col = POS_COLOR if self.polarity > 0 else NEG_COLOR
        for i, (sx, sy) in enumerate(self.snake):
            rect = pygame.Rect(sx * CELL + 2, HUD_H + sy * CELL + 2, CELL - 4, CELL - 4)
            col = active_col if i == 0 else (max(20, active_col[0] - i * 4), max(40, active_col[1] - i * 4), max(60, active_col[2] - i * 3))
            pygame.draw.rect(self.screen, col, rect, border_radius=7 if i == 0 else 4)

        # Draw HUD
        pygame.draw.rect(self.screen, (16, 22, 36), (0, 0, WIDTH, HUD_H))
        pol_text = "POSITIVE (+)" if self.polarity > 0 else "NEGATIVE (-)"
        hud1 = self.font.render(f"SCORE {self.score:04d}   |   POLARITY [SPACE] {pol_text}", True, active_col)
        hud2 = self.font.render(f"OVERCLOCK [SHIFT] {int(self.charge):03d}%   |   LENGTH {len(self.snake)}", True, (226, 232, 240))
        self.screen.blit(hud1, (20, 12))
        self.screen.blit(hud2, (20, 38))

        if self.game_over:
            banner = self.big_font.render("CIRCUIT FAULT - PRESS R TO REBOOT", True, (248, 113, 113))
            self.screen.blit(banner, banner.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w) and self.direction != (0, 1):
                        self.next_dir = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and self.direction != (0, -1):
                        self.next_dir = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and self.direction != (1, 0):
                        self.next_dir = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.direction != (-1, 0):
                        self.next_dir = (1, 0)
                    elif event.key == pygame.K_SPACE:
                        self.polarity *= -1
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    SnekVoltGame().run()
