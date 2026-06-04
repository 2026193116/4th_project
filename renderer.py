import pygame
import sys
import os

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, YELLOW, RED, GREEN, SHOUT_COOLDOWN

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        try:
            self.font = pygame.font.SysFont("malgungothic", 24, bold=True)
            self.ui_font = pygame.font.SysFont("malgungothic", 20, bold=True)
        except:
            self.font = pygame.font.SysFont("Arial", 24, bold=True)
            self.ui_font = pygame.font.SysFont("Arial", 20, bold=True)

        self.background_images = {}
        
    def draw_frame(self, state, mic_volume: float, is_shouting: bool, 
                   current_time: int, custom_bg=None, player_name="", selected_char=1):
        if custom_bg:
            self.screen.blit(custom_bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0)) 

        if state.game_over:
            pygame.display.flip()
            return

        # 단어들 그리기
        for word in state.active_words:
            if word.is_heavy:
                display_text = word.text
                text_color = YELLOW
            else:
                display_text = word.text
                text_color = WHITE
                
            word_surface = self.font.render(display_text, True, text_color)
            self.screen.blit(word_surface, (word.x, word.y))

        self._draw_ui(state, current_time)
        # 마이크 게이지 그리기
        self._draw_mic_bar(mic_volume, is_shouting)
        # 플레이어 닉네임 그리기
        self._draw_player_name(player_name)

        # 레벨업 텍스트 효과
        if current_time - state.level_up_time < 2000 and state.level_up_time > 0:
            lvl_text = self.font.render(f"STAGE {state.level} START!!", True, YELLOW)
            text_rect = lvl_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(lvl_text, text_rect)

        pygame.display.flip()

    def _draw_ui(self, state, current_time: int):
        score_text = self.ui_font.render(f"SCORE: {state.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        lives_string = "♥ " * max(0, state.lives) if state.lives > 0 else "☠️"
        lives_text = self.ui_font.render(f"LIVES: {lives_string}", True, RED)
        lives_rect = lives_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        self.screen.blit(lives_text, lives_rect)
        
        if state.current_input:
            input_text = self.font.render(state.current_input, True, GREEN)
            input_rect = input_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(input_text, input_rect)

        # 쿨타임 표시: 사운드바(왼쪽 상단)와 목숨(오른쪽 상단) 사이 중앙에 배치
        try:
            if state.is_cooling_down:
                elapsed = current_time - state.last_shout_success_time
                remaining_ms = max(0, SHOUT_COOLDOWN - elapsed)
                remaining_s = remaining_ms / 1000.0
                cd_text = self.ui_font.render(f"SHOUT COOLDOWN: {remaining_s:.1f}s", True, YELLOW)
                cd_rect = cd_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
                self.screen.blit(cd_text, cd_rect)
        except Exception:
            pass

    def _draw_mic_bar(self, mic_volume: float, is_shouting: bool):
        """좌측 상단에 마이크 입력 세기를 그립니다."""
        bar_x = 20
        bar_y = 60
        bar_width = 200
        bar_height = 15

        # 기본 배경 회색 막대 프레임
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

        # ⭐ [수정]: 내 소리가 80dB일 때 회색 막대를 가득 채우도록 스케일 조정 (mic_volume / 80.0)
        fill_width = int((mic_volume / 80.0) * bar_width)
        
        # ⭐ [수정]: 80dB보다 커지더라도 회색 막대(bar_width) 범위 밖으로 삐져나가지 않도록 엄격히 차단
        fill_width = max(0, min(fill_width, bar_width))

        # 75dB 이상(is_shouting) 상태면 빨간색, 평상시면 초록색 게이지 출력
        color = RED if is_shouting else GREEN
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height))

        # 바 테두리선 추가
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

        # 현재 mic 볼륨 숫자로 표시
        try:
            mic_text = self.ui_font.render(f"{mic_volume:.1f} dB", True, WHITE)
            self.screen.blit(mic_text, (bar_x + bar_width + 8, bar_y - 2))
        except Exception:
            pass

    def _draw_player_name(self, player_name: str):
        """왼쪽 캐릭터 아래에 플레이어 닉네임을 그립니다."""
        if not player_name:
            return
        
        # 왼쪽 아래 영역에 닉네임 표시
        name_text = self.font.render(player_name, True, WHITE)
        name_x = 20
        name_y = SCREEN_HEIGHT - 60
        self.screen.blit(name_text, (name_x, name_y))