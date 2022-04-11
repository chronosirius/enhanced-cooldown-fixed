"""
command_models

Content:

* EnhancedOption: typehintable option
* option: decoratable option

GitHub: https://github.com/interactions-py/enhanced/blob/main/interactions/ext/enhanced/command_models.py

(c) 2022 interactions-py.
"""
from msilib.schema import Component
from aiohttp import MultipartWriter
from typing import List, Optional, Union
from types import MethodType
from sys import modules

import interactions
from interactions import (
    MISSING,
    File,
    Embed,
    MessageInteraction,
    ActionRow,
    Button,
    SelectMenu,
    Message,
    InteractionCallbackType,
)
from interactions.api.http.route import Route
from interactions.client.context import _Context, CommandContext, ComponentContext
from interactions.client.models.component import _build_components
from loguru import logger

from ._logging import get_logger

log = get_logger("file_sending")


# file sending
async def create_interaction_response(
    self, token: str, application_id: int, data: dict, files: List[File]
) -> None:
    """
    Posts initial response to an interaction, but you need to add the token.
    :param token: Token.
    :param application_id: Application ID snowflake
    :param data: The data to send.
    """

    file_data = None
    if files:
        file_data = MultipartWriter("form-data")
        part = file_data.append_json(data)
        part.set_content_disposition("form-data", name="payload_json")
        data = None

        for id, file in enumerate(files):
            part = file_data.append(
                file._fp,
            )
            part.set_content_disposition("form-data", name=f"files[{str(id)}]", filename=file._filename)


    return await self._req.request(
        Route("POST", f"/interactions/{application_id}/{token}/callback"), json=data, data=file_data
    )


async def base_send(
    self,
    content: Optional[str] = MISSING,
    *,
    tts: Optional[bool] = MISSING,
    files: Optional[List[File]] = None,
    embeds: Optional[Union[Embed, List[Embed]]] = MISSING,
    allowed_mentions: Optional[MessageInteraction] = MISSING,
    components: Optional[
        Union[
            ActionRow,
            Button,
            SelectMenu,
            List[ActionRow],
            List[Button],
            List[SelectMenu],
        ]
    ] = MISSING,
    ephemeral: Optional[bool] = False,
) -> Message:
    """
    This allows the invocation state described in the "context"
    to send an interaction response.

    :param content?: The contents of the message as a string or string-converted value.
    :type content: Optional[str]
    :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
    :type tts: Optional[bool]
    :param embeds?: An embed, or list of embeds for the message.
    :type embeds: Optional[Union[Embed, List[Embed]]]
    :param allowed_mentions?: The message interactions/mention limits that the message can refer to.
    :type allowed_mentions: Optional[MessageInteraction]
    :param components?: A component, or list of components for the message.
    :type components: Optional[Union[ActionRow, Button, SelectMenu, List[Union[ActionRow, Button, SelectMenu]]]]
    :param ephemeral?: Whether the response is hidden or not.
    :type ephemeral: Optional[bool]
    :return: The sent message as an object.
    :rtype: Message
    """
    if (
        content is MISSING
        and self.message
        and self.callback == InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
    ):
        _content = self.message.content
    else:
        _content: str = "" if content is MISSING else content
    _tts: bool = False if tts is MISSING else tts
    # _file = None if file is None else file
    # _attachments = [] if attachments else None
    if (
        embeds is MISSING
        and self.message
        and self.callback == InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
    ):
        embeds = self.message.embeds
    _embeds: list = (
        []
        if not embeds or embeds is MISSING
        else (
            [embed._json for embed in embeds]
            if isinstance(embeds, list)
            else [embeds._json]
        )
    )
    _allowed_mentions: dict = {} if allowed_mentions is MISSING else allowed_mentions
    if components is not MISSING and components:
        # components could be not missing but an empty list
        _components = _build_components(components=components)
    elif (
        components is MISSING
        and self.message
        and self.callback == InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
    ):
        if isinstance(self.message.components, list):
            _components = self.message.components
        else:
            _components = [self.message.components]
    else:
        _components = []

    if not files or files is MISSING:
        _files = []
    elif isinstance(files, list):
        _files = [file._json_payload(id) for id, file in enumerate(files)]
    else:
        _files = [files._json_payload(0)]
        files = [files]

    _ephemeral: int = (1 << 6) if ephemeral else 0

    # TODO: post-v4: Add attachments into Message obj.
    payload: Message = Message(
        content=_content,
        tts=_tts,
        # files=file,
        attachments=_files,
        embeds=_embeds,
        allowed_mentions=_allowed_mentions,
        components=_components,
        flags=_ephemeral,
    )
    self.message = payload
    self.message._client = self.client
    return payload, files


async def command_send(self, content: Optional[str] = MISSING, **kwargs) -> Message:
    payload, files = await base_send(self, content, **kwargs)

    if not self.deferred:
        self.callback = InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE

    _payload: dict = {"type": 1, "data": payload._json}

    msg = None
    if self.responded or self.deferred:
        if self.deferred:
            res = await self.client.edit_interaction_response(
                data=payload._json,
                token=self.token,
                application_id=str(self.application_id),
            )
            self.responded = True
        else:
            res = await self.client._post_followup(
                data=payload._json,
                token=self.token,
                application_id=str(self.application_id),
            )
        self.message = msg = Message(**res, _client=self.client)
    else:
        await create_interaction_response(
            self.client,
            token=self.token,
            application_id=int(self.id),
            data=_payload,
            files=files,
        )
        __newdata = await self.client.edit_interaction_response(
            data={},
            token=self.token,
            application_id=str(self.application_id),
        )
        if not __newdata.get("code"):
            # if sending message fails somehow
            msg = Message(**__newdata, _client=self.client)
            self.message = msg
        self.responded = True
    if msg is not None:
        return msg
    return payload


async def component_send(self, content: Optional[str] = MISSING, **kwargs) -> Message:
    payload, files = await base_send(self, content, **kwargs)

    if not self.deferred:
        self.callback = InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE
    _payload: dict = {"type": self.callback.value, "data": payload._json}
    msg = None
    if (
        self.responded
        or self.deferred
        or self.callback == InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
    ):
        if self.deferred:
            res = await self.client.edit_interaction_response(
                data=payload._json,
                token=self.token,
                application_id=str(self.application_id),
            )
            self.responded = True
        else:
            res = await self.client._post_followup(
                data=payload._json,
                token=self.token,
                application_id=str(self.application_id),
            )
        self.message = msg = Message(**res, _client=self.client)
    else:
        await create_interaction_response(
            self.client,
            token=self.token,
            application_id=int(self.id),
            data=_payload,
            files=files,
        )
        __newdata = await self.client.edit_interaction_response(
            data={},
            token=self.token,
            application_id=str(self.application_id),
        )
        if not __newdata.get("code"):
            # if sending message fails somehow
            msg = Message(**__newdata, _client=self.client)
            self.message = msg
        self.responded = True
    if msg is not None:
        return msg
    return payload


# _Context.send = MethodType(base_send, _Context)
# CommandContext.send = MethodType(command_send, CommandContext)
# ComponentContext.send = MethodType(component_send, ComponentContext)

_Context.send = base_send
CommandContext.send = command_send
ComponentContext.send = component_send
