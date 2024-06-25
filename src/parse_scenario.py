from dot_to_frame_parser import DotToFrameParser
from dot_to_trajectory_parser import DotToTrajectoryParser
from frame import Frame
import time
import os
from scenic_script_generator import ScenicScriptGenerator

def parse_scenario(gen):    
    current_directory = os.path.dirname(os.path.abspath(__file__))
    solution_folder = f'{current_directory}/../assets/solutions'
    
    traj_parser = DotToTrajectoryParser(f'{solution_folder}/designSpace.dot')
    
    url_parser_map : dict[str, tuple[DotToFrameParser, Frame]] = dict()
    
    import pygame
    pygame.init()

    screen = pygame.display.set_mode((1500, 500))
    pygame.display.set_caption('Traffic Situations Demo')
    
    frames : list[list[Frame]] = []
    for i, solution in enumerate(traj_parser.solutions):
        frames.append([])
        for frame_info in solution:
            if frame_info[0] in url_parser_map:
                parser = url_parser_map[frame_info[0]][0]
                frame = url_parser_map[frame_info[0]][1]
            else:
                parser = DotToFrameParser(f'{solution_folder}/{frame_info[0]}')
                frame = Frame(frame_info[0], parser, screen, frame_info[1])
                url_parser_map[frame_info[0]] = (parser, frame)
            frames[-1].append(frame)
        if gen:
            ScenicScriptGenerator([frame.car_frames for frame in frames[-1]], frames[-1][0].road_length, f'solution{i}.scenic')    
        print(f'Solution {len(frames)} done.')
        
    if gen:
        return


    sol_num = len(frames)
    
    frame_counter = 0
    sol_counter = 0
    frames[sol_counter][frame_counter].draw(screen, frame_counter, len(frames[sol_counter]), sol_counter, sol_num)
    pygame.display.flip()

    running = True
    start_time = None
    playback = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

                
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_time = time.time()
                last_event = event
            elif event.type == pygame.MOUSEBUTTONUP:
                playback = False
                start_time = None                   
                frame_counter += refresh_frame_counter(event, frames[sol_counter], frame_counter)
                frames[sol_counter][frame_counter].draw(screen, frame_counter, len(frames[sol_counter]), sol_counter, sol_num)
                pygame.display.flip()
            elif event.type == pygame.KEYUP:
                sol_counter += refresh_sol_counter(event, frames, sol_counter)
                frame_counter = 0
                frames[sol_counter][frame_counter].draw(screen, frame_counter, len(frames[sol_counter]), sol_counter, sol_num)
                pygame.display.flip()
                
        if start_time is not None and (time.time() - start_time) >= 0.5:
            playback = True
        if playback and (time.time() - start_time) >= 0.35:
            frame_counter += refresh_frame_counter(last_event, frames[sol_counter], frame_counter)
            frames[sol_counter][frame_counter].draw(screen, frame_counter, len(frames[sol_counter]), sol_counter, sol_num)
            pygame.display.flip()
            start_time = time.time()
                
    pygame.quit()
    
def refresh_frame_counter(event, frames, counter):
    if event.button == 1:
        if counter < len(frames) - 1:
            return 1
    elif event.button == 3:
        if counter > 0:
            return -1    
    return 0

def refresh_sol_counter(event, sols, counter):
    import pygame
    if event.key == pygame.K_RIGHT:
        if counter < len(sols) - 1:
            return 1
    elif event.key == pygame.K_LEFT:
        if counter > 0:
            return -1    
    return 0

