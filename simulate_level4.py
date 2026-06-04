"""
Level 4 클리어 시뮬레이션 파일
- 이 파일은 main.py와 독립적으로 실행됨
- level 4의 클리어 메커니즘을 테스트하기 위한 파일
- 단어 풀에서 문장 하나만 입력하면 바로 클리어 화면으로 넘어감
"""

import pygame
import sys
import os

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, YELLOW, RED, 
    LEVEL_WORD_POOLS, MAX_LEVEL, BOSS_X
)
from entities import GameState, WordSpawner, Word
from renderer import Renderer
from game_logic import try_submit_word, update_words, spawn_word_if_ready
from video_player import play_video

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

def simulate_level4():
    """Level 4 클리어 시뮬레이션"""
    
    pygame.init()
    pygame.mixer.init()
    
    # 배경 음악 로드 및 재생
    try:
        pygame.mixer.music.load(os.path.join(ASSETS_DIR, "MP_Battle of Boss.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"⚠️ 배경 음악 로드 실패: {e}")
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("[SIM] Level 4 클리어 테스트")
    
    clock = pygame.time.Clock()
    renderer = Renderer(screen)
    
    # GameState 초기화 및 Level 4로 설정
    state = GameState()
    state.level = MAX_LEVEL  # Level 4로 설정
    state.lives = 3  # 풀 생명
    
    # Level 4의 next_level_target 계산
    # level_up 로직: next_level_target += 10 + (level * 5)
    # 따라서 level 1: 10, level 2: 10 + 20 = 30, level 3: 30 + 25 = 55, level 4: 55 + 30 = 85
    state.next_level_target = 85
    state.words_cleared = 84  # 1문장만 입력하면 클리어
    
    # Level 4 배경 이미지 로드 (character 1, stage 4, hearts 3)
    game_clear_img = None
    game_bg_img = None
    try:
        game_bg_img = pygame.image.load(os.path.join(ASSETS_DIR, 'stage4_heart3.png')).convert()
        game_bg_img = pygame.transform.scale(game_bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        print("✅ stage4_heart3.png 로드 완료")
    except Exception as e:
        print(f"⚠️ stage4_heart3.png를 로드하지 못했습니다: {e}")
        # 로드 실패시 회색 배경으로 처리
        game_bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        game_bg_img.fill((50, 50, 50))
    
    try:
        game_clear_img = pygame.image.load(os.path.join(ASSETS_DIR, 'gameclear.png')).convert()
        game_clear_img = pygame.transform.scale(game_clear_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        print("✅ gameclear.png 로드 완료")
    except Exception as e:
        print(f"⚠️ gameclear.png를 로드하지 못했습니다: {e}")
    
    # Level 4 단어 풀에서 몇 개의 단어 스폰 (화면에 표시할 용)
    spawner = WordSpawner()
    for i in range(5):
        word = spawner.spawn(state.level, state.active_words)
        state.active_words.append(word)
    
    # Level 4 단어 풀 표시
    level_4_words = LEVEL_WORD_POOLS[4]
    print(f"\n🎮 Level 4 클리어 시뮬레이션 시작")
    print(f"📋 Level 4 단어 풀 ({len(level_4_words)}개):")
    for i, word in enumerate(level_4_words, 1):
        print(f"   {i}. {word}")
    print(f"\n💡 위의 단어 중 하나를 정확하게 입력하세요.")
    print(f"   현재 상태: words_cleared = {state.words_cleared}, next_level_target = {state.next_level_target}")
    print(f"   1문장만 더 입력하면 LEVEL 4 CLEAR! 🎉\n")
    
    # 게임 루프
    running = True
    game_cleared = False
    game_state = "PLAY"  # PLAY 또는 CLEAR
    last_spawn_time = pygame.time.get_ticks()
    pending_video_path = None
    
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_RETURN:
                    # 입력된 단어 제출
                    print(f"📝 입력: '{state.current_input}'")
                    matched, leveled_up, final_clear = try_submit_word(state, current_time)
                    
                    if matched:
                        print(f"✅ 맞았습니다!")
                        print(f"   words_cleared: {state.words_cleared}")
                        print(f"   level: {state.level}")
                        print(f"   final_level_cleared: {state.final_level_cleared}")
                        
                        if final_clear:
                            # 클리어 음악 변경 및 비디오 준비
                            pygame.mixer.music.stop()
                            try:
                                pygame.mixer.music.load(os.path.join(ASSETS_DIR, "MP_Big Sound.mp3"))
                                pygame.mixer.music.set_volume(0.5)
                                pygame.mixer.music.play()
                            except Exception as e:
                                print(f"⚠️ 클리어 음악 로드 실패: {e}")
                            
                            # 비디오 경로 설정
                            pending_video_path = os.path.join(ASSETS_DIR, "level4.mp4")
                            game_state = "VIDEO"
                            print(f"🎬 비디오 재생 준비: {pending_video_path}")
                    else:
                        print(f"❌ 단어를 찾을 수 없습니다. 다시 시도하세요.")
                        print(f"   현재 입력: {state.current_input}")
                
                elif event.key == pygame.K_BACKSPACE:
                    state.backspace_input()
                
                elif event.unicode.isprintable():
                    state.append_input(event.unicode)
        
        # 게임 업데이트: 단어 스폰 및 이동
        last_spawn_time = spawn_word_if_ready(
            state, spawner, current_time, last_spawn_time
        )
        update_words(state, current_time)
        
        # 상태별 렌더링
        if game_state == "VIDEO":
            # 비디오 재생
            if pending_video_path:
                print(f"🎬 비디오 재생 중...")
                play_video(screen, pending_video_path)
                pending_video_path = None
                game_state = "CLEAR"
                print(f"\n🎉 LEVEL 4 CLEAR! 🎉")
                print(f"최종 스코어: {state.score}")
        
        elif game_state == "CLEAR":
            # 클리어 화면
            state.game_over = True
            renderer.draw_frame(
                state, 0.0, False, current_time,
                custom_bg=game_clear_img, player_name="[SIM] Player", selected_char=1
            )
        
        else:  # game_state == "PLAY"
            # 게임 진행 중: renderer를 사용하여 main과 동일하게 표시
            renderer.draw_frame(
                state, 0.0, False, current_time,
                custom_bg=game_bg_img, player_name="[SIM] Player", selected_char=1
            )
        
        clock.tick(FPS)
    
    pygame.mixer.music.stop()
    pygame.quit()
    print("\n👋 시뮬레이션 종료")

if __name__ == "__main__":
    simulate_level4()
