import pygame
import sys
import random
import os
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Simulateur de vol")

# Couleurs
GREEN_FIELD = (34, 139, 34)
BROWN_FIELD = (139, 69, 19)
GREY_VILLAGE = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
TEXT_COLOR = (0, 0, 0)
BACKGROUND_GREEN = (53, 104, 45)
FOREST_GREEN = (64, 125, 54)

# Police pour l'affichage du texte
font = pygame.font.SysFont("Arial", 24)

# Charger les images de l'avion et de la piste
try:
    plane_img = pygame.image.load("plane.png").convert_alpha()
    plane_img = pygame.transform.scale(plane_img, (60, 40))
    plane_img = pygame.transform.rotate(plane_img, -90)

    runway_img = pygame.image.load("runway.png").convert_alpha()
    runway_img = pygame.transform.scale(runway_img, (104, 612))
except pygame.error as e:
    print("Erreur lors du chargement de l'image:", e)
    pygame.quit()
    sys.exit()

# Position initiale de la piste
LANDSCAPE_WIDTH, LANDSCAPE_HEIGHT = WIDTH * 3, HEIGHT * 3
runway_x = LANDSCAPE_WIDTH // 2 - runway_img.get_width() // 2
runway_y = LANDSCAPE_HEIGHT // 2 - runway_img.get_height() // 2

# Zone dégagée autour de la piste
clear_zone_margin = 150
clear_zone_rect = pygame.Rect(
    runway_x - clear_zone_margin,
    runway_y - clear_zone_margin,
    runway_img.get_width() + 2 * clear_zone_margin,
    runway_img.get_height() + 2 * clear_zone_margin
)

# Position de départ de l'avion
plane_x = runway_x + runway_img.get_width() // 2 - plane_img.get_width() // 2
plane_y = runway_y + runway_img.get_height() - plane_img.get_height() - 20

# Variables de vol
plane_speed_x, plane_speed_y = 0, 0
max_speed = 7
drag = 0.01
start_time = pygame.time.get_ticks()

# Fonction pour simuler des zones montagneuses et plates
def get_altitude(x, y):
    frequency = 0.001  # Ajuster pour plus ou moins de montagnes
    noise = math.sin(frequency * x) * math.sin(frequency * y)
    return abs(noise)
    
# Forets pas trop proche des champs
def is_too_close(rect, elements, min_distance):
    for element in elements:
        if element[0] in ["rect", "forest_rect"]:  # Vérifier uniquement pour les champs et forêts
            existing_rect = element[2]
            distance = math.sqrt((rect.centerx - existing_rect.centerx) ** 2 +
                                  (rect.centery - existing_rect.centery) ** 2)
            if distance < min_distance:
                return True
    return False

# Fonction pour générer le paysage
def generate_landscape():
    elements = []

    # Création de zones agricoles
    for _ in range(10):  # 10 zones agricoles
        cluster_x = random.randint(0, LANDSCAPE_WIDTH)
        cluster_y = random.randint(0, LANDSCAPE_HEIGHT)

        if clear_zone_rect.collidepoint(cluster_x, cluster_y) or get_altitude(cluster_x, cluster_y) > 0.4:
            continue

        for _ in range(random.randint(5, 15)):  # Champs individuels
            x = cluster_x + random.randint(-100, 100)
            y = cluster_y + random.randint(-100, 100)
            width = random.randint(30, 120)
            height = random.randint(20, 80)
            color = random.choice([GREEN_FIELD, BROWN_FIELD])
            new_rect = pygame.Rect(x, y, width, height)

            if not is_too_close(new_rect, elements, min_distance=20):  # Espacement minimal
                elements.append(("rect", color, new_rect))


        # Générer forêts et villages dans d'autres zones
    for _ in range(300):  # Générer forêts et villages
        x = random.randint(0, LANDSCAPE_WIDTH)
        y = random.randint(0, LANDSCAPE_HEIGHT)
        width = random.randint(100, 250)
        height = random.randint(80, 200)

        if clear_zone_rect.collidepoint(x, y) or get_altitude(x, y) > 0.6:
            continue

        new_rect = pygame.Rect(x, y, width, height)
        if not is_too_close(new_rect, elements, min_distance=30):  # Espacement minimal pour les forêts
            terrain_type = random.choice(["forest", "village"])
            if terrain_type == "forest":
                color = FOREST_GREEN
                elements.append(("forest_rect", color, new_rect))
                for _ in range(random.randint(20, 60)):  # Ajouter des arbres
                    tree_x = x + random.randint(0, width)
                    tree_y = y + random.randint(0, height)
                    elements.append(("tree", (tree_x, tree_y)))
        elif terrain_type == "village":
            color = GREY_VILLAGE
            house_width = random.randint(30, 50)
            house_height = random.randint(30, 50)
            for _ in range(random.randint(1, 5)):
                house_x = x + random.randint(0, width)
                house_y = y + random.randint(0, height)
                house_rect = pygame.Rect(house_x, house_y, house_width, house_height)
                elements.append(("rect", color, house_rect))

        elif terrain_type == "village":
            color = GREY_VILLAGE
            house_width = random.randint(30, 50)
            house_height = random.randint(30, 50)
            for _ in range(random.randint(1, 5)):
                house_x = x + random.randint(0, width)
                house_y = y + random.randint(0, height)
                elements.append(("rect", color, pygame.Rect(house_x, house_y, house_width, house_height)))

    return elements

landscape_elements = generate_landscape()

# Fonction pour afficher le temps de vol et la vitesse
def display_flight_info():
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    time_text = font.render(f"Temps de vol : {minutes:02d}:{seconds:02d}", True, TEXT_COLOR)
    window.blit(time_text, (10, 10))

    speed_px_per_frame = math.sqrt(plane_speed_x ** 2 + plane_speed_y ** 2)
    speed_kmh = speed_px_per_frame * 60 * 60 / 1000
    speed_text = font.render(f"Vitesse : {speed_kmh:.1f} km/h", True, TEXT_COLOR)
    window.blit(speed_text, (WIDTH - speed_text.get_width() - 10, 10))

# Fonction pour dessiner un petit aéroport à gauche de la piste
def draw_airport(plane_x, plane_y):
    airport_x = runway_x - 300  # À gauche de la piste
    airport_y = runway_y + 100  # Aligné verticalement avec la piste
    terminal_rect = pygame.Rect(
        airport_x - plane_x + WIDTH // 2,
        airport_y - plane_y + HEIGHT // 2,
        100, 150
    )
    pygame.draw.rect(window, GREY_VILLAGE, terminal_rect)

    hangar_width, hangar_height = 80, 60
    for i in range(3):  # Trois hangars alignés
        hangar_rect = pygame.Rect(
            airport_x + i * (hangar_width + 10) - plane_x + WIDTH // 2,
            airport_y + 160 - plane_y + HEIGHT // 2,
            hangar_width,
            hangar_height
        )
        pygame.draw.rect(window, BROWN_FIELD, hangar_rect)

    parking_spacing = 50
    for i in range(4):  # Quatre emplacements de parking
        parking_x = airport_x + 110 + i * parking_spacing
        parking_y = airport_y + 80
        pygame.draw.rect(window, (255, 255, 255), (
            parking_x - plane_x + WIDTH // 2,
            parking_y - plane_y + HEIGHT // 2,
            40, 20
        ), 2)

# Fonction pour appliquer la physique
def apply_physics():
    global plane_speed_x, plane_speed_y
    plane_speed_x -= drag * plane_speed_x
    plane_speed_y -= drag * plane_speed_y

# Fonction pour calculer la rotation de l'avion
def calculate_plane_rotation(speed_x, speed_y):
    return math.degrees(math.atan2(-speed_y, speed_x))

# Boucle principale du jeu
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    # Contrôles de l'avion
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        plane_speed_y -= 0.1
    if keys[pygame.K_DOWN]:
        plane_speed_y += 0.1
    if keys[pygame.K_LEFT]:
        plane_speed_x -= 0.1
    if keys[pygame.K_RIGHT]:
        plane_speed_x += 0.1

    # Limiter la vitesse
    plane_speed_x = max(-max_speed, min(max_speed, plane_speed_x))
    plane_speed_y = max(-max_speed, min(max_speed, plane_speed_y))

    # Appliquer la physique
    apply_physics()

    # Calculer la rotation et la position de l'avion
    plane_rotation = calculate_plane_rotation(plane_speed_x, plane_speed_y)
    plane_x += plane_speed_x
    plane_y += plane_speed_y

    # Remplir l'écran
    window.fill(BACKGROUND_GREEN)

    # Dessiner les éléments du paysage en deux étapes pour l'ordre d'affichage
    for element in landscape_elements:
        if element[0] == "rect" or element[0] == "forest_rect":
            color, rect = element[1], element[2]
            adjusted_rect = pygame.Rect(
                rect.x - plane_x + WIDTH // 2,
                rect.y - plane_y + HEIGHT // 2,
                rect.width,
                rect.height
            )
            pygame.draw.rect(window, color, adjusted_rect)

    for element in landscape_elements:
        if element[0] == "tree":
            tree_x, tree_y = element[1]
            display_x = tree_x - plane_x + WIDTH // 2
            display_y = tree_y - plane_y + HEIGHT // 2
            pygame.draw.rect(window, (139, 69, 19), (display_x, display_y + 15, 5, 15))
            pygame.draw.circle(window, (144, 238, 144), (display_x + 2, display_y), 10)

    # Dessiner la piste de décollage
    window.blit(runway_img, (runway_x - plane_x + WIDTH // 2, runway_y - plane_y + HEIGHT // 2))

    # **Dessiner l'aéroport à gauche de la piste**
    draw_airport(plane_x, plane_y)

    # Dessiner l'avion
    rotated_plane = pygame.transform.rotate(plane_img, plane_rotation)
    plane_rect = rotated_plane.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(rotated_plane, plane_rect.topleft)

    # Afficher les informations de vol
    display_flight_info()

    # Rafraîchir l'écran
    pygame.display.flip()
    pygame.time.Clock().tick(60)
