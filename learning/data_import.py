
import os

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learning.settings")
    import django
    django.setup()

    from network.models import Person,Device
    pass
