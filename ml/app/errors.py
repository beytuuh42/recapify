class ModelUnavailableError(Exception):
    def __init__(self, code: int, status: str, message: str):
        self.code = code
        self.status = status
        super().__init__(message)


class SubtitleNotFoundError(Exception):
    def __init__(self, title: str, season: int, episode: int, language: str):
        self.title = title
        self.season = season
        self.episode = episode
        self.language = language
        super().__init__(f"No subtitles found for {title} S{season:02d}E{episode:02d} ({language})")
