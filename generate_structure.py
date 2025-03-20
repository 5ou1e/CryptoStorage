import os
from typing import List, Set


class FolderStructureGenerator:
    def __init__(
        self,
        excluded_dirs: Set[str] = None,
        excluded_files: Set[str] = None,
    ):
        self.excluded_dirs = excluded_dirs or {
            "__pycache__",
            ".mypy_cache",
            ".git",
            ".venv",
            "venv",
            ".idea",
            ".pytest_cache",
            "postgres",
            "migrations",
            "etl",
            "frontend",
            "nginx",
            "admin",
            "sql_queries",
            "tests"
        }
        self.excluded_files = excluded_files or {".DS_Store", ".gitignore"}

    def generate(self, directory: str, prefix: str = "") -> List[str]:
        tree_lines = []
        entries = sorted(
            e for e in os.listdir(directory) if e not in self.excluded_dirs and e not in self.excluded_files
        )

        for i, entry in enumerate(entries):
            path = os.path.join(directory, entry)
            connector = "└── " if i == len(entries) - 1 else "├── "
            tree_lines.append(prefix + connector + entry)

            if os.path.isdir(path):
                tree_lines.extend(self.generate(path, prefix + ("    " if i == len(entries) - 1 else "│   ")))

        return tree_lines


if __name__ == "__main__":
    project_dir = "backend"  # Задайте корневую папку проекта
    generator = FolderStructureGenerator()
    tree_output = generator.generate(project_dir)

    print("\n".join(tree_output))
