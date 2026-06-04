import sys
import io

# Windows 환경에서 유니코드 이모지 출력 시 cp949 인코딩 에러 방지
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from entities import GameState, WordSpawner, Word
from audio import AudioManager
from config import PLAYER_X, SHOUT_PUSH_BASE, SHOUT_COOLDOWN, SHOUT_PUSH_MULTIPLIER

def process_shout(state: GameState, audio: AudioManager, current_time: int):
    """
    소리치기 처리 (쿨타임 포함):
    - `audio.is_shouting()`이 True이면 일반 단어들만 뒤로 밀어냅니다.
    - 한 번 소리쳐서 밀어낸 뒤 `SHOUT_COOLDOWN` 기간 동안은 추가 밀침이 발생하지 않습니다.
    """
    # 쿨타임이 활성화되어 있으면 경과 확인
    if state.is_cooling_down:
        if current_time - state.last_shout_success_time >= SHOUT_COOLDOWN:
            state.is_cooling_down = False
        else:
            return

    if audio.is_shouting():
        # 레벨에 비례하여 밀어내는 파워가 증가합니다.
        push_amount = (SHOUT_PUSH_BASE + state.level) * SHOUT_PUSH_MULTIPLIER
        pushed_count = 0
        print(f"[SHOUT] mic={audio.get_volume():.2f} threshold={audio.threshold} push_amount={push_amount} active_words={len(state.active_words)}")
        for idx, w in enumerate(state.active_words):
            # 일반 단어만 뒤로 밀려나고, 무거운(heavy) 단어는 면역 상태가 되어 밀리지 않습니다.
            if not w.is_heavy:
                before_x = w.x
                w.push_back(push_amount)
                pushed_count += 1
                if idx < 5:
                    print(f"  pushed word='{w.text}' idx={idx} before_x={before_x:.1f} after_x={w.x:.1f} is_heavy={w.is_heavy}")

        print(f"[SHOUT] pushed_count={pushed_count}")

        if pushed_count > 0:
            state.last_shout_success_time = current_time
            state.is_cooling_down = True

def try_submit_word(state: GameState, current_time: int) -> tuple[bool, bool, bool]:
    matched = False
    leveled_up = False
    final_clear = False
    for w in state.active_words[:]:
        if w.matches(state.current_input):
            state.active_words.remove(w)
            state.add_score(100)
            leveled_up = state.check_level_up(current_time)
            if not leveled_up:
                final_clear = state.check_final_clear()
            matched = True
            break
    state.clear_input()
    return matched, leveled_up, final_clear

def update_words(state: GameState, current_time: int):
    if state.game_over:
        return

    removable_words = []
    for word in state.active_words:
        # 단어 고유의 속도 및 사인파 움직임 업데이트
        word.update(current_time)
        
        # 단어가 좌측 플레이어 캐릭터 방어선(X=90 이하)까지 도달했는지 판정
        if word.x <= 90:
            removable_words.append(word)
            state.lives -= 1
            
            print(f"⚠️ 단어가 방어선을 돌파했습니다! 남은 목숨: {state.lives}")
            
            if state.lives <= 0:
                state.game_over = True
                print("🚨 LIVES EXHAUSTED. GAME OVER!")

    for word in removable_words:
        if word in state.active_words:
            state.active_words.remove(word)

def spawn_word_if_ready(state: GameState, spawner: WordSpawner,
                        current_time: int, last_spawn_time: int) -> int:
    delay = spawner.get_spawn_delay(state.level)
    
    if current_time - last_spawn_time > delay:
        word = spawner.spawn(state.level, state.active_words)
        state.active_words.append(word)
        return current_time  
        
    return last_spawn_time