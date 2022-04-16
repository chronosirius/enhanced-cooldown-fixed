from inspect import getdoc, signature
from typing import Any, Callable, Coroutine, List, Optional, Union

from interactions import MISSING, Guild, InteractionException, Option, OptionType

from ._logging import get_logger
from .command_models import parameters_to_options

log = get_logger("subcommand")


class SubcommandManager:
    def __init__(self, manager: "Manager") -> None:
        self.m = manager

    def __call__(
        self,
        _coro: Optional[Coroutine] = MISSING,
        *,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        options: Optional[List[Option]] = MISSING,
    ) -> Callable[..., Any]:
        def decorator(coro: Coroutine) -> Coroutine:
            _name = coro.__name__ if name is MISSING else name
            _description = (
                (getdoc(coro) or "No description") if description is MISSING else description
            ).split("\n")[0]
            if len(_description) > 100:
                raise ValueError("Description must be less than 100 characters.")

            params = signature(coro).parameters
            _options = (
                getattr(coro, "__decor_options")
                if hasattr(coro, "__decor_options")
                else parameters_to_options(params)
                if options is MISSING and len(params) > 1
                else None
                if options is MISSING
                else options
            )

            if not params:
                raise InteractionException(
                    11,
                    message="Your command needs at least one argument to return context.",
                )

            self.m.data.append(
                Option(
                    type=OptionType.SUB_COMMAND,
                    name=_name,
                    description=_description,
                    options=_options,
                )._json
            )

            return coro

        if _coro is not MISSING:
            return decorator(_coro)
        return decorator


class GroupManager:
    def __init__(self, manager: "Manager") -> None:
        self.m = manager
        self.group: Optional[str] = None

    def __call__(
        self,
        _coro: Optional[Coroutine] = MISSING,
        *,
        group: Optional[str] = MISSING,
    ) -> Callable[..., Any]:
        def decorator(coro: Coroutine) -> Coroutine:
            _group = coro.__name__ if group is MISSING else group
            self.m.data.append(
                Option(
                    type=OptionType.SUB_COMMAND_GROUP,
                    name=_group,
                    description=(getdoc(coro) or "No description").split("\n")[0],
                )._json
            )
            self.m.groups.append(_group)
            self.group = _group

            try:
                coro.subcommand = self.subcommand
            except AttributeError:
                coro.__func__.subcommand = self.subcommand

            return coro

        if _coro is not MISSING:
            return decorator(_coro)
        return decorator

    def subcommand(
        self,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        options: Optional[List[Option]] = MISSING,
    ) -> Callable[..., Any]:
        def decorator(coro: Coroutine) -> Coroutine:
            _name = coro.__name__ if name is MISSING else name
            _description = (
                (getdoc(coro) or "No description") if description is MISSING else description
            ).split("\n")[0]
            if len(_description) > 100:
                raise ValueError("Description must be less than 100 characters.")

            params = signature(coro).parameters
            _options = (
                getattr(coro, "__decor_options")
                if hasattr(coro, "__decor_options")
                else parameters_to_options(params)
                if options is MISSING and len(params) > 1
                else None
                if options is MISSING
                else options
            )

            if not params:
                raise InteractionException(
                    11,
                    message="Your command needs at least one argument to return context.",
                )

            if not self.group:
                raise InteractionException(
                    12,
                    message="You must call `group` before calling `subcommand`.",
                )

            for i, group in enumerate(self.m.data):
                if group["type"] == OptionType.SUB_COMMAND_GROUP and group["name"] == self.group:
                    print("E", self.m.data[i])
                    if group.get("options"):
                        self.m.data[i]["options"].append(
                            Option(
                                type=OptionType.SUB_COMMAND,
                                name=_name,
                                description=_description,
                                options=_options,
                            )._json
                        )
                    else:
                        self.m.data[i]["options"] = [
                            Option(
                                type=OptionType.SUB_COMMAND,
                                name=_name,
                                description=_description,
                                options=_options,
                            )._json
                        ]
                    break

            return coro

        return decorator


class Manager:
    def __init__(
        self,
        base: str,
        description: str,
        options: list,
        scope: Union[int, Guild, List[int], List[Guild]],
        default_permission: bool,
    ) -> None:
        self.base = base
        self.description = description
        self.options = options
        self.scope = scope
        self.default_permission = default_permission
        self.groups: List[str] = []
        self.data: List[dict] = []

        self.subcommand = SubcommandManager(self)
        self.group = GroupManager(self)
