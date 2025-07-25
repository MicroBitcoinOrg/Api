from functools import lru_cache
from dynaconf import Dynaconf  # type: ignore


__all__ = ["get_settings"]


@lru_cache()
def get_settings():
    return Dynaconf(
        settings_files=["settings.toml"],
        default_env="default",
        environments=True,
    )
