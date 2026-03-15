class SessionNotFoundError(ValueError):
    pass


class InvalidChoiceError(ValueError):
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
