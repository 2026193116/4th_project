import pygame
import sys
import os

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from audio import AudioManager, SOUNDDEVICE_AVAILABLE
from entities import GameState, WordSpawner
from game_logic import process_shout, try_submit_word, update_words, spawn_word_if_ready
from renderer import Renderer
from video_player import play_video

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
LEVEL_INTRO_VIDEOS = {
    1: "level1.mp4",
    2: "level2.mp4",
    3: "level3.mp4",
    4: "level4.mp4"
}

def get_level_video(level: int) -> str:
    return os.path.join(ASSETS_DIR, LEVEL_INTRO_VIDEOS.get(level, ""))

def main():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join(ASSETS_DIR, "MP_Modern Chic.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("화난 교수에게서 도망쳐라 - 가로형 디펜스 에디션")

    clock = pygame.time.Clock()
    renderer = Renderer(screen)
    audio = AudioManager()
    audio.start()

    state = GameState()
    spawner = WordSpawner()
    last_spawn_time = pygame.time.get_ticks()
    last_log_time = 0

    # 이미지 로드
    try:
        start_img = pygame.image.load(os.path.join(ASSETS_DIR, 'start_screen.png')).convert()
        setup_img = pygame.image.load(os.path.join(ASSETS_DIR, 'setup_screen.png')).convert()
        game_over_img = pygame.image.load(os.path.join(ASSETS_DIR, 'game_over.png')).convert()
        story_img = pygame.image.load(os.path.join(ASSETS_DIR, 'game_story.png')).convert()
        game_clear_img = pygame.image.load(os.path.join(ASSETS_DIR, 'gameclear.png')).convert()
        
        game_bgs = {
            1: {
                1: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_heart1.png')).convert()},
                2: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_heart1.png')).convert()},
                3: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_heart1.png')).convert()},
                4: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_heart1.png')).convert()}
            },
            2: {
                1: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_2_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_2_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_2_heart1.png')).convert()},
                2: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_2_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_2_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_2_heart1.png')).convert()},
                3: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_2_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_2_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_2_heart1.png')).convert()},
                4: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_2_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_2_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_2_heart1.png')).convert()}
            },
            3: {
                1: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_3_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_3_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_3_heart1.png')).convert()},
                2: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_3_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_3_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_3_heart1.png')).convert()},
                3: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_3_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_3_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_3_heart1.png')).convert()},
                4: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_3_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_3_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_3_heart1.png')).convert()}
            },
            4: {
                1: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_4_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_4_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_4_heart1.png')).convert()},
                2: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_4_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_4_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_4_heart1.png')).convert()},
                3: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_4_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_4_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_4_heart1.png')).convert()},
                4: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_4_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_4_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_4_heart1.png')).convert()}
            },
            5: {
                1: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_5_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_5_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage1_5_heart1.png')).convert()},
                2: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_5_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_5_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage2_5_heart1.png')).convert()},
                3: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_5_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_5_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage3_5_heart1.png')).convert()},
                4: {3: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_5_heart3.png')).convert(),
                    2: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_5_heart2.png')).convert(),
                    1: pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_5_heart1.png')).convert()}
            },
        }
        
        char_imgs = {
            "default": pygame.image.load(os.path.join(ASSETS_DIR, 'select_main.png')).convert(),
            1: pygame.image.load(os.path.join(ASSETS_DIR, 'select_1.png')).convert(), 
            2: pygame.image.load(os.path.join(ASSETS_DIR, 'select_2.png')).convert(),
            3: pygame.image.load(os.path.join(ASSETS_DIR, 'select_3.png')).convert(),
            4: pygame.image.load(os.path.join(ASSETS_DIR, 'select_4.png')).convert(),
            5: pygame.image.load(os.path.join(ASSETS_DIR, 'select_5.png')).convert()
        }
        
        start_img = pygame.transform.scale(start_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        setup_img = pygame.transform.scale(setup_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        game_over_img = pygame.transform.scale(game_over_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        story_img = pygame.transform.scale(story_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        game_clear_img = pygame.transform.scale(game_clear_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        for char_idx in game_bgs:
            for stage_idx in game_bgs[char_idx]:
                for hp_idx in game_bgs[char_idx][stage_idx]:
                    game_bgs[char_idx][stage_idx][hp_idx] = pygame.transform.scale(
                        game_bgs[char_idx][stage_idx][hp_idx], (SCREEN_WIDTH, SCREEN_HEIGHT)
                    )
            
        for key in char_imgs:
            char_imgs[key] = pygame.transform.scale(char_imgs[key], (SCREEN_WIDTH, SCREEN_HEIGHT))
            
    except pygame.error as e:
        print(f"⚠️ assets 폴더 안의 이미지 파일들을 다시 확인하세요! 에러 내용: {e}")
        pygame.quit()
        sys.exit()

    start_button_rect = pygame.Rect(350, 350, 400, 110)
    input_box_rect = pygame.Rect(570, 250, 250, 50)
    setup_next_button_rect = pygame.Rect(570, 320, 250, 50) 
    char_start_button_rect = pygame.Rect(365, 480, 270, 60)

    story_button_rect = pygame.Rect(700, 120, 170, 35)
    story_back_button_rect = pygame.Rect(510, 460, 85, 35)

    char_rects = {
        1: pygame.Rect(70, 120, 150, 320),
        2: pygame.Rect(250, 120, 150, 320),
        3: pygame.Rect(430, 120, 150, 320),
        4: pygame.Rect(610, 120, 150, 320),
        5: pygame.Rect(790, 120, 150, 320)
    }

    user_nickname = ""
    input_active = False 
    selected_char = 1 

    try:
        font_input = pygame.font.SysFont("malgungothic", 24, bold=True)
    except:
        font_input = pygame.font.SysFont("Arial", 24, bold=True)

    game_state = "TITLE"
    pending_video_path = None
    post_video_state = None

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                
                if game_state == "SETUP" and input_active:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_nickname = user_nickname[:-1]
                    else:
                        if len(user_nickname) < 8:
                            if event.unicode and event.unicode.isprintable():
                                user_nickname += event.unicode

                elif game_state == "PLAY":
                    if event.key == pygame.K_BACKSPACE:
                        state.backspace_input()
                    elif event.key == pygame.K_RETURN:
                        matched, level_up, final_clear = try_submit_word(state, current_time)
                        if level_up:
                            previous_level = max(1, state.level - 1)
                            pending_video_path = get_level_video(previous_level)
                            post_video_state = "PLAY"
                            game_state = "VIDEO"
                            continue
                        if final_clear:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(os.path.join(ASSETS_DIR, "MP_Big Sound.mp3"))
                            pygame.mixer.music.set_volume(0.5)
                            pygame.mixer.music.play()
                            pending_video_path = get_level_video(state.level)
                            post_video_state = "GAME_CLEAR"
                            game_state = "VIDEO"
                            continue
                    elif event.key == pygame.K_SPACE:
                        state.append_input(" ")
                    else:
                        if event.unicode and event.unicode.isprintable():
                            state.append_input(event.unicode)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if game_state == "TITLE":
                        if start_button_rect.collidepoint(event.pos):
                            game_state = "SETUP"
                    
                    elif game_state == "SETUP":
                        if story_button_rect.collidepoint(event.pos):
                            game_state = "STORY"
                        elif input_box_rect.collidepoint(event.pos):
                            input_active = True
                        elif setup_next_button_rect.collidepoint(event.pos):
                            if user_nickname.strip():
                                game_state = "CHAR_SELECT"
                        else:
                            input_active = False
                            
                    elif game_state == "STORY":
                        if story_back_button_rect.collidepoint(event.pos):
                            game_state = "SETUP"

                    elif game_state == "CHAR_SELECT":
                        for char_id, rect in char_rects.items():
                            if rect.collidepoint(event.pos):
                                selected_char = char_id
                                break
                                
                        if char_start_button_rect.collidepoint(event.pos):
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(os.path.join(ASSETS_DIR, "MP_Battle of Boss.mp3"))
                            pygame.mixer.music.set_volume(0.5)
                            pygame.mixer.music.play(-1)
                            game_state = "PLAY"
                            last_spawn_time = pygame.time.get_ticks()

        if game_state == "TITLE":
            screen.blit(start_img, (0, 0))
            pygame.display.flip()

        elif game_state == "SETUP":
            screen.blit(setup_img, (0, 0))
            text_surface = font_input.render(user_nickname, True, (0, 0, 0))
            screen.blit(text_surface, (input_box_rect.x + 10, input_box_rect.y + (input_box_rect.height - text_surface.get_height()) // 2))
            pygame.display.flip()

        elif game_state == "STORY":
            screen.blit(story_img, (0, 0))
            pygame.display.flip()

        elif game_state == "CHAR_SELECT":
            current_display_char = selected_char
            for char_id, rect in char_rects.items():
                if rect.collidepoint(mouse_pos):
                    current_display_char = char_id
                    break
            screen.blit(char_imgs[current_display_char], (0, 0))
            pygame.display.flip()

        elif game_state == "VIDEO":
            if pending_video_path:
                play_video(screen, pending_video_path)
            state.active_words.clear()
            state.clear_input()
            pending_video_path = None
            next_state = post_video_state or "PLAY"
            post_video_state = None
            if next_state == "PLAY":
                last_spawn_time = pygame.time.get_ticks()
            game_state = next_state
            continue

        elif game_state == "PLAY":
            process_shout(state, audio, current_time)

            # 디버그: 1초마다 mic 상태 로깅
            if current_time - last_log_time > 1000:
                print(f"[DEBUG] SOUNDDEVICE_AVAILABLE={SOUNDDEVICE_AVAILABLE} mic_volume={audio.get_volume():.2f} is_shouting={audio.is_shouting()}")
                last_log_time = current_time
            last_spawn_time = spawn_word_if_ready(
                state, spawner, current_time, last_spawn_time
            )
            update_words(state, current_time)

            if state.game_over:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(os.path.join(ASSETS_DIR, "MP_Sad Trombone.mp3"))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play()
                game_state = "GAME_OVER"

            chosen_bg = None
            if selected_char in [1, 2, 3, 4, 5]:
                current_stage = max(1, min(4, state.level))
                current_lives = max(1, min(3, state.lives))
                chosen_bg = game_bgs[selected_char][current_stage][current_lives]

            renderer.draw_frame(
                state, audio.get_volume(), audio.is_shouting(), current_time,
                custom_bg=chosen_bg, player_name=user_nickname.strip(), selected_char=selected_char
            )
            clock.tick(FPS)

        elif game_state == "GAME_OVER":
            renderer.draw_frame(
                state, audio.get_volume(), audio.is_shouting(), current_time,
                custom_bg=game_over_img, player_name=user_nickname.strip(), selected_char=selected_char
            )
            clock.tick(FPS)

        elif game_state == "GAME_CLEAR":
            renderer.draw_frame(
                state, audio.get_volume(), audio.is_shouting(), current_time,
                custom_bg=game_clear_img, player_name=user_nickname.strip(), selected_char=selected_char
            )
            clock.tick(FPS)

    audio.stop()
    pygame.quit()

if __name__ == "__main__":
    main()