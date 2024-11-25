from typing import Any, Callable, List


def test1(arg1: bool, arg2: Any, arg3: Any) -> Any:
    return arg2 if arg1 else arg3


def test2(arg1: List[int]) -> int:
    return 0 if len(arg1) < 1 else arg1[0] + test2(arg1[1:])


def test3(arg1: List[int], arg2: List[int]) -> List[int]:
    return (
        []
        if len(arg1) < 1 or not len(arg1) == len(arg2)
        else [arg1[0] * arg2[0], *test3(arg1[1:], arg2[1:])]
    )


def test4(arg1: List[int]) -> int:
    return (
        arg1[0]
        if len(arg1) <= 1
        else (arg1[0] if arg1[0] > test4(arg1[1:]) else test4(arg1[1:]))
    )


def test5(arg1: List[int], arg2: List[int]) -> List[int]:
    return (
        []
        if len(arg1) < 1 or not len(arg1) == len(arg2)
        else [arg1[0] + arg2[0], *test5(arg1[1:], arg2[1:])]
    )


def test6(arg1: List[int], arg2: List[int]) -> List[int]:
    return (
        []
        if len(arg1) < 1 or not len(arg1) == len(arg2)
        else [arg1[0] - arg2[0], *test6(arg1[1:], arg2[1:])]
    )


def test7(arg1: List[int], arg2: List[int]) -> List[int]:
    return (
        []
        if len(arg1) < 1 or not len(arg1) == len(arg2)
        else [arg1[0] // arg2[0], *test7(arg1[1:], arg2[1:])]
    )


def test8(arg1: List[List[int]], arg2: List[List[int]]) -> List[List[int]]:
    return (
        []
        if len(arg1) < 1 or not len(arg1) == len(arg2)
        else [
            test5(arg1[0], arg2[0]),
            *test8(arg1[1:], arg2[1:]),
        ]
    )


def test9(arg1: List[List[int]], arg2: List[List[int]]) -> List[List[int]]:
    return (
        []
        if len(arg1) < 1 or not len(arg1) == len(arg2)
        else [
            test6(arg1[0], arg2[0]),
            *test9(arg1[1:], arg2[1:]),
        ]
    )


def test10(arg1: int, arg2: List[List[int]]) -> List[List[int]]:
    return (
        []
        if len(arg2) < 1
        else [test15(arg1, arg2[0]), *test10(arg1, arg2[1:])]
    )


def test11(arg1: int, arg2: List[List[int]]) -> List[List[int]]:
    return (
        []
        if len(arg2) < 1
        else [test16(arg1, arg2[0]), *test11(arg1, arg2[1:])]
    )


def test12(arg1: List[List[int]]) -> List[List[int]]:
    return [] if len(arg1) < 1 else [test32(arg1), *test12(test33(arg1))]


def test13(arg1: List[List[int]], arg2: List[List[int]]) -> List[List[int]]:
    return (
        []
        if len(arg1) < 1 or not len(arg1) == len(arg2)
        else [
            test7(arg1[0], arg2[0]),
            *test13(arg1[1:], arg2[1:]),
        ]
    )


def test14(arg1: int, arg2: List[int]) -> List[int]:
    return [] if len(arg2) < 1 else [arg1 + arg2[0], *test14(arg1, arg2[1:])]


def test15(arg1: int, arg2: List[int]) -> List[int]:
    return [] if len(arg2) < 1 else [arg2[0] - arg1, *test15(arg1, arg2[1:])]


def test16(arg1: int, arg2: List[int]) -> List[int]:
    return [] if len(arg2) < 1 else [arg1 * arg2[0], *test16(arg1, arg2[1:])]


def test17(arg1: int, arg2: List[int]) -> List[int]:
    return [] if len(arg2) < 1 else [arg2[0] // arg1, *test17(arg1, arg2[1:])]


def test18(arg1: int, arg2: List[int]) -> List[int]:
    return [] if len(arg2) < 1 else [arg1 - arg2[0], *test18(arg1, arg2[1:])]


def test19(arg1: int, arg2: List[int]) -> List[int]:
    return [] if len(arg2) < 1 else [arg1 // arg2[0], *test19(arg1, arg2[1:])]


def test20(arg1: int, arg2: List[List[int]]) -> List[List[int]]:
    return (
        []
        if len(arg2) < 1
        else [test14(arg1, arg2[0]), *test20(arg1, arg2[1:])]
    )


def test21(arg1: List[List[int]], arg2: List[int]) -> List[int]:
    return (
        []
        if len(arg1) < 1 or len(arg1[0]) < 1 or not len(arg1[0]) == len(arg2)
        else [
            test2(test3(arg1[0], arg2)),
            *test21(arg1[1:], arg2),
        ]
    )


def test22(arg1: List[int]) -> int:
    return 1 if len(arg1) < 1 else arg1[0] * test22(arg1[1:])


def test23(arg1: int, arg2: List[List[int]]) -> List[List[int]]:
    return (
        []
        if len(arg2) < 1
        else [test17(arg1, arg2[0]), *test23(arg1, arg2[1:])]
    )


def test24(arg1: int, arg2: List[List[int]]) -> List[List[int]]:
    return (
        []
        if len(arg2) < 1
        else [test18(arg1, arg2[0]), *test24(arg1, arg2[1:])]
    )


def test25(arg1: int, arg2: List[List[int]]) -> List[List[int]]:
    return (
        []
        if len(arg2) < 1
        else [test19(arg1, arg2[0]), *test25(arg1, arg2[1:])]
    )


def test26(arg1: List[int], arg2: Callable[[int], int]) -> List[int]:
    return [] if len(arg1) < 1 else [arg2(arg1[0]), *test26(arg1[1:], arg2)]


def test27(
    arg1: List[List[int]],
    arg2: List[List[int]],
    arg3: Callable[[int, int], int],
) -> List[List[int]]:
    return (
        []
        if len(arg1) < 1 or not len(arg1) == len(arg2)
        else [
            test28(arg1[0], arg2[0], arg3),
            *test27(arg1[1:], arg2[1:], arg3),
        ]
    )


def test28(
    arg1: List[int],
    arg2: List[int],
    arg3: Callable[[int, int], int]
) -> List[int]:
    return (
        []
        if len(arg1) < 1 or not len(arg1) == len(arg2)
        else [
            arg3(arg1[0], arg2[0]),
            *test28(arg1[1:], arg2[1:], arg3),
        ]
    )


def test29(arg1: List[int], arg2: int, arg3: int) -> List[int]:
    return arg1[:arg3][arg2:]


def test30(arg1: List[List[int]], arg2: int, arg3: int) -> List[List[int]]:
    return arg1[:arg3][arg2:]


def test31(arg1: List[List[int]], arg2: int, arg3: int) -> List[List[int]]:
    return (
        []
        if len(arg1) < 1
        else [arg1[0][arg2:arg3], *test31(arg1[1:], arg2, arg3)]
    )


def test32(arg1: List[List[int]]) -> List[int]:
    return [] if len(arg1) < 1 else [arg1[0][0], *test32(arg1[1:])]


def test33(arg1: List[List[int]]) -> List[List[int]]:
    return [] if len(arg1) < 1 else test31(arg1, 1, len(arg1[0]))


def test34(arg1: List[List[int]], arg2: List[List[int]]) -> List[List[int]]:
    return (
        []
        if len(arg1) < 1 or not len(arg1) == len(arg2)
        else [
            test3(arg1[0], arg2[0]),
            *test34(arg1[1:], arg2[1:]),
        ]
    )


def integer_sqrt(n: int) -> int:
    """Return the integer square root of n."""
    return n


def integer_exp(n: int) -> int:
    """Returns e raised to the power of n as integer."""
    return n


def test35(arg1: List[List[int]], arg2: int) -> List[int]:
    return test12(test31(arg1, arg2, arg2 + 1))[0]
