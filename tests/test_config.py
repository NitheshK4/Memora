from app.config import Settings

def test_settings_default_openai_not_configured():
    settings = Settings(OPENAI_API_KEY="")
    assert settings.is_openai_configured is False

def test_settings_openai_configured_with_whitespace():
    settings = Settings(OPENAI_API_KEY="   ")
    assert settings.is_openai_configured is False

def test_settings_openai_configured_success():
    settings = Settings(OPENAI_API_KEY="sk-1234567890abcdef")
    assert settings.is_openai_configured is True
