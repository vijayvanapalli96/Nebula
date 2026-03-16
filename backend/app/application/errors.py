class SessionNotFoundError(ValueError):
    pass


class InvalidChoiceError(ValueError):
    pass


class ThemeNotFoundError(ValueError):
    pass


class StoryGenerationError(RuntimeError):
    pass


class ProjectNotFoundError(ValueError):
    pass


class CompositionNotFoundError(ValueError):
    pass


class PartNotFoundError(ValueError):
    pass


class AssetNotFoundError(ValueError):
    pass


class VideoJobNotFoundError(ValueError):
    pass


class VideoGenerationError(RuntimeError):
    pass
