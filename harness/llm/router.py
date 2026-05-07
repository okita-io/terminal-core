import os
from openai import OpenAI


def get_client(provider: str, config: dict) -> OpenAI:
    provider_cfg = config["providers"][provider]

    if "api_key_env" in provider_cfg:
        api_key = os.environ.get(provider_cfg["api_key_env"])
        if not api_key:
            raise ValueError(f"Environment variable {provider_cfg['api_key_env']} not set")
    else:
        api_key = provider_cfg.get("api_key", "local")

    kwargs = {"base_url": provider_cfg["base_url"], "api_key": api_key}

    if provider == "openrouter":
        kwargs["default_headers"] = {
            "HTTP-Referer": "https://tactic.studio",
            "X-Title": "Terminal Core",
        }

    return OpenAI(**kwargs)


def get_client_for_role(role: str, config: dict) -> tuple[OpenAI, dict]:
    role_cfg = config["llm_roles"][role]
    client = get_client(role_cfg["provider"], config)
    return client, role_cfg
