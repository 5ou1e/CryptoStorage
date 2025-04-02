from dataclasses import dataclass


@dataclass(eq=False)
class RepositoryException(Exception):
    title: str = None

    def __str__(self):
        return self.title
