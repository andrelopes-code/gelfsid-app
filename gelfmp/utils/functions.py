import os

from gelfcore.logger import log


def handle_file_cleanup(instance):
    try:
        if instance.pk:
            old_file = instance.__class__.objects.get(pk=instance.pk).file
            if old_file and os.path.exists(old_file.path):
                if not instance.file or (instance.file and instance.file.name != old_file.name):
                    os.remove(old_file.path)

    except Exception as e:
        log.error(f'Erro ao tentar deletar arquivo: [{instance.__class__.__name__}] {e}')


def handle_file_cleanup_on_delete(instance):
    try:
        if instance.file and os.path.exists(instance.file.path):
            instance.file.close()
            os.remove(instance.file.path)

    except Exception as e:
        log.error(f'Erro ao tentar deletar arquivo: [{instance.__class__.__name__}] {e}')
