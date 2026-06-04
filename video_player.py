import os
import sys
import subprocess


def play_video(screen, video_path: str) -> None:
    video_path = os.path.abspath(video_path)
    if not os.path.isfile(video_path):
        print(f"[VIDEO] 파일을 찾을 수 없습니다: {video_path}")
        return

    if _can_play_with_opencv() and _can_use_pygame():
        _play_video_with_opencv(screen, video_path)
    else:
        _play_video_with_system_player(video_path)


def _can_play_with_opencv() -> bool:
    try:
        import cv2  # type: ignore
        return True
    except ImportError:
        return False


def _can_use_pygame() -> bool:
    try:
        import pygame  # type: ignore
        return True
    except ImportError:
        return False


def _play_video_with_opencv(screen, video_path: str) -> None:
    import cv2  # type: ignore
    import pygame  # type: ignore

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[VIDEO] OpenCV로 동영상을 열 수 없습니다: {video_path}")
        return

    screen_width, screen_height = screen.get_size()
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or fps != fps:
        fps = 25.0

    clock = pygame.time.Clock()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception:
            break

        frame = cv2.resize(frame, (screen_width, screen_height))
        surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        screen.blit(surface, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                cap.release()
                return

        clock.tick(fps)

    cap.release()


def _play_video_with_system_player(video_path: str) -> None:
    print(f"[VIDEO] OpenCV가 설치되지 않아 기본 플레이어로 동영상을 실행합니다: {video_path}")
    try:
        if sys.platform.startswith("win"):
            subprocess.run(f'start "" /WAIT "{video_path}"', shell=True)
        elif sys.platform == "darwin":
            subprocess.run(["open", video_path])
        else:
            subprocess.run(["xdg-open", video_path])
    except Exception as exc:
        print(f"[VIDEO] 동영상 실행에 실패했습니다: {exc}")
