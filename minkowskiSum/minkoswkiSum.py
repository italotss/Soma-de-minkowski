import pygame
import numpy as np
import math


# Colors
BG_COLOR = (10, 10, 15)
POINT_COLOR = (249, 127, 81)
HULL_COLOR = (27, 156, 252)
LINE_COLOR = (37, 204, 247)
OBSTACLE_COLOR = (80, 180, 255)
MINKOWSKI_COLOR = (255, 120, 255)
AGENT_COLOR = (120, 255, 120)

WIDTH, HEIGHT = 1000, 1000

def direction(a, b, c):
    # (b-a) x (c-a)
    # Checks vector for negative because screen y-axis is inverted
    return (((b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])) < 0)


def compute_convex_hull(coords):
    if len(coords) < 3:
        return coords.copy()
    hull = []
    leftmost_x = min([xcoord[0] for xcoord in coords])
    leftmost_point = [t for t in coords if leftmost_x == t[0]][0]
    current_point = leftmost_point
    while True:
        hull.append(current_point)
        next_point = coords[(coords.index(current_point) + 1) % len(coords)]
        for check_point in coords:
            if direction(current_point, next_point, check_point):
                next_point = check_point
        current_point = next_point
        if current_point == hull[0]:
            break
    return hull


def pt_add(p1, p2):
    return [p1[0] + p2[0], p1[1] + p2[1]]

def pt_sub(p1, p2):
    return [p1[0] - p2[0], p1[1] - p2[1]]

def pt_cross(p1, p2):
    return p1[0] * p2[1] - p1[1] * p2[0]

def negate_polygon(poly):
    return [[-x, -y] for x, y in poly]

def reorder_polygon(P):
    pos = 0
    for i in range(1, len(P)):
        if P[i][1] < P[pos][1] or (P[i][1] == P[pos][1] and P[i][0] < P[pos][0]):
            pos = i
    P[:] = P[pos:] + P[:pos]

def minkowski(P, Q):
    # the first vertex must be the lowest
    P = [p[:] for p in P] 
    Q = [q[:] for q in Q] 
    reorder_polygon(P)
    reorder_polygon(Q)
    # we must ensure cyclic indexing
    P.append(P[0])
    P.append(P[1])
    Q.append(Q[0])
    Q.append(Q[1])
    # main part
    result = []
    i = 0
    j = 0
    while i < len(P) - 2 or j < len(Q) - 2:
        result.append(pt_add(P[i], Q[j]))
        cross = pt_cross(pt_sub(P[i + 1], P[i]), pt_sub(Q[j + 1], Q[j]))
        if cross >= 0 and i < len(P) - 2:
            i += 1
        if cross <= 0 and j < len(Q) - 2:
            j += 1
    return result

def center_polygon_at_origin(poly):
    if not poly:
        return poly
    cx = sum(x for x, _ in poly) / len(poly)
    cy = sum(y for _, y in poly) / len(poly)
    return [[x - cx, y - cy] for x, y in poly]

def get_polygon_center(poly):
    if not poly:
        return [0, 0]
    cx = sum(x for x, _ in poly) / len(poly)
    cy = sum(y for _, y in poly) / len(poly)
    return [cx, cy]

def translate_polygon(poly, position):
    return [[x + position[0], y + position[1]] for x, y in poly]

def draw_polygon(surface, poly, color, width=2):
    if len(poly) < 2:
        return
    pygame.draw.polygon(surface, color, [(int(x), int(y)) for x, y in poly], width)

def generate_random_convex_polygon(center, radius, num_vertices):
    cx, cy = center
    angles = np.sort(np.random.uniform(0, 2 * math.pi, num_vertices))
    radii = np.random.uniform(radius * 0.5, radius, num_vertices)
    pts = [[cx + float(r * math.cos(a)), cy + float(r * math.sin(a))] for a, r in zip(angles, radii)]
    hull = compute_convex_hull(pts)
    for p in hull:
        p[0] = max(10, min(WIDTH - 10, p[0]))
        p[1] = max(10, min(HEIGHT - 10, p[1]))
    return hull

def main():
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Minkowski Sum")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    np.random.seed() 
    num_obstacles = 6
    obstacles = []
    for _ in range(num_obstacles):
        center = [np.random.randint(200, WIDTH - 200), np.random.randint(200, HEIGHT - 200)]
        radius = np.random.randint(40, 120)
        k = np.random.randint(3, 8)
        poly = generate_random_convex_polygon(center, radius, k)
        obstacles.append(poly)

    agent_shape = [
        [-25, -20],
        [32, 0],
        [-35, 50]
    ]
    agent_centered = center_polygon_at_origin(agent_shape)
 
    agent_negated = negate_polygon(agent_centered)

    agent_position = [100, 800]


    cspace_obstacles = [minkowski(ob, agent_negated) for ob in obstacles]

    running = True
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_x, mouse_y = pygame.mouse.get_pos()
        agent_position = [mouse_x, mouse_y]

        agent_hull = translate_polygon(agent_centered, agent_position)

        window.fill(BG_COLOR)

        for ob in obstacles:
            draw_polygon(window, ob, OBSTACLE_COLOR, width=2)

        for cspace in cspace_obstacles:
            draw_polygon(window, cspace, MINKOWSKI_COLOR, width=1)

        draw_polygon(window, agent_hull, AGENT_COLOR, width=3)

        pygame.draw.circle(window, AGENT_COLOR, 
                          (int(agent_position[0]), int(agent_position[1])), 5)

        window.blit(font.render("Obstacles", True, OBSTACLE_COLOR), (10, 10))
        window.blit(font.render("Minkowski sum", True, MINKOWSKI_COLOR), (10, 35))
        window.blit(font.render("Agent", True, AGENT_COLOR), (10, 60))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()