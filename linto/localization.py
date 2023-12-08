# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#                           
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import os
from typing import Any
import yaml
from .database import Database

class Localization:
    def __init__(self, database: Database) -> None:
        self.database = database

    @property
    def language(self):
        return self.database.get("linto", "language", "en")

    @property
    def languages(self):
        return os.listdir("linto/languages")
    
    @property
    def translations(self):
        translations = {}
        for lang in map(lambda x: x[:-4], self.languages):
            with open(f"linto/languages/{lang}.yml") as file:
                translations[lang] = yaml.safe_load(file)
        
        return translations
        
    def get_translations(self):
        """
        :return: Translation with current language
        """
        return self.translations[self.language]
    
class Translations(Localization):
    def __init__(self, database: Database, name: str) -> None:
        self.name = name
        super().__init__(database)
    
    def __getitem__(self, key: str):
        return self.get(key)
    
    def get(self, key: str) -> Any:
        translations = self.get_translations()
        return translations[self.name][key]
        
    def __call__(self, key: str) -> Any:
        return self.get(self.name, key)