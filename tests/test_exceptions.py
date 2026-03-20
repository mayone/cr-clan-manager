import pytest

from exceptions import APIError, SheetError


class TestAPIError:
    """Equivalence classes: dict payload, non-dict payload."""

    def test_dict_payload(self):
        err = APIError(404, {"message": "Not found"})
        assert err.status_code == 404
        assert err.payload == {"message": "Not found"}
        assert "404" in str(err)

    def test_raises_and_catches(self):
        with pytest.raises(APIError) as exc_info:
            raise APIError(403, {"reason": "forbidden"})
        assert exc_info.value.status_code == 403

    def test_inherits_from_exception(self):
        err = APIError(500, {})
        assert isinstance(err, Exception)


class TestSheetError:
    def test_message(self):
        err = SheetError("sheet not found")
        assert str(err) == "sheet not found"

    def test_inherits_from_exception(self):
        assert issubclass(SheetError, Exception)
