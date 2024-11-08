import pygame
import sys
import random
import os

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
DARK_GREEN = (0, 100, 0)  # Forêts
LIGHT_BLUE = (135, 206, 235)  # Ciel clair
DARK_BLUE = (70, 130, 180)  # Océan ou rivières
MOUNTAIN_COLOR = (169, 169, 169)  # Montagnes
RIVER_COLOR = (0, 191, 255)  # Rivières
LIGHT_GREEN = (144, 238, 144)  # Fond vert

# Charger l'image de l'avion
base_path = os.path.dirname(__file__)
plane_img_path = os.path.join(base_path, "plane.png")

try:
    plane_img = pygame.image.load(plane_img_path).convert_alpha()
    plane_img = pygame.transform.scale(plane_img, (60, 40))
except pygame.error as e:
    print("Erreur lors du chargement de l'image:", e)
    pygame.quit()
    sys.exit()

# Police pour l'affichage du texte
font = pygame.font.SysFont("Arial", 24)
TEXT_COLOR = (0, 0, 0)
BUTTON_COLOR = (255, 0, 0)

# Variables pour l'avion
plane_x, plane_y = WIDTH // 2, HEIGHT // 2
plane_speed_x, plane_speed_y = 0, 0
max_speed = 7  # Augmenter la vitesse maximale
start_time = pygame.time.get_ticks()

# Paramètres de la zone étendue du paysage
LANDSCAPE_WIDTH, LANDSCAPE_HEIGHT = WIDTH * 3, HEIGHT * 3

# Générer un paysage étendu et détaillé
def generate_landscape():
    landscape_elements = []
    for _ in range(500):  # Plus d'éléments pour une densité accrue
        x = random.randint(0, LANDSCAPE_WIDTH)
        y = random.randint(0, LANDSCAPE_HEIGHT)
        width = random.randint(30, 120)
        height = random.randint(20, 80)

        # Générer différents types de terrain
        terrain_type = random.choice(["field", "forest", "village", "river", "mountain"])
        if terrain_type == "field":
            color = random.choice([GREEN_FIELD, BROWN_FIELD])
        elif terrain_type == "forest":
            color = DARK_GREEN
        elif terrain_type == "village":
            color = GREY_VILLAGE
        elif terrain_type == "river":
            color = RIVER_COLOR
            y += height  # Les rivières peuvent être plus basses dans le paysage
        elif terrain_type == "mountain":
            color = MOUNTAIN_COLOR
            height *= 2  # Les montagnes sont plus grandes
            y -= height // 2  # Les montagnes doivent être plus élevées dans le paysage

        landscape_elements.append((color, pygame.Rect(x, y, width, height)))
    return landscape_elements

landscape_elements = generate_landscape()

# Réinitialiser le jeu
def reset_game():
    global plane_x, plane_y, plane_speed_x, plane_speed_y, start_time, landscape_elements
    plane_x, plane_y = WIDTH // 2, HEIGHT // 2
    plane_speed_x, plane_speed_y = 0, 0
    start_time = pygame.time.get_ticks()
    landscape_elements = generate_landscape()

reset_game()  # Initialise les valeurs du jeu

# Fonction pour afficher le menu de pause
def display_pause_menu():
    pause_font = pygame.font.SysFont("Arial", 48)
    pause_text = pause_font.render("PAUSE", True, TEXT_COLOR)
    window.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 100))
    resume_text = font.render("Appuyez sur ESC pour reprendre", True, TEXT_COLOR)
    window.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2))

# Variables pour la gestion de la pause
is_paused = False
pause_start_time = 0

# Boucle principale du jeu
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if is_paused:
                    is_paused = False
                    # Reprendre le timer
                    start_time += pygame.time.get_ticks() - pause_start_time
                else:
                    is_paused = True
                    # Sauvegarder le temps de la pause
                    pause_start_time = pygame.time.get_ticks()

    # Si le jeu est en pause, ne met pas à jour la position de l'avion ni le paysage
    if not is_paused:
        # Récupérer les touches pressées
        keys = pygame.key.get_pressed()

        # Mouvement de l'avion avec inertie
        if keys[pygame.K_UP]:
            plane_speed_y -= 0.8  # Augmenter la vitesse de montée
        if keys[pygame.K_DOWN]:
            plane_speed_y += 0.8  # Augmenter la vitesse de descente
        if keys[pygame.K_LEFT]:
            plane_speed_x -= 0.8  # Augmenter la vitesse vers la gauche
        if keys[pygame.K_RIGHT]:
            plane_speed_x += 0.8  # Augmenter la vitesse vers la droite

        # Limiter la vitesse
        plane_speed_x = max(min(plane_speed_x, max_speed), -max_speed)
        plane_speed_y = max(min(plane_speed_y, max_speed), -max_speed)

        # Appliquer la gravité légère
        plane_speed_y += 0.05

        # Mise à jour de la position de l'avion
        plane_x += plane_speed_x
        plane_y += plane_speed_y

        # Mise à jour de l'affichage du fond
        window.fill(LIGHT_GREEN)  # Remplir avec le fond vert (ciel de campagne)

        # Dessiner le paysage étendu et détaillé
        for color, rect in landscape_elements:
            adjusted_rect = pygame.Rect(
                (rect.x - plane_x) % LANDSCAPE_WIDTH - WIDTH // 2,
                (rect.y - plane_y) % LANDSCAPE_HEIGHT - HEIGHT // 2,
                rect.width, rect.height
            )
            pygame.draw.rect(window, color, adjusted_rect)

        # Afficher l'avion
        window.blit(plane_img, (WIDTH // 2, HEIGHT // 2))

        # Afficher la vitesse et le temps
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        speed_kmh = ((plane_speed_x**2 + plane_speed_y**2) ** 0.5) * 3.6  # Conversion en km/h
        speed_text = font.render(f"Vitesse: {speed_kmh:.2f} km/h", True, TEXT_COLOR)
        window.blit(speed_text, (10, 10))

        # Afficher le timer
        timer_text = font.render(f"Temps: {elapsed_time // 60}:{elapsed_time % 60:02}", True, TEXT_COLOR)
        window.blit(timer_text, (10, 40))
    else:
        display_pause_menu()

    pygame.display.flip()
    pygame.time.Clock().tick(30)
