

import os
from pathlib import Path
from typing import List, Set

class DirectoryWatcher:
    def __init__(self, directory: str):
        """
        Инициализация наблюдателя за директорией
        
        :param directory: Путь к директории для наблюдения
        """
        self.directory = Path(directory)
        self._known_files: Set[str] = set()
        
        # Создаем директорию, если она не существует
        self.directory.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем список известных файлов
        # self._update_known_files()
    
    def _update_known_files(self) -> None:
        """Обновляет внутренний список известных файлов"""
        current_files = {f.name for f in self.directory.glob('*') if f.is_file()}
        self._known_files.update(current_files)
    
    def get_new_files(self) -> List[str]:
        """
        Возвращает список новых файлов, появившихся с последнего вызова
        
        :return: Список имен новых файлов
        """
        current_files = {f.name for f in self.directory.glob('*') if f.is_file()}
        new_files = current_files - self._known_files
        
        # Обновляем список известных файлов
        self._known_files = current_files
        
        return sorted(list(new_files))
    
    def get_all_files(self) -> List[str]:
        """
        Возвращает список всех файлов в директории
        
        :return: Список имен всех файлов
        """
        return sorted([f.name for f in self.directory.glob('*') if f.is_file()])
    
    def clear_known_files(self) -> None:
        """Очищает историю известных файлов"""
        self._known_files = set()

if __name__=="__main__":
    dw = DirectoryWatcher('.')
    print(dw.get_new_files())
    print(dw.get_new_files())

