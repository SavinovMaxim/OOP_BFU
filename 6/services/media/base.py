from .abstract import AbstractMediaPlayer
from services.output.abstract import AbstractOutputService


class MediaPlayer(AbstractMediaPlayer):
    def __init__(self, output_service: AbstractOutputService):
        self.__is_playing = False
        self.__output_service = output_service

    @property
    def is_playing(self):
        return self.__is_playing

    def play(self):
        if not self.is_playing:
            self.__is_playing = True
            message = "Playing media"
            self.__output_service.message(message)
            # return
        # raise Exception("Media already playing")

    def stop(self):
        if self.is_playing:
            self.__is_playing = False
            message = "Stopped media"
            self.__output_service.message(message)
            # return
        # raise Exception("Media already stopped")

