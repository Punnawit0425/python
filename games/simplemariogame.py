"""
Super Mario - Python Edition
Controls:
  Arrow Left / Right  — Move
  Space / Up Arrow    — Jump (hold for higher jump)
  R                   — Restart
  ESC                 — Quit
"""

import pygame, sys, random, math

# ── Constants ────────────────────────────────────────────────────────────────
W, H        = 900, 540
FPS         = 60
GRAVITY     = 0.55
TILE        = 40

# Palette
SKY         = (107, 189, 255)
CLOUD_C     = (255, 255, 255)
GROUND_TOP  = (92, 184, 92)
GROUND_FILL = (139, 90, 43)
BRICK_C     = (196, 116, 60)
BRICK_DARK  = (160, 82, 30)
QMARK_C     = (255, 200, 0)
QMARK_DARK  = (200, 140, 0)
MARIO_R     = (220, 50,  50)
MARIO_B     = (50,  100, 200)
MARIO_SKIN  = (255, 210, 170)
MARIO_SHOE  = (120, 60,  20)
GOOMBA_C    = (160, 90,  30)
GOOMBA_F    = (200, 130, 60)
COIN_C      = (255, 215, 0)
COIN_SHINE  = (255, 255, 180)
FLAG_G      = (50,  200, 50)
FLAG_W      = (240, 240, 240)
HUD_BG      = (0,   0,   0,  120)

pygame.init()
screen  = pygame.display.set_mode((W, H))
pygame.display.set_caption("🍄  Super Mario – Python Edition")
clock   = pygame.time.Clock()

try:
    font_big   = pygame.font.SysFont("Arial", 42, bold=True)
    font_med   = pygame.font.SysFont("Arial", 26, bold=True)
    font_small = pygame.font.SysFont("Arial", 20)
except:
    font_big = font_med = font_small = pygame.font.Font(None, 36)


# ── Camera ────────────────────────────────────────────────────────────────────
class Camera:
    def __init__(self):
        self.offset_x = 0

    def update(self, player):
        target = player.rect.centerx - W // 3
        self.offset_x += (target - self.offset_x) * 0.12
        self.offset_x = max(0, self.offset_x)

    def apply(self, rect):
        return pygame.Rect(rect.x - self.offset_x, rect.y, rect.width, rect.height)


# ── Tile helpers ──────────────────────────────────────────────────────────────
def draw_brick(surf, rx, ry, rw, rh):
    pygame.draw.rect(surf, BRICK_C,    (rx, ry, rw, rh))
    pygame.draw.rect(surf, BRICK_DARK, (rx, ry, rw, rh), 2)
    for row in range(2):
        y_off = ry + rh // 4 + row * (rh // 2)
        x_off = 0 if row % 2 == 0 else rw // 2
        for col in range(3):
            bx = rx + x_off + col * rw // 2
            pygame.draw.line(surf, BRICK_DARK, (bx, y_off), (bx + rw // 4, y_off), 1)
        pygame.draw.line(surf, BRICK_DARK, (rx, y_off), (rx + rw, y_off), 1)


def draw_qmark(surf, rx, ry, rw, rh, used=False):
    c  = (130, 130, 130) if used else QMARK_C
    cd = (90, 90, 90)    if used else QMARK_DARK
    pygame.draw.rect(surf, c,  (rx, ry, rw, rh))
    pygame.draw.rect(surf, cd, (rx, ry, rw, rh), 3)
    char = "?" if not used else "·"
    txt = font_med.render(char, True, (40, 20, 0) if not used else (80, 80, 80))
    surf.blit(txt, txt.get_rect(center=(rx + rw // 2, ry + rh // 2)))


def draw_ground(surf, rx, ry, rw, rh, cam_off=0):
    pygame.draw.rect(surf, GROUND_FILL, (rx, ry, rw, rh))
    pygame.draw.rect(surf, GROUND_TOP,  (rx, ry, rw, TILE // 4))
    for gx in range(rx, rx + rw, TILE):
        pygame.draw.line(surf, (70, 140, 70), (gx, ry), (gx, ry + TILE // 4), 1)


# ── Coin ──────────────────────────────────────────────────────────────────────
class Coin:
    def __init__(self, x, y):
        self.rect    = pygame.Rect(x + 10, y + 6, 20, 28)
        self.alive   = True
        self.anim    = random.randint(0, 60)

    def update(self):
        self.anim += 1

    def draw(self, surf, cam):
        if not self.alive: return
        r  = self.rect
        cr = cam.apply(r)
        scale = abs(math.sin(self.anim * 0.08))
        cw = max(4, int(20 * scale))
        cx = cr.centerx - cw // 2
        pygame.draw.ellipse(surf, COIN_C,     (cx, cr.y, cw, cr.height))
        pygame.draw.ellipse(surf, COIN_SHINE, (cx + 2, cr.y + 4, max(2, cw // 3), cr.height // 3))


# ── Question Block ─────────────────────────────────────────────────────────────
class QBlock:
    def __init__(self, x, y):
        self.rect  = pygame.Rect(x, y, TILE, TILE)
        self.used  = False
        self.bump  = 0

    def hit(self, coins_list):
        if not self.used:
            self.used = True
            self.bump = 10
            coins_list.append(Coin(self.rect.x, self.rect.y - TILE))

    def update(self):
        if self.bump > 0:
            self.bump -= 2

    def draw(self, surf, cam):
        r  = cam.apply(self.rect)
        ry = r.y - abs(self.bump)
        draw_qmark(surf, r.x, ry, r.width, r.height, self.used)


# ── Goomba ────────────────────────────────────────────────────────────────────
class Goomba:
    def __init__(self, x, y):
        self.rect    = pygame.Rect(x, y - TILE, TILE - 4, TILE)
        self.vx      = -1.4
        self.vy      = 0
        self.alive   = True
        self.squished= False
        self.squish_t= 0
        self.on_ground = False

    def update(self, platforms):
        if self.squished:
            self.squish_t += 1
            if self.squish_t > 40:
                self.alive = False
            return

        self.vy = min(self.vy + GRAVITY, 14)
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.on_ground = False

        for p in platforms:
            if self.rect.colliderect(p):
                if self.vy > 0 and self.rect.bottom - self.vy <= p.top + 4:
                    self.rect.bottom = p.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = p.bottom
                    self.vy = 0
                elif self.vx > 0:
                    self.rect.right = p.left
                    self.vx *= -1
                else:
                    self.rect.left  = p.right
                    self.vx *= -1

    def squish(self):
        self.squished = True
        self.rect.height = TILE // 3
        self.rect.y      += TILE - TILE // 3

    def draw(self, surf, cam):
        if not self.alive: return
        r  = cam.apply(self.rect)
        if self.squished:
            alpha = max(0, 255 - self.squish_t * 6)
            s = pygame.Surface((r.width, TILE // 3), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (*GOOMBA_C, alpha), (0, 0, r.width, TILE // 3))
            surf.blit(s, (r.x, r.y))
            return
        # body
        pygame.draw.ellipse(surf, GOOMBA_C, (r.x, r.y + r.h // 3, r.w, r.h * 2 // 3))
        # head
        pygame.draw.ellipse(surf, GOOMBA_F, (r.x, r.y, r.w, r.h * 2 // 3))
        # eyes
        ex = [r.x + r.w // 4, r.x + r.w * 3 // 4 - 6]
        for ex_ in ex:
            pygame.draw.ellipse(surf, (10, 10, 10), (ex_, r.y + r.h // 6, 8, 8))
            pygame.draw.ellipse(surf, (255, 255, 255), (ex_ + 1, r.y + r.h // 6, 3, 3))
        # feet
        foot_w = r.w // 3
        for fx in [r.x - 2, r.x + r.w - foot_w + 2]:
            pygame.draw.ellipse(surf, GOOMBA_C, (fx, r.bottom - 8, foot_w, 10))


# ── Mario ─────────────────────────────────────────────────────────────────────
class Mario:
    W, H    = 30, 44
    SPEED   = 4.2
    JUMP_V  = -13.5
    MAX_JUMP= 18        # frames jump can be held

    def __init__(self, x, y):
        self.rect      = pygame.Rect(x, y - self.H, self.W, self.H)
        self.vx = self.vy = 0
        self.on_ground = False
        self.facing    = 1
        self.jump_held = 0
        self.alive     = True
        self.won       = False
        self.anim      = 0
        self.dead_t    = 0

    def update(self, keys, platforms, qblocks, goombas, coins, flag_rect):
        if not self.alive:
            self.dead_t += 1
            if self.dead_t == 10: self.vy = -12
            self.vy = min(self.vy + GRAVITY, 14)
            self.rect.y += self.vy
            return

        # Horizontal
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx    = -self.SPEED
            self.facing = -1
        if keys[pygame.K_RIGHT]:
            self.vx    = self.SPEED
            self.facing = 1

        # Jump
        jump_key = keys[pygame.K_SPACE] or keys[pygame.K_UP]
        if jump_key and self.on_ground:
            self.vy        = self.JUMP_V
            self.jump_held = 0
            self.on_ground = False
        elif jump_key and self.jump_held and self.jump_held < self.MAX_JUMP:
            self.vy        = self.JUMP_V * (1 - self.jump_held / self.MAX_JUMP) * 0.4 + self.vy * 0.9
            self.jump_held += 0.5
        elif not jump_key:
            self.jump_held = 0

        self.vy = min(self.vy + GRAVITY, 14)

        # Move X
        self.rect.x   += self.vx
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vx > 0: self.rect.right = p.left
                else:           self.rect.left  = p.right
                self.vx = 0

        # Move Y
        self.on_ground = False
        self.rect.y   += self.vy
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vy > 0:
                    self.rect.bottom = p.top
                    self.vy = 0
                    self.on_ground = True
                    self.jump_held = 0
                else:
                    self.rect.top = p.bottom
                    self.vy       = 1
                    # check Q-blocks
                    for qb in qblocks:
                        if qb.rect == p:
                            qb.hit(coins)

        # Fall out of world
        if self.rect.top > H + 60:
            self.alive = False

        # Goomba collision
        for g in goombas:
            if not g.alive or g.squished: continue
            if self.rect.colliderect(g.rect):
                if self.vy > 0 and self.rect.bottom < g.rect.centery + 12:
                    g.squish()
                    self.vy = -8
                else:
                    self.alive = False
                    return

        # Coin collection
        for c in coins:
            if c.alive and self.rect.colliderect(c.rect):
                c.alive = False

        # Flag
        if flag_rect and self.rect.colliderect(flag_rect):
            self.won = True

        if self.vx != 0:
            self.anim += 1

    def draw(self, surf, cam):
        r  = cam.apply(self.rect)
        fx = -1 if self.facing == -1 else 1

        def px(ox, oy, w, h):
            x = r.x + (ox if fx == 1 else self.W - ox - w)
            return (x, r.y + oy, w, h)

        if not self.alive:
            # spinning dead Mario
            pygame.draw.ellipse(surf, MARIO_R,    (*r.topleft, r.w, r.h // 2))
            pygame.draw.ellipse(surf, MARIO_SKIN, (*r.topleft, r.w, r.h // 4))
            return

        # Cap
        pygame.draw.rect(surf, MARIO_R,    px(2,  0, 26, 8))
        pygame.draw.rect(surf, MARIO_R,    px(0,  6, 30, 6))
        # Face
        pygame.draw.rect(surf, MARIO_SKIN, px(2, 10, 26, 14))
        # Eye
        pygame.draw.rect(surf, (30, 30, 30), px(17, 12, 6, 6))
        # Mustache
        pygame.draw.rect(surf, (80, 40, 10), px(6, 20, 20, 5))
        # Overalls
        pygame.draw.rect(surf, MARIO_B,    px(2, 24, 26, 14))
        pygame.draw.rect(surf, MARIO_R,    px(6, 24,  7, 7))
        pygame.draw.rect(surf, MARIO_R,    px(17,24,  7, 7))
        # Legs
        walk = int(math.sin(self.anim * 0.25) * 4) if self.vx != 0 else 0
        pygame.draw.rect(surf, MARIO_B,    px(2,  38, 12, 6))
        pygame.draw.rect(surf, MARIO_B,    px(16, 38, 12, 6))
        # Shoes
        pygame.draw.rect(surf, MARIO_SHOE, px(0,  40, 14, 4))
        pygame.draw.rect(surf, MARIO_SHOE, px(16, 40, 14, 4))


# ── Level Builder ─────────────────────────────────────────────────────────────
def build_level():
    platforms  = []
    qblocks    = []
    goombas    = []
    coins_list = []

    WORLD_W = 5600

    # Ground
    for gx in range(0, 2800, TILE):
        platforms.append(pygame.Rect(gx, H - TILE, TILE, TILE * 3))
    # gap at 2800-3040
    for gx in range(3040, 4200, TILE):
        platforms.append(pygame.Rect(gx, H - TILE, TILE, TILE * 3))
    # gap 4200-4320
    for gx in range(4320, WORLD_W + TILE, TILE):
        platforms.append(pygame.Rect(gx, H - TILE, TILE, TILE * 3))

    # Elevated platforms
    steps = [
        (400,  H - TILE * 3, 3),
        (640,  H - TILE * 4, 2),
        (880,  H - TILE * 3, 4),
        (1200, H - TILE * 5, 3),
        (1520, H - TILE * 4, 2),
        (1760, H - TILE * 3, 5),
        (2200, H - TILE * 5, 4),
        (2520, H - TILE * 3, 3),
        (3200, H - TILE * 4, 4),
        (3600, H - TILE * 5, 3),
        (4000, H - TILE * 3, 5),
        (4500, H - TILE * 4, 3),
        (4900, H - TILE * 5, 4),
    ]
    for sx, sy, sw in steps:
        for i in range(sw):
            platforms.append(pygame.Rect(sx + i * TILE, sy, TILE, TILE))

    # Q-blocks
    qb_positions = [
        (480,  H - TILE * 5),
        (920,  H - TILE * 6),
        (1240, H - TILE * 7),
        (1560, H - TILE * 6),
        (2240, H - TILE * 7),
        (3240, H - TILE * 6),
        (4040, H - TILE * 5),
        (4540, H - TILE * 6),
    ]
    for qx, qy in qb_positions:
        qb = QBlock(qx, qy)
        qblocks.append(qb)
        platforms.append(qb.rect)

    # Coins on ground and platforms
    coin_spots = [
        (300, H - TILE * 2), (340, H - TILE * 2), (380, H - TILE * 2),
        (700, H - TILE * 5), (740, H - TILE * 5),
        (1000, H - TILE * 4), (1040, H - TILE * 4),
        (1600, H - TILE * 5), (1640, H - TILE * 5),
        (2300, H - TILE * 2), (2340, H - TILE * 2), (2380, H - TILE * 2),
        (3300, H - TILE * 5), (3340, H - TILE * 5), (3380, H - TILE * 5),
        (4100, H - TILE * 4), (4140, H - TILE * 4),
        (4600, H - TILE * 5), (4640, H - TILE * 5),
    ]
    for cx, cy in coin_spots:
        coins_list.append(Coin(cx, cy))

    # Goombas
    goomba_x = [500, 760, 1000, 1300, 1700, 2100, 2400, 3100, 3500, 3900, 4200, 4700, 5000, 5200]
    for gx in goomba_x:
        goombas.append(Goomba(gx, H - TILE))

    # Flag pole at end
    flag_pole_x = WORLD_W - TILE * 2
    flag_rect   = pygame.Rect(flag_pole_x, H - TILE * 9, 12, TILE * 9)

    return platforms, qblocks, goombas, coins_list, flag_rect, WORLD_W


# ── Draw Clouds (parallax) ────────────────────────────────────────────────────
CLOUDS = [(i * 380 + 80, 50 + (i % 3) * 30) for i in range(18)]

def draw_clouds(surf, cam_x):
    for cx, cy in CLOUDS:
        rx = cx - cam_x * 0.3
        pygame.draw.ellipse(surf, CLOUD_C, (rx, cy,      80, 35))
        pygame.draw.ellipse(surf, CLOUD_C, (rx + 20, cy - 18, 60, 40))
        pygame.draw.ellipse(surf, CLOUD_C, (rx + 50, cy,      70, 30))


def draw_flag(surf, cam, flag_rect, world_w):
    r  = cam.apply(flag_rect)
    # pole
    pygame.draw.rect(surf, (180, 180, 180), (r.x + 1, r.y, 4, r.height))
    # flag
    pts = [(r.x + 5, r.y), (r.x + 35, r.y + 15), (r.x + 5, r.y + 30)]
    pygame.draw.polygon(surf, FLAG_G, pts)
    # castle silhouette at end
    cx = r.x + TILE
    pygame.draw.rect(surf, (150, 150, 170), (cx, H - TILE * 5, TILE * 3, TILE * 5))
    for i in range(5):
        if i % 2 == 0:
            pygame.draw.rect(surf, (150, 150, 170), (cx + i * TILE // 2, H - TILE * 6, TILE // 2, TILE))


def draw_hud(surf, mario, coins_list, level_t):
    collected = sum(1 for c in coins_list if not c.alive)
    total     = len(coins_list)
    time_sec  = level_t // FPS

    hud = pygame.Surface((W, 44), pygame.SRCALPHA)
    hud.fill((0, 0, 0, 130))
    surf.blit(hud, (0, 0))

    surf.blit(font_small.render(f"🍄  MARIO",          True, (255, 255, 255)), (12, 10))
    surf.blit(font_small.render(f"🪙  {collected}/{total}", True, COIN_C),     (180, 10))
    surf.blit(font_small.render(f"⏱  {time_sec:03d}s", True, (200, 240, 255)), (360, 10))
    surf.blit(font_small.render("← → MOVE  |  SPACE JUMP  |  R RESTART",
                                 True, (180, 180, 180)), (500, 12))


# ── Main Game Loop ────────────────────────────────────────────────────────────
def main():
    running = True
    while running:
        platforms, qblocks, goombas, coins_list, flag_rect, WORLD_W = build_level()
        mario    = Mario(80, H - TILE)
        camera   = Camera()
        level_t  = 0
        won_timer = 0

        while True:
            clock.tick(FPS)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    if event.key == pygame.K_r:
                        break           # restart
            else:
                # ── Update ──────────────────────────────────────────────────
                mario.update(keys, platforms, qblocks, goombas, coins_list, flag_rect)
                camera.update(mario)

                for qb in qblocks: qb.update()
                for g  in goombas: g.update(platforms)
                for c  in coins_list: c.update()

                if mario.won:
                    won_timer += 1

                if mario.alive and not mario.won:
                    level_t += 1

                # ── Draw ────────────────────────────────────────────────────
                screen.fill(SKY)
                draw_clouds(screen, camera.offset_x)

                # Ground & platforms
                for p in platforms:
                    r = camera.apply(p)
                    if -TILE < r.x < W + TILE:
                        if p.y >= H - TILE:
                            draw_ground(screen, r.x, r.y, r.width, r.height, camera.offset_x)
                        else:
                            # check if it's a Q-block
                            is_q = any(qb.rect == p for qb in qblocks)
                            if not is_q:
                                draw_brick(screen, r.x, r.y, r.width, r.height)

                for qb in qblocks: qb.draw(screen, camera)
                for c  in coins_list: c.draw(screen, camera)
                draw_flag(screen, camera, flag_rect, WORLD_W)
                for g  in goombas: g.draw(screen, camera)
                mario.draw(screen, camera)
                draw_hud(screen, mario, coins_list, level_t)

                # Win screen
                if mario.won:
                    if won_timer > 30:
                        ov = pygame.Surface((W, H), pygame.SRCALPHA)
                        ov.fill((0, 0, 0, 160))
                        screen.blit(ov, (0, 0))
                        coins_got = sum(1 for c in coins_list if not c.alive)
                        screen.blit(font_big.render("🎉 YOU WIN! 🎉", True, COIN_C),
                                    font_big.render("🎉 YOU WIN! 🎉", True, COIN_C).get_rect(center=(W//2, H//2-60)))
                        screen.blit(font_med.render(f"Coins: {coins_got}/{len(coins_list)}  Time: {level_t//FPS}s",
                                                     True, (255, 255, 255)),
                                    font_med.render(f"Coins: {coins_got}/{len(coins_list)}  Time: {level_t//FPS}s",
                                                     True, (255, 255, 255)).get_rect(center=(W//2, H//2)))
                        screen.blit(font_small.render("Press  R  to play again", True, (200, 200, 200)),
                                    font_small.render("Press  R  to play again", True, (200, 200, 200)).get_rect(center=(W//2, H//2+60)))
                    if keys[pygame.K_r]:
                        break

                # Death screen
                if not mario.alive and mario.dead_t > 80:
                    ov = pygame.Surface((W, H), pygame.SRCALPHA)
                    ov.fill((0, 0, 0, 160))
                    screen.blit(ov, (0, 0))
                    screen.blit(font_big.render("💀  GAME OVER", True, (255, 80, 80)),
                                font_big.render("💀  GAME OVER", True, (255, 80, 80)).get_rect(center=(W//2, H//2-40)))
                    screen.blit(font_small.render("Press  R  to restart", True, (200, 200, 200)),
                                font_small.render("Press  R  to restart", True, (200, 200, 200)).get_rect(center=(W//2, H//2+30)))
                    if keys[pygame.K_r]:
                        break

                pygame.display.flip()
                continue
            break   # inner restart


if __name__ == "__main__":
    main()