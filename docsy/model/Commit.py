from dataclasses import dataclass

@dataclass
class Commit:
    sha: str
    message: str
    diff: str

    def __str__(self):
        return f"{self.sha[:7]} - {self.message} - {self.diff}"
