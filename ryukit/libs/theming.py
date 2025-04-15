# ====================================================================
# Code provided by https://github.com/A-2-4-8-5-10-9-7-3-6-1/pykit.git
# ====================================================================
#
# - version: 0.2.2

"""Theme-setting utilities."""

import collections
import collections.abc
import functools
import typing

__all__ = ["theme_applier"]


# MARK: Theme Appliers

type Args = tuple[object, ...]
type Kwargs = dict[str, object]
type ThemedFunction[**P, R] = collections.abc.Callable[P, R]
type FunctionReturn = object


class Configs(typing.TypedDict, total=False):
    default_kwargs: Kwargs
    preprocessor: collections.abc.Callable[..., tuple[Args, Kwargs]]
    postprocessor: collections.abc.Callable[[FunctionReturn], FunctionReturn]


def theme_applier(
    configs: (
        dict[collections.abc.Callable[..., object], Configs] | None
    ) = None,
):
    """
    Generate a theme-applier hook.

    :param configs: Functions recognized by your theme, and their default settings.

    :returns: A theme-applier hook.

    Instructions
    ------------

    When working functions returned by the applier, ensure that arguments for parameters in the function's "default_kwargs" field are passed only as kwargs; for example:

    ```
    def f(param0: str, param1: str, ...):
        ...

    applier = theme_applier({
        f: {
            "default_kwargs": {
                "param1": "foo",
            }
        },
        ...
    })

    applier(f)("foobar", param1="bar") # correct
    applier(f)("foobar", "bar") # problematic
    ```

    Note that there's no issue with the first argument in either case, because it was not included in "default_kwargs". Overall, it's recommended to have consistency over the arguments for any function recognized by the applier; flipping between use of positional and keyword arguments might result in unintended behaviour.
    """

    configs = configs or {}

    def applier[**P, R](
        function: collections.abc.Callable[P, R],
    ) -> ThemedFunction[P, R]:
        if function not in configs:
            return function

        @functools.wraps(function)
        def inner(*args: P.args, **kwargs: P.kwargs):
            args, kwargs = typing.cast(
                typing.Any,
                configs[function].get(
                    "preprocessor", lambda *args, **kwargs: (args, kwargs)
                )(
                    *args,
                    **(configs[function].get("default_kwargs", {}) | kwargs),
                ),
            )

            try:
                return typing.cast(
                    collections.abc.Callable[[R], R],
                    configs[function].get("postprocessor", lambda x: x),
                )(function(*args, **kwargs))

            except TypeError as e:
                raise TypeError(
                    "If the previous error was regarding duplicate arguments, "
                    "then please refer to the `theme_applier` instructions."
                ) from e

        return inner

    return applier
