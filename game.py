# Importation des bibliothèques nécessaires au jeu
import pygame
from pygame import mixer
import random

# Initialisation de pygame
pygame.init()

# Création de la fenêtre du jeu
WIDTH, HEIGHT = 750, 750  # Définition de la taille de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # Application de la taille de la fenêtre
pygame.display.set_caption("Space Invader - Jikan Games") # Nom de la fenêtre
icon = pygame.image.load('data/img/player/player.png') # Définition de l'icône de la fenêtre
pygame.display.set_icon(icon) # Afifchage de l'icône de la fenêtre

# Chargement des sprites ennemis
RED_ENEMY = pygame.image.load("data/img/enemies/enemy_red.png")
GREEN_ENEMY = pygame.image.load("data/img/enemies/enemy_green.png")
BLUE_ENEMY = pygame.image.load("data/img/enemies/enemy_blue.png")

# Chargement du sprite du Joueur
PLAYER_SHIP = pygame.image.load("data/img/player/player.png")

# Chargement des sprites des lasers
RED_LASER = pygame.image.load("data/img/enemies/enemy_red_laser.png")
GREEN_LASER = pygame.image.load("data/img/enemies/enemy_green_laser.png")
BLUE_LASER = pygame.image.load("data/img/enemies/enemy_blue_laser.png")
YELLOW_LASER = pygame.image.load("data/img/player/player_laser.png")

# Mise en place du Background
BG = pygame.transform.scale(pygame.image.load("data/img/background.png"), (WIDTH, HEIGHT))


# Mise en place des lasers
class Laser:
    # Initialisation des lasers
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    # Affichage des lasers
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    # Mouvements des lasers
    def move(self, vel):
        self.y += vel

    # Position des lasers (s'ils sont en dehors de la fenêtre)
    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    # Hitbox des lasers
    def collision(self, obj):
        return collide(self, obj)


# Mise en place d'une template de personnage pour créer le Joueur et les Ennemis
class Ship:
    # Cooldown du laser en FPS, sachant que le jeu tourne à 60 FPS, le cooldown est donc de 0,5 secondes
    COOLDOWN = 30

    # Initialisation du personnage (barre de vie et lasers)
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    # Affichage des lasers selon la postion du personnage
    def draw(self, window):
        window.blit(self.ship_img, (self.x - 15, self.y))
        for laser in self.lasers:
            laser.draw(window)

    # Déplacement et destruction du laser
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                hitSound = mixer.Sound("data/musics/hit.wav")
                hitSound.play()
                self.lasers.remove(laser)

    # Mise en place du Cooldown
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    # Mise en place du tir
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            laserSound = mixer.Sound("data/musics/laser.wav")
            laserSound.play()
            self.lasers.append(laser)
            self.cool_down_counter = 1

    # Savoir la taille du personnage
    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


# Création du Joueur à partir de la Template de personnage (Ship)
class Player(Ship):
    # Initialisation du Joueur
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP # Définition du sprite du joueur
        self.laser_img = YELLOW_LASER # Définition du sprite du laser du joueur
        self.mask = pygame.mask.from_surface(self.ship_img) # Définition de la place que prend le joueur
        self.max_health = health # Définition de la vie du joueur

    # Déplacement et destruction du laser du joueur
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel) # Déplacement du laser selon sa vélocité
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs: # Pour tous les objets (c'est à dire les ennemis) présents sur le jeu
                    if laser.collision(obj): # Si le laser rentre en collision avec ces objets
                        objs.remove(obj) # Alors détruire l'objet en question
                        explosionSound = mixer.Sound("data/musics/explosion.wav") # Trouver le bruit de l'explosion
                        explosionSound.play() # Le jouer
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    # Définition de l'affichage de la barre de vie
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    # Affichage de la barre de vie en dessous du vaisseau du joueur
    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x - 15, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x - 15, self.y + self.ship_img.get_height() + 10,
                                               self.ship_img.get_width() * (self.health / self.max_health), 10))


# Création des Ennemis à partir de la Template de personnage (Ship)
class Enemy(Ship):
    # Liste des Ennemis existants
    COLOR_MAP = {
        "red": (RED_ENEMY, RED_LASER),
        "green": (GREEN_ENEMY, GREEN_LASER),
        "blue": (BLUE_ENEMY, BLUE_LASER)
    }

    # Initialisation des Ennemis
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    # Mouvements des Ennemis
    def move(self, vel):
        self.y += vel

    # Tir des Ennemis
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y + 50, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


# Création de la Hitbox
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


# Création du Jeu
def game():
    run = True  # Ceci permet de faire tourner la fenêtre du jeu à l'infini pour que le jeu ne se ferme pas seul
    locked_FPS = 60  # Bridage des FPS à 60 pour un meilleur contrôle de vitesse
    level = 0  # Niveau du départ
    lives = 5  # Nombre de Vies (c'est à dire le nombre d'ennemi pouvant traverser le bas de le fenêtre)
    main_font = pygame.font.Font("data/fonts/pixelated.ttf", 40) # Définition de la police d'écriture des Vies et Niveaux
    lost_font = pygame.font.Font("data/fonts/pixelated.ttf", 125) # Définition de la police d'écriture de Game Over
    # Lecture de la musique de fond
    mixer.music.stop()
    mixer.music.load("data/musics/xDeviruchi - Minigame (Loop).wav")
    mixer.music.play(-1)

    enemies = []
    wave_length = 5 # Nombre d'ennemi à la première vague (premier niveau)
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630) # Spawn du Joueur

    clock = pygame.time.Clock() # Création de l'horloge interne du jeu (permettant plus tard de la fixer à 60 FPS)

    lost = False
    lost_count = 0

    def redraw_window():
        screen.blit(BG, (0, 0)) # Affichage de Background
        # Setup des stats
        lives_label = main_font.render(f"Vie(s) : {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Niveau : {level}", 1, (255, 255, 255))
        # Affichage des stats
        screen.blit(lives_label, (10, 10))
        screen.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # Affichage des Ennemis
        for enemy in enemies:
            enemy.draw(screen)

        # Affichage du Joueur
        player.draw(screen)

        # Si le Joueur perds
        if lost:
            mixer.music.stop() # Arrêter la musique de fond
            lost_label = lost_font.render("Game Over", 1, (255, 255, 255)) # Setup du Game Over
            screen.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, HEIGHT / 2)) # Affichage du Game Over
            mixer.music.load("data/musics/xDeviruchi - Minigame (Intro).wav") # Définition de la musique du Menu
            mixer.music.play(-1) # Lecture de cette musique

        # Rafraichir l'écran
        pygame.display.update()

    # Quand le jeu se lance
    while run:
        clock.tick(locked_FPS) # Limiter les fps à 60
        redraw_window() # Refaire la fenêtre

        if lives <= 0 or player.health <= 0: # Si le joueur a laissé passé X Ennemis ou s'il a perdu toute sa vie
            lost = True # Alors lost (perdu) est vrai (donc il a perdu)
            lost_count += 1 # Nombre de défaite

        if lost: # Si le joueur a perdu
            if lost_count > locked_FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0: # S'il n'y a plus d'ennemi
            level += 1 # Passer au niveau suivant
            wave_length += 5 # Rajouter 5 ennemis en plus à ce niveau (donc niveau 1 : 5; niveau 2 : 10; etc)
            for i in range(wave_length): # Pour chaque ennemis dans la vague (niveau)
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), # Spwan random dans une certaine zone
                              random.choice(["red", "blue", "green"])) # Avec une couleur random
                enemies.append(enemy) # Faire spawn les ennemis

        for event in pygame.event.get(): # Pour chauqe events détéctés par Pygame
            if event.type == pygame.QUIT: # Si l'event est Quitter
                quit() # Alors fermer le jeu
            if event.type == pygame.KEYDOWN: # Si l'event est une touche du clavier
                if event.key == pygame.K_ESCAPE: # Voir si la touche est la touche ECHAP
                    main_menu() # Puis lancer le Menu Principal

        # Input du Joueur - Clavier
        keys = pygame.key.get_pressed() # Définiton de cette variable pour éviter de toujours devoir réécrire pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0 or keys[
            pygame.K_q] and player.x - player_vel > 0:  # Gauche
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH or keys[
            pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # Droite
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0 or keys[pygame.K_z] and player.y - player_vel > 0:  # Haut
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT or keys[
            pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # Bas
            player.y += player_vel
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            player.shoot()  # Tirer

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1: # Création d'un chiffre au hasard, s'il est égal à 1
                enemy.shoot() # Tirer

            if collide(enemy, player): # Si le joueur rentre en collison avec un ennemi
                player.health -= 10 # Retirer 10PV au joueur
                enemies.remove(enemy) # Détruire l'ennemi
                explosionSound = mixer.Sound("data/musics/explosion.wav") # Trouver la musique d'explosion
                explosionSound.play() # La jouer
            elif enemy.y + enemy.get_height() > HEIGHT: # Si un ennemi dépasse le bas de la fenêtre de jeu
                lives -= 1 # Retiré 1 vie au joueur
                enemies.remove(enemy) # Détruire l'ennemi
                explosionSound = mixer.Sound("data/musics/explosion.wav") # Trouver la musique d'explosion
                explosionSound.play() # La jouer

        player.move_lasers(-laser_vel, enemies)


# Menu Principal
def main_menu():
    title_font = pygame.font.Font("data/fonts/pixelated.ttf", 80) # Définiton de la police du titre
    menu_font = pygame.font.Font("data/fonts/pixelated.ttf", 40) # Définition de la police des textes du menu
    copyrights_font = pygame.font.Font("data/fonts/pixelated.ttf", 20) # Défintion de la police du copyright
    run = True
    # Lecture de la musique de fond
    mixer.music.load("data/musics/xDeviruchi - Minigame (Intro).wav")
    mixer.music.play(-1)
    while run:
        screen.blit(BG, (0, 0)) # Afficher le Background
        title_label = title_font.render("Space Invader", 1, (255, 255, 255)) # Définir le titre
        start_label = menu_font.render("Appuyez sur ESPACE pour commencer", 1, (255, 255, 255)) # Définir la ligne concerant la barre ESPACE
        quit_label = menu_font.render("Appuyez sur ECHAP pour quitter", 1, (255, 255, 255)) # Définir la ligne concernant la touche ECHAP
        copyrights_label = copyrights_font.render("Jikan Games 2021", 1, (255, 255, 255)) # Définir les copyrights
        # Afficher tous ces messages à l'écran
        screen.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, HEIGHT - 550))
        screen.blit(start_label, (WIDTH / 2 - start_label.get_width() / 2, HEIGHT - 400))
        screen.blit(quit_label, (WIDTH / 2 - quit_label.get_width() / 2, HEIGHT - 350))
        screen.blit(copyrights_label, (WIDTH - 670 - copyrights_label.get_width() / 2, HEIGHT - 40))
        # Mettre à jour l'écran
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game()
                if event.key == pygame.K_ESCAPE:
                    run = False
    pygame.quit()


main_menu()

# Merci à toutes les personnes qui ont pris le temps de lire tout ce code et d'essayer de le comprendre
# Merci également à tous ceux qui ont joué au jeu