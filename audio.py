import numpy as np
from config import DB_THRESHOLD, MIC_DB_MULTIPLIER, MIC_DB_OFFSET

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except (ImportError, OSError):
    SOUNDDEVICE_AVAILABLE = False

class AudioManager:
    """마이크 입력을 관리하고 볼륨(RMS)을 계산하는 클래스"""

    def __init__(self, threshold: float = DB_THRESHOLD):
        self.threshold = threshold
        self.mic_volume = 0.0
        self._stream = None

    def _audio_callback(self, indata, frames, time, status):
        """sounddevice 콜백: RMS 볼륨 계산"""
        # 정확한 RMS 계산: 모든 샘플(및 채널)을 제곱하여 평균한 뒤 제곱근을 취합니다.
        try:
            arr = np.asarray(indata, dtype=np.float64)
            linear_rms = float(np.sqrt(np.mean(np.square(arr))))
        except Exception:
            linear_rms = np.linalg.norm(indata) / np.sqrt(len(indata))

        # 기본 RMS를 0~100 스케일로 바꾼 뒤, 사용자 설정 배율/오프셋을 적용하여
        # 게임 내에서 사용하는 'dB 유사' 값으로 매핑합니다.
        self.mic_volume = (linear_rms * 100.0) * MIC_DB_MULTIPLIER + MIC_DB_OFFSET

    def start(self):
        """오디오 스트림 시작"""
        if SOUNDDEVICE_AVAILABLE:
            self._stream = sd.InputStream(callback=self._audio_callback)
            self._stream.start()

    def stop(self):
        """오디오 스트림 정지 및 종료"""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def is_shouting(self) -> bool:
        """현재 볼륨이 설정된 임계값 이상인지 반환
        임계값과 같을 때도 소리치기로 간주합니다 (>=).
        """
        return self.mic_volume >= self.threshold

    def get_volume(self) -> float:
        """현재 마이크 볼륨 반환"""
        return self.mic_volume

    def set_volume(self, volume: float):
        """테스트용: 볼륨을 수동으로 설정"""
        self.mic_volume = volume

    @staticmethod
    def compute_rms(indata: np.ndarray) -> float:
        """
        입력 오디오 데이터에서 RMS 값을 계산하여 0~100 스케일로 반환.
        """
        if len(indata) == 0:
            return 0.0
        try:
            arr = np.asarray(indata, dtype=np.float64)
            linear_rms = float(np.sqrt(np.mean(np.square(arr))))
        except Exception:
            linear_rms = np.linalg.norm(indata) / np.sqrt(len(indata))

        return (linear_rms * 100.0) * MIC_DB_MULTIPLIER + MIC_DB_OFFSET