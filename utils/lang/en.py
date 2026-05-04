def try_verb_past(w: str, p: int) -> str:
    return w

def inflect(s: str, form: str, _pn: int | None = None) -> str:
    ret = lemminflect.getInflection(s, form)[0]
    assert isinstance(ret, str)
    return ret

def agree_with_number(s: str, num: int, _: any) -> str:
    if type(num) != int or abs(num) > 1:
        return s + "s"
    return s
