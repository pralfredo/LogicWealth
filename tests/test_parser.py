from logicwealth.dsl.parser import parse_portlogic

def test_portlogic_parser():
    spec = parse_portlogic("""
    EXACTLY 18 ASSETS
    WEIGHT BETWEEN 0.02 AND 0.08
    SECTOR Technology <= 0.25
    BETA BETWEEN 0.8 AND 1.1
    IF SELECTED(TSLA) THEN NOT SELECTED(F)
    """)
    assert spec.cardinality == 18
    assert spec.sector_max["Technology"] == 0.25
    assert spec.implications == [("TSLA", "F", False)]
