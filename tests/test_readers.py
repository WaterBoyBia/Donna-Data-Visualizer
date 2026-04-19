import numpy as np
import numpy.testing as npt
import os
import tempfile
import pytest
from readers import read_file


class TestReadAsc:
    """Tests for reading .asc files."""

    def test_read_asc_returns_correct_structure(self):
        asc_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "202512211-RSV-17-rsv-22-hepes 10 150 7.5-s200.asc"
        )
        x, y_series, labels = read_file(asc_path)
        assert isinstance(x, np.ndarray)
        assert isinstance(y_series, list)
        assert len(y_series) >= 1
        assert isinstance(y_series[0], np.ndarray)
        assert isinstance(labels, list)
        assert len(labels) == len(y_series)

    def test_read_asc_data_shape(self):
        asc_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "202512211-RSV-17-rsv-22-hepes 10 150 7.5-s200.asc"
        )
        x, y_series, labels = read_file(asc_path)
        assert x.ndim == 1
        assert y_series[0].ndim == 1
        assert len(x) == len(y_series[0])
        assert len(x) > 0

    def test_read_asc_first_values(self):
        asc_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "202512211-RSV-17-rsv-22-hepes 10 150 7.5-s200.asc"
        )
        x, y_series, labels = read_file(asc_path)
        npt.assert_almost_equal(x[0], 0.0, decimal=3)
        npt.assert_almost_equal(y_series[0][0], -0.8936033, decimal=5)

    def test_read_asc_series_name(self):
        asc_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "202512211-RSV-17-rsv-22-hepes 10 150 7.5-s200.asc"
        )
        _, _, labels = read_file(asc_path)
        assert len(labels) == 1
        assert "mAU" in labels[0]

    def test_read_unsupported_extension_raises(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            read_file("data.csv")

    def test_read_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            read_file("nonexistent.asc")

    def test_read_asc_from_temp_file(self):
        content = "Chrom.1\nUV\nml\tmAU\n0\t1.5\n1\t2.5\n2\t3.5\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".asc", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = f.name
        try:
            x, y_series, labels = read_file(tmp_path)
            npt.assert_array_equal(x, np.array([0.0, 1.0, 2.0]))
            npt.assert_array_almost_equal(y_series[0], np.array([1.5, 2.5, 3.5]))
            assert labels == ["mAU"]
        finally:
            os.unlink(tmp_path)


class TestReadXls:
    """Tests for reading .xls files."""

    def test_read_xls_returns_correct_structure(self):
        xls_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "20260327-NDN-RSV-22-HEPES.xls"
        )
        x, y_series, labels = read_file(xls_path)
        assert isinstance(x, np.ndarray)
        assert isinstance(y_series, list)
        assert len(y_series) >= 1
        assert isinstance(y_series[0], np.ndarray)
        assert isinstance(labels, list)
        assert len(labels) == len(y_series)

    def test_read_xls_data_shape(self):
        xls_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "20260327-NDN-RSV-22-HEPES.xls"
        )
        x, y_series, labels = read_file(xls_path)
        for y in y_series:
            assert len(x) == len(y)

    def test_read_xls_multiple_series(self):
        xls_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "20260327-NDN-RSV-22-HEPES.xls"
        )
        x, y_series, labels = read_file(xls_path)
        assert len(y_series) == 2
        assert len(labels) == 2

    def test_read_xls_series_names_from_header(self):
        xls_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "20260327-NDN-RSV-22-HEPES.xls"
        )
        _, _, labels = read_file(xls_path)
        assert "UV1_280" in labels[0]
        assert "UV2_260" in labels[1]

    def test_read_xls_first_values(self):
        xls_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "20260327-NDN-RSV-22-HEPES.xls"
        )
        x, y_series, labels = read_file(xls_path)
        npt.assert_almost_equal(x[0], -2.775, decimal=3)
        npt.assert_almost_equal(y_series[0][0], 54.197, decimal=2)
        npt.assert_almost_equal(y_series[1][0], 28.14, decimal=2)
