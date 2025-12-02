from src.datasheets import datasheets

def test_lookup_width_6205():
    val, src = datasheets.lookup("6205", "width")
    assert val is not None
    assert "mm" in val

def test_lookup_bore_6205n():
    val, src = datasheets.lookup("6205 N", "bore diameter")
    assert val is not None
