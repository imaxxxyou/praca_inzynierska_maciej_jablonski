import sys
import time
import pyautogui
import pygame

def logo_animation():
    # Zrób zrzut ekranu jako tło
    screenshot = pyautogui.screenshot()
    screenshot = pygame.image.fromstring(screenshot.tobytes(), screenshot.size, screenshot.mode)

    pygame.init()

    # Ustawienia ekranu
    screen_info = pygame.display.Info()
    window_size = (screen_info.current_w, screen_info.current_h)
    screen = pygame.display.set_mode(window_size, pygame.FULLSCREEN)
    pygame.display.set_caption("")

    screenshot = pygame.transform.scale(screenshot, window_size)

    # Ustawienia logo
    logo_image = pygame.image.load("logoHS.png")
    logo_rect = logo_image.get_rect()

    # Początkowe rozmiary i pozycja logo
    logo_width, logo_height = 2, 2
    logo_x, logo_y = (window_size[0] - logo_width) // 2, (window_size[1] - logo_height) // 2

    # Rozpocznij animację
    clock = pygame.time.Clock()
    fps = 60
    scale_speed = 10

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(screenshot, (0, 0))  # Rysuj zrzut ekranu jako tło

        # Powiększanie logo
        logo_width += scale_speed
        logo_height += scale_speed

        # Ustaw nowe rozmiary logo
        logo_image_scaled = pygame.transform.scale(logo_image, (logo_width, logo_height))
        logo_rect = logo_image_scaled.get_rect(center=(window_size[0] // 2, window_size[1] // 2))

        # Rysuj logo
        screen.blit(logo_image_scaled, logo_rect.topleft)

        pygame.display.flip()
        clock.tick(fps)

        # Zatrzymaj animację po osiągnięciu docelowych rozmiarów
        if logo_width >= 500 and logo_height >= 300:
            break

    time.sleep(1)  # Poczekaj przed zamknięciem
    pygame.quit()


if __name__ == "__main__":
    logo_animation()