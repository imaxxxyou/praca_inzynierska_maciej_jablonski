import pygame
import sys

class PulsatingPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.max_radius = 20
        self.min_radius = 5
        self.growing = True

    def update(self):
        if self.growing:
            self.radius += 1
            if self.radius >= self.max_radius:
                self.growing = False
        else:
            self.radius -= 1
            if self.radius <= self.min_radius:
                self.growing = True

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), self.radius)


def main(x,y):
    pygame.init()

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Lokalizacja w magazynie')

    # Wczytaj obraz tła
    background = pygame.image.load('mag_viz.png')
    background = pygame.transform.scale(background, (width, height))

    clock = pygame.time.Clock()

    # Zmienic kordynaty podczas wyswietlania lokalizacji
    pulsating_point = PulsatingPoint(x, y)

    ok_button_rect = pygame.Rect(width - 100, height - 50, 80, 40)

    is_setting_position = False  # Flaga wskazująca, czy aktualnie ustawiamy pozycję pulsującego punktu

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                coordinates_message = pulsating_point.x, pulsating_point.y
                print("Koordynaty:", coordinates_message, type(coordinates_message))
                return coordinates_message
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if ok_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    coordinates_message = pulsating_point.x, pulsating_point.y
                    print("Koordynaty:", coordinates_message, type(coordinates_message))
                    return coordinates_message
                else:
                    is_setting_position = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                is_setting_position = False

            elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    if event.key == pygame.K_RETURN:
                        pygame.quit()
                        coordinates_message = pulsating_point.x, pulsating_point.y
                        print("Koordynaty:", coordinates_message, type(coordinates_message))
                        return coordinates_message

        if is_setting_position:
            pulsating_point.x, pulsating_point.y = pygame.mouse.get_pos()

        keys = pygame.key.get_pressed()
        pulsating_point.update()

        # Ustaw tło
        screen.blit(background, (0, 0))

        pulsating_point.draw(screen)

        # Wyświetl aktualne współrzędne w lewym dolnym rogu
        font = pygame.font.Font(None, 36)
        text = font.render(f'Zaznacz położenie produktu: ({pulsating_point.x}, {pulsating_point.y})', True, (255, 255, 255))
        screen.blit(text, (10, height - 50))

        # Narysuj przycisk OK
        pygame.draw.rect(screen, (0, 100, 0), ok_button_rect)  # Zielony kolor
        font = pygame.font.Font(None, 36)
        text = font.render('OK', True, (255, 255, 255))
        screen.blit(text, (width - 90, height - 40))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
