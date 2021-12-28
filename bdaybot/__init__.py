from bdaybot.base import BirthdayBot


__all__ = ("bot", "EXTENSIONS")


bot = BirthdayBot()
EXTENSIONS = {"bdaybot.exts.owner"}  # add more here as you go
