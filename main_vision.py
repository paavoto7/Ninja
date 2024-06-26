from os import listdir
from sys import argv
import random
import math

import pygame
import mediapipe as mp
import cv2

from menu import menu
from Score import Score

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Model in use: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
model_path = "./vision/hand_landmarker.task"

# Initialise some constants
FPS = 60
SCREEN_BOTTOM = 810
SCREEN_WIDTH = 926
SCORE = 0
HIGH_SCORE = 0
LIVES = 5
CREATE_FRUIT = pygame.event.custom_type()
INTERVAL = 1000 if len(argv) == 1 else int(argv[1])

images = {}
images["fruits"] = []

def load_images():
    """Loads all the images in the assets folder.
    Puts the fruits in a list so that fruit generation can randomly choose them.
    """
    for imagename in listdir("./assets/"):
        if "fruit" in imagename:
            images["fruits"].append((pygame.image.load(f"./assets/{imagename}").convert_alpha(),
                                     imagename[0:-4].strip("_fruit")))
        else:
            images[imagename[0:-4]] = pygame.image.load(f"./assets/{imagename}").convert_alpha()


class Fruit(pygame.sprite.Sprite):
    """Creates the fruit that falls"""
    def __init__(self, image: pygame.surface.Surface, position, *groups) -> None:
        super().__init__(*groups)
        self.image = image[0]
        self.name = image[1]
        self.rect = self.image.get_rect(center=position)
        self.speed = random.randint(30,40)
        self.side = 1 if SCREEN_WIDTH / 2 > self.rect.centerx else -1

        self.angle = math.radians(random.uniform(self._angle(position[0]), 90))
        self.vx = self.speed * self.side * math.cos(self.angle)
        self.vy = self.speed * math.sin(self.angle)
    
    def _angle(self, x):
        angle = min(((SCREEN_WIDTH-x)*0.981)/self.speed**2, 1)
        return 90 - math.degrees(0.5*math.asin(angle))
    
    def _update_falling(self):
        # The one for non hand movement
        self.rect.y += 5
        if self.rect.y >= SCREEN_BOTTOM:
            global LIVES
            LIVES -= 1
            self.kill()
    
    def update(self):
        """Handles the motion of the fruit"""
        self.rect.x += self.vx
        self.rect.y -= self.vy
        self.vy -= 0.98
        if self.rect.midtop[1] >= SCREEN_BOTTOM:
            global LIVES
            LIVES -= 1
            self.kill()


class Sliced(pygame.sprite.Sprite):
    """Creates a sliced fruit based on which fruit was sliced and the side."""
    def __init__(self, whole: Fruit, order, *groups) -> None:
        super().__init__(*groups)
        self.image = images[f"{whole.name}_{order}"]
        self.order = order
        self.rect = self._set_rect(whole)
        self.velx = 0
        self.vely = 0
        self.acceleration = -0.5 if self.order == 1 else 0.5

    def _set_rect(self, whole):
        # Decides whether to use the left or right side of sliced
        if self.order == 1:
            return self.image.get_rect(topright=whole.rect.midbottom)
        else:
            return self.image.get_rect(topleft=whole.rect.midbottom)
    
    def update(self):
        # Makes the movement more natural
        self.velx += self.acceleration
        self.vely += 1
        self.rect.x += self.velx
        self.rect.y += self.vely
        if self.rect.y >= SCREEN_BOTTOM:
            self.kill()


class Katana(pygame.sprite.Sprite):
    """Acts as the player sprite and updates on mouse movement"""
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.image = images["katana"]
        #self.rect = self.image.get_rect(center=(100, 100))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.pos = pygame.Vector2((100,100))
        self.sound = pygame.mixer.Sound("./sounds/Recording.wav")
        self.sound.set_volume(0.2)

    def update(self):
        heading = pygame.mouse.get_pos() - self.pos
        self.pos += heading
        self.rect.bottomright = self.pos

        angle = (SCREEN_WIDTH / 180) * (self.rect.x / 100)
        self.image = pygame.transform.rotate(images["katana"], angle)
    
    def update_from_hand(
        self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int
    ):
        """Update the position of the Katana based on the mediapipe hand results"""
        if len(landmarks := result.hand_landmarks) == 0:
            if not self._out_of_bounds():  
                self.pos += self.pos * 0.01
                self.rect.bottomright = self.pos
            return
        
        avg_landmarks = self._average(landmarks[0])
        heading = (
            avg_landmarks[0] * SCREEN_WIDTH,
            avg_landmarks[1] * SCREEN_BOTTOM
            ) - self.pos
        self.pos += heading * 0.1
        self.rect.bottomright = self.pos

        angle = (SCREEN_WIDTH / 180) * (self.rect.x / 100)
        self.image = pygame.transform.rotate(images["katana"], angle)
    
    def create_mask(self):
        """This solves a peculiar bug that happened when I called
        the following line in the update_from_hand method.
        Might be caused by the detect_async and callback of mediapipe.
        """
        self.mask = pygame.mask.from_surface(self.image)
    
    def _out_of_bounds(self):
        # Don't update the positon if isn't in bounds of the screen
        if 0 <= self.pos.x <= SCREEN_WIDTH and 0 <= self.pos.y <= SCREEN_BOTTOM:
            return False
        else:
            return True
    
    def _average(self, landmarks) -> tuple[float, float]:
        # Return the average coordinates of the middle of the hand
        # Indexes are the points of hand (https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker#models)
        results = landmarks[6:-1]
        x = y = 0
        for coords in results:
            x += coords.x
            y += coords.y
        return (x / len(results), y / len(results))


def fruit_generator(group: pygame.sprite.Group, width=SCREEN_WIDTH) -> None:
    """Generate the fruits.
    """
    # Choose a random image from
    image = random.choice(images["fruits"])
    position = (random.randint(0 + image[0].get_width(), width - image[0].get_width()), SCREEN_BOTTOM)
    Fruit(image, position, group)


def generate_sliced(whole:pygame.sprite.Sprite, group) -> None:
    """Generate the sliced fruits"""
    Sliced(whole, 1, group)
    Sliced(whole, 2, group)


def save_score():
    with open("./high_score.txt", "w") as score:
        score.write(str(SCORE))


def load_score():
    global HIGH_SCORE
    with open("./high_score.txt", "r") as score:
        HIGH_SCORE = int(score.read())


def quit(screen, clock, fruits, sliced, game_over=False) -> bool:
    """Function for quitting and initialising a fresh game.
    Takes the screen canvas and clock.
    Takes fruits and sliced to empty them.
    game_over is optional.
    """
    global LIVES, SCORE
    SCORE = 0
    LIVES = 5
    fruits.empty()
    sliced.empty()
    return menu(screen, clock, FPS, images["shoji"], game_over)


def check_collided(sprite: Katana, other_sprite: Fruit) -> bool:
    """Checks accurately (masks) whether fruit was hit"""
    return pygame.sprite.collide_mask(sprite, other_sprite) is not None


def main():
    global SCORE, LIVES
    load_score()

    pygame.init()

    screen_size = (SCREEN_WIDTH, SCREEN_BOTTOM)
    screen = pygame.display.set_mode(screen_size, pygame.SCALED)
    clock = pygame.time.Clock()

    load_images()

    # Create the sprite groups
    fruits = pygame.sprite.Group()
    sliced = pygame.sprite.Group()
    katanaGroup = pygame.sprite.GroupSingle()

    katana = Katana(katanaGroup)

    score = Score("impact", SCORE, (50, 50), 100, "white")
    fps_display = Score("impact", 0, (50, 120), 80, "white")

    # A timer to create new fruits
    pygame.time.set_timer(CREATE_FRUIT, INTERVAL)

    options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            num_hands=1,
            min_hand_detection_confidence=0.01,
            min_hand_presence_confidence=0.01,
            min_tracking_confidence=0.01,
            result_callback=katana.update_from_hand
        )

    cam = cv2.VideoCapture(0)
    handlandmarker = HandLandmarker.create_from_options(options)
    timestamp = 0

    running = menu(screen, clock, FPS, images["shoji"])

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = quit(screen, clock, fruits, sliced)
            if event.type == CREATE_FRUIT:
                fruit_generator(fruits, screen.get_width())
        
        ret, frame = cam.read()
        # Flip so the coordinates are correct to the viewer
        frame = cv2.flip(frame, 1)

        if not ret:
            print("Ignoring empty frame")
            break

        timestamp += 1
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

        # Can be used for reducing stress: if timestamp % 2 != 0:
        handlandmarker.detect_async(mp_image, timestamp)

        
        if LIVES == 0:
            save_score()
            running = quit(screen, clock, fruits, sliced, game_over=True)
        
        if collideds := pygame.sprite.spritecollide(katana, fruits, False, collided=check_collided):
            SCORE += 1
            katana.sound.play()
            for collided in collideds:
                generate_sliced(collided, sliced)
                collided.kill()
            # Update the timer every ten fruits until the fruits start spawning rougly every 100 ms
            if SCORE <= 260 and SCORE % 10 == 0:
                pygame.time.set_timer(CREATE_FRUIT, int(INTERVAL - SCORE**1.05))
        score.update(SCORE)
        
        screen.fill("black")
        screen.blit(images["shoji"], (0,0))
        
        [
            screen.blit(
                images["heart"],
                (screen.get_width() - images["heart"].get_width() * (i + 1), 10))
                for i in range(LIVES)
        ]

        screen.blit(score.text, score.tRect)
        if timestamp % 2 != 0:    
            fps_display.update(round(clock.get_fps(), 2))
        screen.blit(fps_display.text, fps_display.tRect)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        webcam = pygame.transform.scale_by(pygame.surfarray.make_surface(frame.transpose([1,0,2])), 0.6)
        screen.blit(webcam, (SCREEN_WIDTH-webcam.get_width(), SCREEN_BOTTOM-webcam.get_height()))

        fruits.update()
        fruits.draw(screen)

        katanaGroup.draw(screen)
        katana.create_mask()
        
        sliced.draw(screen)
        sliced.update()

        pygame.display.flip()
        clock.tick(FPS)

    handlandmarker.close()
    pygame.quit()


if __name__ == "__main__":
    main()
