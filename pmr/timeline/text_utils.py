import pygame


class TextRectException:
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


def get_lines(text, font, w):
    final_lines = []
    requested_lines = text.splitlines()

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > w:
            words = requested_line.split(" ")
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "

                if font.size(test_line)[0] < w:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)
    return final_lines


def get_text_height(text, font, w):
    lines = get_lines(text, font, w)
    height = 0
    for line in lines:
        height += font.size(line)[1]
    return height


def render_text(screen, text, font, x, y, w, text_color):
    final_lines = get_lines(text, font, w)

    accumulated_height = 0
    for line in final_lines:
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            screen.blit(tempsurface, (x, y + accumulated_height))
        accumulated_height += font.size(line)[1]
