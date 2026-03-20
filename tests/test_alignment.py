from utils.alignment import align, get_width, is_wide, remove_ansi_escape


class TestRemoveAnsiEscape:
    """Equivalence classes: string with ANSI, string without ANSI, empty string."""

    def test_removes_color_codes(self):
        assert remove_ansi_escape("\033[94mHello\033[0m") == "Hello"

    def test_removes_underline_codes(self):
        assert remove_ansi_escape("\033[4mHi\033[0m") == "Hi"

    def test_no_ansi(self):
        assert remove_ansi_escape("plain text") == "plain text"

    def test_empty_string(self):
        assert remove_ansi_escape("") == ""


class TestIsWide:
    """Equivalence classes: CJK wide, ASCII narrow, fullwidth, halfwidth."""

    def test_cjk_character(self):
        assert is_wide("鄭") is True

    def test_ascii_character(self):
        assert is_wide("a") is False

    def test_fullwidth_character(self):
        assert is_wide("Ａ") is True

    def test_halfwidth_katakana(self):
        assert is_wide("ｱ") is False

    def test_digit(self):
        assert is_wide("1") is False


class TestGetWidth:
    """Equivalence classes: ASCII, CJK, mixed, emoji, empty."""

    def test_ascii_string(self):
        assert get_width("Hello") == 5

    def test_cjk_string(self):
        assert get_width("你好") == 4

    def test_mixed_string(self):
        assert get_width("Hi你") == 4

    def test_empty_string(self):
        assert get_width("") == 0

    def test_emoji_with_variation(self):
        assert get_width("❤️") == 1

    def test_wide_emoji(self):
        assert get_width("✊") == 2

    def test_zwj_emoji_sequence(self):
        assert get_width("🏳️‍🌈") == 3


class TestAlign:
    """Equivalence classes: left-align, right-align, invalid direction, empty, overflow."""

    def test_left_align_ascii(self):
        result = align("Hi", direction="l", length=6)
        assert result == "Hi    "

    def test_right_align_ascii(self):
        result = align("Hello", direction="r", length=8)
        assert result == "   Hello"

    def test_right_align_cjk(self):
        result = align("你好", direction="r", length=8)
        assert result == "    你好"

    def test_left_align_default(self):
        result = align("Hi", length=6)
        assert result == "Hi    "

    def test_empty_string(self):
        assert align("", length=6) == ""

    def test_invalid_direction(self):
        assert align("Hi", direction="x", length=6) is None

    def test_string_longer_than_length(self):
        result = align("LongString", direction="l", length=2)
        assert result is not None
        assert result.startswith("LongString")
