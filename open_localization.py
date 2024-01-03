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


def main(values):
    ''' funkcja pobiera wspolrzedne polozenia produktu x i y'''
    print("VALUES:", values)
    import main
    server, db, user, password = main.dbConnectFiles()

    database = main.Database(server=server,
                            database=db,
                            username=user,
                            password=password)

    query = database.execute_query(query=f"SELECT x,y FROM dbo.Lokalizacja_Produktu WHERE id_produktu = {values[0]}")
    x = query[0][0]
    y = query[0][1]
    pygame.init()

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Lokalizacja w magazynie')

    background = pygame.image.load('mag_viz.png')
    background = pygame.transform.scale(background, (width, height))

    clock = pygame.time.Clock()

    pulsating_point = PulsatingPoint(x, y)

    ok_button_rect = pygame.Rect(width - 100, height - 50, 80, 40)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if ok_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    return 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return 0

        pulsating_point.update()

        screen.blit(background, (0, 0))

        pulsating_point.draw(screen)

        font = pygame.font.Font(None, 36)
        text = font.render(f'Produkt: {values[1]}  ({pulsating_point.x}, {pulsating_point.y})', True, (255, 255, 255))
        screen.blit(text, (10, height - 50))

        pygame.draw.rect(screen, (0, 100, 0), ok_button_rect)
        font = pygame.font.Font(None, 36)
        text = font.render('OK', True, (255, 255, 255))
        screen.blit(text, (width - 90, height - 40))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
