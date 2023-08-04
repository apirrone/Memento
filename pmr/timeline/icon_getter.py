from thefuzz import fuzz
from glob import glob
import os
import pygame


class IconGetter:
    def __init__(self, size=100):
        self.all_icons_paths = []
        self.icons_paths = ["/usr/share/icons/**/", "/usr/share/pixmaps/**/"]
        self.extensions = [".png", ".jpg"]
        self.size = size

    def lookup_icon(self, app_name):
        if app_name in [None, "None"]:
            return None, None
        if self.all_icons_paths == []:
            for icons_path in self.icons_paths:
                for ext in self.extensions:
                    self.all_icons_paths += glob(
                        os.path.join(icons_path, "*" + ext), recursive=True
                    )
        best_score = 0
        best_icon_path = None
        for icon_path in self.all_icons_paths:
            score = fuzz.ratio(app_name, icon_path)
            if score > best_score:
                best_score = score
                best_icon_path = icon_path

        if best_icon_path is None:
            return None, None

        icon_big = pygame.transform.scale(
            pygame.image.load(best_icon_path), (self.size * 2, self.size * 2)
        )
        icon_small = pygame.transform.scale(
            pygame.image.load(best_icon_path), (self.size, self.size)
        )

        return icon_small, icon_big
