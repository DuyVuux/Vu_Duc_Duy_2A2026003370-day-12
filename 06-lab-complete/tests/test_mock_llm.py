import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.mock_llm import ask, ask_stream


def test_ask_returns_string():
    result = ask("hello")
    assert isinstance(result, str)
    assert len(result) > 0


def test_ask_docker_keyword():
    result = ask("What is docker?")
    assert "container" in result.lower() or "anywhere" in result.lower()


def test_ask_deploy_keyword():
    result = ask("How to deploy?")
    assert "deployment" in result.lower() or "server" in result.lower()


def test_ask_default_response():
    result = ask("random question xyz")
    assert isinstance(result, str)
    assert len(result) > 0


def test_ask_stream_yields_words():
    words = list(ask_stream("test question"))
    assert len(words) > 0
    full_text = "".join(words).strip()
    assert len(full_text) > 0
