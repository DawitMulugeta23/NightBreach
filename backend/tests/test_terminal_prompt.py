from app.domains.sandbox.runtime.prompt import build_bashrc, build_prompt


def test_prompt_matches_spec_format():
    ps1 = build_prompt("alice")
    assert ps1.startswith("alice@DE=>M-[\\w]")
    assert ps1.endswith("|_____$ ")


def test_prompt_rejects_unsafe_username():
    import pytest

    with pytest.raises(ValueError):
        build_prompt("alice; rm -rf /")


def test_bashrc_exports_ps1():
    script = build_bashrc("bob")
    assert "export PS1='bob@DE=>M-[\\w]\\n|_____$ '" in script
    assert "HISTFILE=/tmp/.nb_history" in script