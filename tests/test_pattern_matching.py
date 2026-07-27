from helpers import _Tester


def test_pattern_matching_by_kind():
    def match_by_kind(tester: _Tester) -> str:
        match tester.kind:
            case _Tester.Kind.STRING:
                return f"[STRING] {tester.item}"
            case _Tester.Kind.COORDINATES:
                x, y = tester.item
                return f"[COORDINATES] {x, y}"
            case _Tester.Kind.NONE:
                return "[NONE] Nothing"
            case _:
                raise ValueError

    assert match_by_kind(_Tester.STRING("Hello")) == "[STRING] Hello"
    assert match_by_kind(_Tester.COORDINATES((1.0, 2.0))) == "[COORDINATES] (1.0, 2.0)"
    assert match_by_kind(_Tester.NONE()) == "[NONE] Nothing"


def test_structural_pattern_matching():
    def match_structurally(tester: _Tester) -> str:
        match tester:
            case _Tester(case=_Tester.STRING, item=val):
                return f"Match: {val}"
            case _Tester(case=_Tester.COORDINATES, item=(x, y)):
                return f"Match: ({x}, {y})"
            case _Tester(case=_Tester.NONE):
                return "Match: Nothing"
            case _:
                raise ValueError

    assert match_structurally(_Tester.STRING("Python")) == "Match: Python"
    assert match_structurally(_Tester.COORDINATES((3.0, 4.0))) == "Match: (3.0, 4.0)"
    assert match_structurally(_Tester.NONE()) == "Match: Nothing"
