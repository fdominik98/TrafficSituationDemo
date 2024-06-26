from dot_to_frame_parser import DotToFrameParser
import pygame
from pygame import Surface
from pygraphviz import Node
import os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREY = (130, 130, 130)
ORANGE = (199, 80, 0)
DARK_GREY = (99, 99, 99)

MARGIN_WIDTH : float = 2
MARGIN_HEIGHT : float = 50

CELL_WIDTH = 74.8
CELL_HEIGHT = 48.888

CAR_WIDTH = CELL_WIDTH / 1
CAR_HEIGHT = CELL_HEIGHT / 1.1

TEXT_HEIGHT : float = 30    

current_directory = os.path.dirname(os.path.abspath(__file__))

class CellFrame:
    road_image = pygame.image.load(f'{current_directory}/../assets/images/road.png')
    road_line_image = pygame.image.load(f'{current_directory}/../assets/images/road_line.png')
    
    def __init__(self, parser : DotToFrameParser, cell : Node, cell_pos : tuple[float, float], abs_pos : tuple[int, int]) -> None:
        self.parser = parser
        self.cell = cell
        self.pos = cell_pos
        self.abs_pos = abs_pos
        self.is_intermediate = parser.is_intermediate(self.cell)
        self.size = (CELL_WIDTH, CELL_HEIGHT)     
        
        image_size = (self.size[0] + 1, self.size[1] + 1)
        self.road_image = pygame.transform.scale(self.road_image, image_size)
        self.road_line_image = pygame.transform.scale(self.road_line_image, image_size)
        
        
    def draw(self, screen : Surface):
        margined_pos = (MARGIN_WIDTH + self.pos[0], MARGIN_HEIGHT + self.pos[1])
        rect = pygame.Rect(margined_pos[0], margined_pos[1], self.size[0], self.size[1])
        if self.is_intermediate:
            screen.blit(self.road_line_image, margined_pos)
        else:
            screen.blit(self.road_image, margined_pos)
        #pygame.draw.rect(screen, GREY, rect, 1)

class CarFrame:    
    ego_image = pygame.image.load(f'{current_directory}/../assets/images/ego.png')
    car_image = pygame.image.load(f'{current_directory}/../assets/images/car.png')
    
    def __init__(self, parser : DotToFrameParser, car : Node, cell_frame : CellFrame) -> None:
        self.parser = parser
        self.car = car
        self.cell_frame = cell_frame
        self.size = (CAR_WIDTH, CAR_HEIGHT)     
        self.is_ego = self.car in self.parser.ego_cars
        self.is_forward = parser.is_forward(self.car)
        self.color = DotToFrameParser.get_car_color(self.car)
        self.name = 'ego' if self.is_ego else f'car{car}' 
        self.blueprint = 'vehicle.mini.cooper_s' if self.is_ego else 'vehicle.nissan.micra'
        self.blueprint = 'vehicle.mini.cooper_s'
        
        if self.is_ego:
            self.image = self.ego_image
        else:
            self.image = self.car_image
        if not self.is_forward:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def draw(self, screen : Surface):
        rect_size = (self.size[0] / 3, self.size[1] / 3)
        rect_pos = self.get_center_pos(rect_size)       
        image_pos = self.get_center_pos(self.size)    
        self.image = pygame.transform.scale(self.image, self.size)
        screen.blit(self.image, image_pos)   
        rect = pygame.Rect(rect_pos[0], rect_pos[1], rect_size[0], rect_size[1])
        pygame.draw.rect(screen, self.color, rect)
        
    def get_center_pos(self, size):
        return (MARGIN_WIDTH + self.cell_frame.pos[0] + self.cell_frame.size[0] / 2 - size[0] / 2,
                MARGIN_HEIGHT + self.cell_frame.pos[1] + self.cell_frame.size[1] / 2 - size[1] / 2)

class Frame():     
    def __init__(self, file : str, parser: DotToFrameParser, screen : Surface, weight) -> None:
        self.weight = weight
        self.file = file
        screen_height = len(parser.cells) * CELL_HEIGHT
        
        screen.fill(GREY) 
        
        car_frames : set[CarFrame] = set()      
        self.state_tokens = parser.state_tokens  
        
        cell_pos = (0.0, 0.0)
        for y, row in enumerate(parser.cells):
            for x, cell in enumerate(row):
                cell_frame = CellFrame(parser, cell, cell_pos, (y, x))
                cell_pos = (cell_frame.pos[0] + cell_frame.size[0], cell_pos[1])
                cell_frame.draw(screen)                
                if cell in parser.car_cells:
                    car_frames.add(CarFrame(parser, parser.car_cells[cell], cell_frame))
            cell_pos = (0.0, cell_frame.pos[1] + cell_frame.size[1])
        self.road_length = len(parser.cells[0])
            
        pygame.draw.line(screen, WHITE, (0, MARGIN_HEIGHT - 15), (screen.get_width(), MARGIN_HEIGHT -15), 20)  
        pygame.draw.line(screen, DARK_GREY, (0, MARGIN_HEIGHT), (screen.get_width(), MARGIN_HEIGHT), 10)
        
        pygame.draw.line(screen, WHITE, (0, screen_height + MARGIN_HEIGHT + 15),
                         (screen.get_width(), screen_height + MARGIN_HEIGHT + 15), 20)
        pygame.draw.line(screen, DARK_GREY, (0, screen_height + MARGIN_HEIGHT),
                         (screen.get_width(), screen_height + MARGIN_HEIGHT), 10)
                    
        for car_frame in car_frames:
            car_frame.draw(screen)
                 
        self.screenshot = screen.copy()
        self.car_frames = car_frames
                  
        
    def draw(self, screen : Surface, frame_id, frame_num, sol_id, sol_num):
        print('______________________________________________')
        for state in self.state_tokens:
            print(f'{state}')
        text_rect = pygame.Rect(0, screen.get_height() - TEXT_HEIGHT, screen.get_width(), TEXT_HEIGHT)
        self.screenshot.fill(BLACK, text_rect)
        status = f' frame : {frame_id + 1}/{frame_num},   objective value: {self.weight:.3f},   solution : {sol_id + 1}/{sol_num},   file: {self.file}'
        self.draw_text(status, WHITE, self.screenshot, text_rect)
        screen.blit(self.screenshot, (0, 0))
        
    def draw_text(self, text, color, screen : Surface, rect : pygame.Rect):
        font = pygame.font.Font(None, 25)
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        text_rect.center = rect.center
        screen.blit(text_obj, text_rect)
        
          
        

        
                