import math
import pygame

from managers.assets import find_asset

TEXT_DARK = (225, 255, 225)
TEXT_MUTED = (140, 190, 150)
TEXT_LIGHT = (232, 250, 225)
GREEN = (34, 160, 66)
GREEN_HOVER = (52, 195, 86)
GREEN_DARK = (16, 96, 44)
CARD = (4, 20, 12)
CARD_BORDER = (40, 150, 80)
FIELD = (6, 30, 18)
RED = (255, 100, 100)
GOLD = (255, 205, 60)

NEON = (90, 255, 120)
NEON_TEXT = (225, 255, 225)
NEON_MUTED = (140, 190, 150)
NEON_RED = (255, 110, 110)

BTN_FILL = (70, 235, 100)
BTN_HOVER = (120, 255, 145)
BTN_EDGE = (20, 130, 55)
BTN_TEXT = (4, 24, 12)

_fonts = {}
_backgrounds = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("Arial", size, bold=bold)
    return _fonts[key]


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _build_background(w, h, dark, stars=True):
    surf = pygame.Surface((w, h))

    if dark:
        top, bottom = (6, 26, 28), (28, 78, 60)
    else:
        top, bottom = (28, 82, 68), (150, 205, 140)

    for y in range(h):
        pygame.draw.line(
            surf, _lerp(top, bottom, y / h), (0, y), (w, y)
        )

    if stars:
        for i in range(70):
            x = (i * 137 + 31) % w
            y = (i * 83 + 17) % int(h * 0.6)
            r = 2 if i % 5 == 0 else 1
            pygame.draw.circle(surf, (215, 245, 205), (x, y), r)

    px, py = w - 95, 95
    pygame.draw.circle(surf, (130, 185, 120), (px, py), 48)
    pygame.draw.circle(surf, (96, 152, 98), (px - 15, py + 10), 12)
    pygame.draw.circle(surf, (96, 152, 98), (px + 18, py - 14), 8)
    pygame.draw.circle(surf, (170, 215, 150), (px, py), 48, 2)

    pygame.draw.ellipse(
        surf, (70, 140, 82), (-180, h - 200, int(w * 0.85), 340)
    )
    pygame.draw.ellipse(
        surf, (92, 162, 94), (int(w * 0.3), h - 160, int(w * 0.95), 320)
    )
    pygame.draw.ellipse(
        surf, (58, 118, 70), (-120, h - 85, w + 240, 260)
    )

    pygame.draw.polygon(
        surf, (40, 78, 66),
        [(w - 150, h - 60), (w - 110, h - 150), (w - 80, h - 100),
         (w - 50, h - 170), (w, h - 70), (w, h)]
    )
    pygame.draw.polygon(
        surf, (40, 78, 66),
        [(0, h - 60), (40, h - 130), (90, h - 80), (120, h)]
    )

    return surf


def _load_menu_image(w, h):
    try:
        image = pygame.image.load(find_asset("ranmenu.png")).convert()
        image = pygame.transform.smoothscale(image, (w, h))

        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 110))
        image.blit(dim, (0, 0))

        return image

    except (FileNotFoundError, pygame.error) as e:
        print(f"Cannot load ranmenu.png: {e}")
        return None


def draw_background(screen, w, h, dark=False):
    key = (w, h, dark)

    if key not in _backgrounds:
        surf = None if dark else _load_menu_image(w, h)
        _backgrounds[key] = surf or _build_background(w, h, dark)

    screen.blit(_backgrounds[key], (0, 0))


def draw_text(screen, text, size, color, center=None,
              topleft=None, bold=False):
    surface = font(size, bold).render(text, True, color)

    if center:
        rect = surface.get_rect(center=center)
    else:
        rect = surface.get_rect(topleft=topleft)

    screen.blit(surface, rect)
    return rect


def draw_outline_text(screen, text, size, color, outline, center,
                      thickness=3):
    f = font(size, True)
    base = f.render(text, True, color)
    edge = f.render(text, True, outline)
    rect = base.get_rect(center=center)

    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx * dx + dy * dy <= thickness * thickness:
                screen.blit(edge, rect.move(dx, dy))

    screen.blit(base, rect)


INVADER = [
    "..#.....#..",
    "...#...#...",
    "..#######..",
    ".##.###.##.",
    "###########",
    "#.#######.#",
    "#.#.....#.#",
    "...##.##...",
]


def draw_invader(screen, cx, top, px, color):
    width = len(INVADER[0]) * px
    left = cx - width // 2

    for row, line in enumerate(INVADER):
        for col, ch in enumerate(line):
            if ch == "#":
                pygame.draw.rect(
                    screen, (20, 60, 30),
                    (left + col * px + 1, top + row * px + 2, px, px)
                )

    for row, line in enumerate(INVADER):
        for col, ch in enumerate(line):
            if ch == "#":
                pygame.draw.rect(
                    screen, color,
                    (left + col * px, top + row * px, px, px)
                )


def draw_logo(screen, cx, top=12):
    draw_invader(screen, cx, top, 5, (160, 235, 110))

    draw_outline_text(
        screen, "SPACE", 66, (175, 240, 100), (20, 60, 30),
        (cx, top + 78)
    )

    draw_outline_text(
        screen, "INVADERS", 32, (238, 252, 228), (20, 60, 30),
        (cx, top + 124), 3
    )


def draw_login_title(screen, cx, cy):
    draw_outline_text(
        screen, "SPACE INVADERS", 34, (150, 255, 110), (8, 60, 20),
        (cx, cy), 2
    )


def draw_dark_card(screen, rect, radius=22):
    pad = 14
    surf = pygame.Surface(
        (rect.width + pad * 2, rect.height + pad * 2), pygame.SRCALPHA
    )
    body = pygame.Rect(pad, pad, rect.width, rect.height)

    for i in range(pad, 0, -2):
        alpha = int(40 * (1 - i / pad)) + 4
        pygame.draw.rect(
            surf, (60, 255, 100, alpha), body.inflate(i * 2, i * 2),
            border_radius=radius + i
        )

    pygame.draw.rect(surf, (4, 20, 12, 215), body, border_radius=radius)
    pygame.draw.rect(
        surf, (90, 255, 120, 255), body, 2, border_radius=radius
    )

    screen.blit(surf, (rect.x - pad, rect.y - pad))


def draw_card(screen, rect, radius=22):
    draw_dark_card(screen, rect, radius)


def draw_icon(screen, name, cx, cy, color):
    if name == "play":
        pygame.draw.polygon(
            screen, color,
            [(cx - 8, cy - 11), (cx - 8, cy + 11), (cx + 11, cy)]
        )

    elif name == "trophy":
        pygame.draw.rect(screen, color, (cx - 8, cy - 11, 16, 12),
                         border_bottom_left_radius=8,
                         border_bottom_right_radius=8)
        pygame.draw.circle(screen, color, (cx - 10, cy - 6), 5, 2)
        pygame.draw.circle(screen, color, (cx + 10, cy - 6), 5, 2)
        pygame.draw.line(screen, color, (cx, cy + 1), (cx, cy + 7), 3)
        pygame.draw.rect(screen, color, (cx - 7, cy + 7, 14, 4))

    elif name == "gear":
        for i in range(8):
            a = i * math.pi / 4
            pygame.draw.line(
                screen, color,
                (cx + math.cos(a) * 7, cy + math.sin(a) * 7),
                (cx + math.cos(a) * 12, cy + math.sin(a) * 12), 4
            )
        pygame.draw.circle(screen, color, (cx, cy), 9, 4)

    elif name == "user":
        pygame.draw.circle(screen, color, (cx, cy - 5), 6)
        pygame.draw.ellipse(screen, color, (cx - 11, cy + 3, 22, 14))

    elif name == "arrow_left":
        pygame.draw.polygon(
            screen, color,
            [(cx - 14, cy), (cx + 2, cy - 13), (cx + 2, cy - 5),
             (cx + 14, cy - 5), (cx + 14, cy + 5), (cx + 2, cy + 5),
             (cx + 2, cy + 13)]
        )

    elif name == "arrow_right":
        pygame.draw.polygon(
            screen, color,
            [(cx + 14, cy), (cx - 2, cy - 13), (cx - 2, cy - 5),
             (cx - 14, cy - 5), (cx - 14, cy + 5), (cx - 2, cy + 5),
             (cx - 2, cy + 13)]
        )

    elif name == "fire":
        pygame.draw.polygon(
            screen, (255, 140, 40),
            [(cx - 4, cy + 9), (cx + 4, cy + 9), (cx, cy + 17)]
        )
        pygame.draw.polygon(
            screen, color,
            [(cx, cy - 15), (cx + 6, cy - 3), (cx + 6, cy + 9),
             (cx - 6, cy + 9), (cx - 6, cy - 3)]
        )
        pygame.draw.polygon(
            screen, color,
            [(cx - 6, cy + 1), (cx - 12, cy + 10), (cx - 6, cy + 9)]
        )
        pygame.draw.polygon(
            screen, color,
            [(cx + 6, cy + 1), (cx + 12, cy + 10), (cx + 6, cy + 9)]
        )
        pygame.draw.circle(screen, (30, 90, 60), (cx, cy - 3), 3)

    elif name == "logout":
        pygame.draw.lines(
            screen, color, False,
            [(cx + 1, cy - 11), (cx - 10, cy - 11),
             (cx - 10, cy + 11), (cx + 1, cy + 11)], 3
        )
        pygame.draw.line(screen, color, (cx - 3, cy), (cx + 11, cy), 3)
        pygame.draw.polygon(
            screen, color,
            [(cx + 12, cy - 6), (cx + 12, cy + 6), (cx + 19, cy)]
        )


def draw_button(screen, rect, text, hover, style="primary",
                size=22, icon=None):
    if style == "primary":
        bg = BTN_HOVER if hover else BTN_FILL
        edge = BTN_EDGE
        fg = BTN_TEXT
        icon_color = BTN_TEXT
        radius = rect.height // 2
    else:
        bg = (16, 62, 36) if hover else (6, 30, 18)
        edge = (40, 170, 80)
        fg = NEON_TEXT
        icon_color = NEON
        radius = 18

    pygame.draw.rect(
        screen, edge, rect.move(0, 4), border_radius=radius
    )
    pygame.draw.rect(screen, bg, rect, border_radius=radius)

    if style != "primary":
        pygame.draw.rect(
            screen, NEON if hover else (60, 200, 100), rect, 2,
            border_radius=radius
        )

    if icon:
        draw_icon(screen, icon, rect.x + 42, rect.centery, icon_color)

    draw_text(screen, text, size, fg, center=rect.center, bold=True)


def draw_back_button(screen, rect, hover):
    bg = BTN_HOVER if hover else BTN_FILL
    pygame.draw.rect(screen, BTN_EDGE, rect.move(0, 3),
                     border_radius=12)
    pygame.draw.rect(screen, bg, rect, border_radius=12)

    cx, cy = rect.center
    pygame.draw.lines(
        screen, BTN_TEXT, False,
        [(cx + 4, cy - 9), (cx - 5, cy), (cx + 4, cy + 9)], 4
    )


def draw_toggle(screen, rect, on):
    color = BTN_FILL if on else (60, 85, 70)
    pygame.draw.rect(screen, color, rect, border_radius=rect.height // 2)

    r = rect.height // 2 - 4
    x = rect.right - r - 5 if on else rect.x + r + 5
    knob = (4, 24, 12) if on else (200, 220, 205)
    pygame.draw.circle(screen, knob, (x, rect.centery), r)


def draw_input(screen, rect, placeholder, value, active,
               password=False, show=False, dark=True):
    bg = (6, 30, 18)
    edge = NEON if active else (40, 120, 70)
    text_color = NEON_TEXT
    hint_color = (110, 160, 125)
    icon_color = (140, 200, 150)

    pygame.draw.rect(screen, bg, rect, border_radius=12)
    pygame.draw.rect(screen, edge, rect, 2, border_radius=12)

    f = font(17)
    max_w = rect.width - (70 if password else 36)

    if value:
        shown = value if (not password or show) else "\u2022" * len(value)

        while f.size(shown)[0] > max_w and len(shown) > 1:
            shown = shown[1:]

        surface = f.render(shown, True, text_color)
    else:
        surface = f.render(placeholder, True, hint_color)

    pos = (rect.x + 16, rect.centery - surface.get_height() // 2)
    screen.blit(surface, pos)

    if active and (pygame.time.get_ticks() // 500) % 2 == 0:
        cx = pos[0] + (surface.get_width() if value else 0) + 2
        pygame.draw.line(
            screen, text_color, (cx, rect.y + 12),
            (cx, rect.bottom - 12), 2
        )

    if password:
        ex, ey = rect.right - 28, rect.centery
        pygame.draw.ellipse(
            screen, icon_color, (ex - 11, ey - 6, 22, 12), 2
        )
        pygame.draw.circle(screen, icon_color, (ex, ey), 3)

        if not show:
            pygame.draw.line(
                screen, icon_color, (ex - 10, ey + 8),
                (ex + 10, ey - 8), 2
            )


def draw_link_line(screen, prefix, link, center_y, cx, dark=True):
    f = font(14)
    fl = font(14, True)

    prefix_color = NEON_MUTED
    link_color = NEON

    a = f.render(prefix + "  ", True, prefix_color)
    b = fl.render(link, True, link_color)

    total = a.get_width() + b.get_width()
    x = cx - total // 2

    screen.blit(a, (x, center_y - a.get_height() // 2))
    rect = b.get_rect(topleft=(x + a.get_width(),
                               center_y - b.get_height() // 2))
    screen.blit(b, rect)
    pygame.draw.line(
        screen, link_color, (rect.x, rect.bottom), (rect.right, rect.bottom), 1
    )

    return rect.inflate(10, 12)


def draw_heart(screen, cx, cy, size, color, outline=None):
    r = max(2, int(size * 0.27))
    left = (cx - r, cy - int(r * 0.6))
    right = (cx + r, cy - int(r * 0.6))
    tri = [
        (cx - int(r * 1.95), cy - int(r * 0.2)),
        (cx + int(r * 1.95), cy - int(r * 0.2)),
        (cx, cy + int(size * 0.5)),
    ]

    pygame.draw.circle(screen, color, left, r)
    pygame.draw.circle(screen, color, right, r)
    pygame.draw.polygon(screen, color, tri)

    if outline:
        pygame.draw.circle(screen, outline, left, r, 1)
        pygame.draw.circle(screen, outline, right, r, 1)
        pygame.draw.polygon(screen, outline, tri, 1)


def draw_hud(screen, w, score, lives, level, max_lives=3):

    def pill(rect):
        pygame.draw.rect(screen, (10, 44, 40), rect,
                         border_radius=rect.height // 2)
        pygame.draw.rect(screen, (90, 175, 125), rect, 2,
                         border_radius=rect.height // 2)

    y, h = 6, 30
    score_r = pygame.Rect(10, y, 150, h)
    lives_r = pygame.Rect(w // 2 - 52, y, 104, h)
    level_r = pygame.Rect(w - 133, y, 84, h)

    for r in (score_r, lives_r, level_r):
        pill(r)

    label = (200, 235, 200)

    draw_text(screen, "SCORE", 11, label,
              topleft=(score_r.x + 14, score_r.centery - 7))
    draw_text(screen, f"{score:06d}", 15, (255, 255, 255),
              topleft=(score_r.x + 60, score_r.centery - 9), bold=True)

    for i in range(max_lives):
        x = lives_r.centerx - 26 + i * 26

        if i < lives:
            draw_heart(screen, x, lives_r.centery - 2, 18,
                       (235, 75, 95), (255, 190, 200))
        else:
            draw_heart(screen, x, lives_r.centery - 2, 18,
                       (40, 75, 68), (90, 130, 115))

    draw_text(screen, "LEVEL", 11, label,
              topleft=(level_r.x + 12, level_r.centery - 7))
    draw_text(screen, f"{level:02d}", 15, (255, 255, 255),
              topleft=(level_r.x + 54, level_r.centery - 9), bold=True)