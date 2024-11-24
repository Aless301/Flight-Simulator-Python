import pygame
import sys
import random
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
TEXT_COLOR = (255, 255, 255)
BACKGROUND_GREEN = (53, 104, 45)
FOREST_GREEN = (64, 125, 54)
COMPASS_COLOR = (255, 255, 255)

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

# Gestion du carburant
fuel = 100.0  # Pourcentage de carburant
fuel_consumption_rate = 0.0001  # Taux de consommation par frame
fuel_recovery_rate = 0.05  # Taux de récupération à l'arrêt

# Fonction pour simuler des zones montagneuses et plates
def get_altitude(x, y):
    frequency = 0.001
    noise = math.sin(frequency * x) * math.sin(frequency * y)
    return abs(noise)

# Générer le paysage
def generate_landscape():
    elements = []

    # Création de zones agricoles
    for _ in range(10):
        cluster_x = random.randint(0, LANDSCAPE_WIDTH)
        cluster_y = random.randint(0, LANDSCAPE_HEIGHT)

        if clear_zone_rect.collidepoint(cluster_x, cluster_y) or get_altitude(cluster_x, cluster_y) > 0.4:
            continue

        for _ in range(random.randint(5, 15)):
            x = cluster_x + random.randint(-100, 100)
            y = cluster_y + random.randint(-100, 100)
            width = random.randint(30, 120)
            height = random.randint(20, 80)
            color = random.choice([GREEN_FIELD, BROWN_FIELD])
            elements.append(("rect", color, pygame.Rect(x, y, width, height)))

    # Création des forêts et villages
    for _ in range(300):
        x = random.randint(0, LANDSCAPE_WIDTH)
        y = random.randint(0, LANDSCAPE_HEIGHT)
        width = random.randint(100, 250)
        height = random.randint(80, 200)

        if clear_zone_rect.collidepoint(x, y) or get_altitude(x, y) > 0.6:
            continue

        terrain_type = random.choice(["forest", "village"])
        if terrain_type == "forest":
            elements.append(("forest_rect", FOREST_GREEN, pygame.Rect(x, y, width, height)))
            for _ in range(random.randint(20, 60)):
                tree_x = x + random.randint(0, width)
                tree_y = y + random.randint(0, height)
                elements.append(("tree", (tree_x, tree_y)))
        elif terrain_type == "village":
            house_width = random.randint(30, 50)
            house_height = random.randint(30, 50)
            for _ in range(random.randint(1, 5)):
                house_x = x + random.randint(0, width)
                house_y = y + random.randint(0, height)
                elements.append(("rect", GREY_VILLAGE, pygame.Rect(house_x, house_y, house_width, house_height)))

    return elements

landscape_elements = generate_landscape()

# Fonction pour afficher les informations de vol
def display_flight_info():
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    time_text = font.render(f"Temps de vol : {minutes:02d}:{seconds:02d}", True, TEXT_COLOR)
    window.blit(time_text, (10, 10))

    speed_px_per_frame = math.sqrt(plane_speed_x ** 2 + plane_speed_y ** 2)
    speed_kmh = speed_px_per_frame * 60 * 60 / 1000
    speed_text = font.render(f"Vitesse : {speed_kmh:.1f} km/h", True, TEXT_COLOR)
    window.blit(speed_text, (10, 40))

# Fonction pour afficher le niveau de carburant
def display_fuel_level():
    fuel_bar_width = 200
    fuel_bar_height = 20
    fuel_bar_x = WIDTH - fuel_bar_width - 20
    fuel_bar_y = 10

    pygame.draw.rect(window, (255, 255, 255), (fuel_bar_x, fuel_bar_y, fuel_bar_width, fuel_bar_height), 2)
    fuel_fill_width = fuel_bar_width * (fuel / 100)
    pygame.draw.rect(window, (0, 255, 0), (fuel_bar_x, fuel_bar_y, fuel_fill_width, fuel_bar_height))

    fuel_text = font.render(f"Carburant : {fuel:.1f}%", True, TEXT_COLOR)
    window.blit(fuel_text, (fuel_bar_x, fuel_bar_y + 25))

# Appliquer la physique de vol
def apply_physics():
    global plane_speed_x, plane_speed_y
    plane_speed_x -= drag * plane_speed_x
    plane_speed_y -= drag * plane_speed_y

# Calculer la rotation de l'avion
def calculate_plane_rotation(speed_x, speed_y):
    return math.degrees(math.atan2(-speed_y, speed_x))

# Fonction pour afficher l'écran de fin
def show_end_screen(reason):
    window.fill((0, 0, 0))  # Fond noir
    if reason == "fuel":
        end_text = font.render("Carburant épuisé !", True, TEXT_COLOR)
    elif reason == "quit":
        end_text = font.render("Vous avez quitté le jeu.", True, TEXT_COLOR)

    continue_text = font.render("Appuyez sur Espace pour rejouer ou sur Echap pour quitter.", True, TEXT_COLOR)

    # Centrer le texte sur l'écran
    end_text_rect = end_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    continue_text_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))

    # Afficher les textes
    window.blit(end_text, end_text_rect)
    window.blit(continue_text, continue_text_rect)
    pygame.display.flip()

    # Attendre l'entrée du joueur
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Quitter
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:  # Rejouer
                    main()  # Redémarrer le jeu

# Fonction pour afficher la boussole et le repère de la piste
def display_compass():
    # Position de la boussole
    compass_radius = 50
    compass_x = WIDTH - compass_radius - 20
    compass_y = HEIGHT - compass_radius - 20
    pygame.draw.circle(window, COMPASS_COLOR, (compass_x, compass_y), compass_radius, 3)

    # Calculer l'angle de l'avion (boussole) pour qu'il pointe vers le nord
    plane_angle = math.degrees(math.atan2(-plane_speed_y, plane_speed_x)) % 360
    compass_angle = (360 - plane_angle) % 360  # Pour faire pointer la boussole vers le nord

    # Dessiner la flèche de la boussole
    angle_rad = math.radians(compass_angle)
    arrow_length = compass_radius - 10
    arrow_x = compass_x + math.cos(angle_rad) * arrow_length
    arrow_y = compass_y + math.sin(angle_rad) * arrow_length
    pygame.draw.line(window, COMPASS_COLOR, (compass_x, compass_y), (arrow_x, arrow_y), 3)

    # Calculer la direction de la piste par rapport à la position de l'avion
    angle_to_runway = math.degrees(math.atan2(runway_y - plane_y, runway_x - plane_x)) % 360

    # Ajuster la direction de la piste pour qu'elle corresponde à la boussole
    runway_angle_on_compass = (compass_angle - angle_to_runway) % 360

    # Dessiner le repère de la piste sur la boussole
    runway_x_pos = compass_x + math.cos(math.radians(runway_angle_on_compass)) * (compass_radius - 10)
    runway_y_pos = compass_y + math.sin(math.radians(runway_angle_on_compass)) * (compass_radius - 10)
    pygame.draw.circle(window, (255, 0, 0), (int(runway_x_pos), int(runway_y_pos)), 5)

# Boucle principale du jeu
def main():
    global plane_x, plane_y, plane_speed_x, plane_speed_y, fuel
    start_time = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                show_end_screen("quit")

        # Contrôles de l'avion
        keys = pygame.key.get_pressed()
        moving = False
        if keys[pygame.K_UP]:
            plane_speed_y -= 0.1
            moving = True
        if keys[pygame.K_DOWN]:
            plane_speed_y += 0.1
            moving = True
        if keys[pygame.K_LEFT]:
            plane_speed_x -= 0.1
            moving = True
        if keys[pygame.K_RIGHT]:
            plane_speed_x += 0.1
            moving = True

        # Gestion du carburant
        if moving:
            fuel -= fuel_consumption_rate * (abs(plane_speed_x) + abs(plane_speed_y)) * 2
        else:
            fuel += fuel_recovery_rate
        fuel = max(0, min(100, fuel))

        if fuel <= 0:
            show_end_screen("fuel")

        # Limiter la vitesse
        plane_speed_x = max(-max_speed, min(max_speed, plane_speed_x))
        plane_speed_y = max(-max_speed, min(max_speed, plane_speed_y))

        # Appliquer la physique
        apply_physics()

        # Calculer la rotation et la position de l'avion
        plane_rotation = calculate_plane_rotation(plane_speed_x, plane_speed_y)
        plane_x += plane_speed_x
        plane_y += plane_speed_y

        # Afficher l'arrière-plan et les éléments avec parallaxe
        window.fill(BACKGROUND_GREEN)
        for element in landscape_elements:
            if element[0] in ["rect", "forest_rect"]:
                color, rect = element[1], element[2]
                adjusted_rect = pygame.Rect(
                    rect.x - plane_x + WIDTH // 2,
                    rect.y - plane_y + HEIGHT // 2,
                    rect.width,
                    rect.height
                )
                pygame.draw.rect(window, color, adjusted_rect)

            if element[0] == "tree":
                tree_x, tree_y = element[1]
                display_x = tree_x - plane_x + WIDTH // 2
                display_y = tree_y - plane_y + HEIGHT // 2
                pygame.draw.rect(window, (139, 69, 19), (display_x, display_y + 15, 5, 15))
                pygame.draw.circle(window, (144, 238, 144), (display_x + 2, display_y), 10)

        # Dessiner la piste
        window.blit(runway_img, (runway_x - plane_x + WIDTH // 2, runway_y - plane_y + HEIGHT // 2))

        # Dessiner l'avion
        rotated_plane = pygame.transform.rotate(plane_img, plane_rotation)
        plane_rect = rotated_plane.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        window.blit(rotated_plane, plane_rect.topleft)

        # Afficher les informations de vol et le carburant
        display_flight_info()
        display_fuel_level()

        # Afficher la boussole
        display_compass()

        # Rafraîchir l'écran
        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Lancer le jeu
main()
