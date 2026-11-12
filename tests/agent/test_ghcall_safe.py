"""The print helpers in ghcall cut the token -> log data flow: only digits and fixed strings come out."""
import ghcall

TOKENS = ["ghp_" + "a1B2" * 9, "github_pat_" + "x9" * 20, "ghs_" + "Z" * 36, "0123456789abcdef" * 2 + "01234567"]


def test_num_emits_digits_only():
    assert ghcall.num(644) == "644"
    assert ghcall.num("7") == "7"
    assert ghcall.num(-3) == "-3"


def test_fixed_never_emits_unlisted_value():
    allowed = ("model:sonnet", "model:haiku")
    assert ghcall.fixed("model:sonnet", allowed) == "model:sonnet"
    for t in TOKENS:
        assert ghcall.fixed(t, allowed) == "?"


def test_mask_hides_token_shaped_values():
    for t in TOKENS:
        out = ghcall.mask(f"error for {t} while calling")
        assert t not in out
        assert "***" in out
    assert ghcall.mask("#12: started (model:haiku)") == "#12: started (model:haiku)"
