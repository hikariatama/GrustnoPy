import asyncio
import functools
import requests
import json
from .errors import (
    EmailExistsError,
    LoginExistsError,
    UserNotFoundError,
    BadCredentialsError,
    UnknownError,
)
from typing import Callable, List, Optional
from .types import Comment


def run_sync(func, *args, **kwargs):
    """Run a non-async function in a new thread and return an awaitable"""
    # Returning a coro
    return asyncio.get_event_loop().run_in_executor(
        None,
        functools.partial(
            func,
            *args,
            **kwargs,
        ),
    )


class GrustnogramClient:
    """Provides quick and easy access to Grustnogram API"""

    _token = None

    def __init__(self) -> None:
        ...

    async def _validate_result(self, result: dict) -> None:
        if "err" not in result or not result["err"]:
            return

        if 100 in result["err"]:
            raise EmailExistsError("Specified email already exists")

        if 101 in result["err"]:
            raise LoginExistsError("Specified login already exists")

        if 102 in result["err"]:
            raise UserNotFoundError("Specified user not found")

        if 103 in result["err"]:
            raise BadCredentialsError("Specified password is invalid")

        if any(result["err"]):
            raise UnknownError(json.dumps(result, indent=4))

    async def login(self, login: str, password: str) -> bool:
        """
        Authentificate in Grustnogram
        :param login: Grustnogram login
        :param password: Grustnogram password
        """
        result = (
            await run_sync(
                requests.post,
                "https://api.grustnogram.ru/sessions",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                },
                data=json.dumps({"email": login, "password": password}).encode(),
            )
        ).json()

        self._validate_result(result)
        self._token = result["data"]["access_token"]
        return True

    async def register(
        self,
        nickname: str,
        email: str,
        password: str,
        phone: str,
        code_handler: Callable = lambda: input(
            "Our sad bot is calling you, enter 4 last digits: "
        ),
    ) -> bool:
        """
        Register a new account
        :param nickname: Nickname
        :param email: Email
        :param password: Password
        :param phone: Phone (will be checked btw)
        :param code_handler: Callable, used to get a code
        """
        result = (
            await run_sync(
                requests.post,
                "https://api.grustnogram.ru/users",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                },
                data=json.dumps(
                    {
                        "nickname": nickname,
                        "email": email,
                        "password": password,
                        "password_confirm": password,
                    }
                ).encode(),
            )
        ).json()
        self._validate_result(result)

        phone_key = result["data"]["phone_key"]
        result = (
            await run_sync(
                requests.post,
                "https://api.grustnogram.ru/callme",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                },
                data=json.dumps(
                    {
                        "phone_key": phone_key,
                        "phone": phone,
                    }
                ).encode(),
            )
        ).json()
        self._validate_result(result)

        code = code_handler()
        result = (
            await run_sync(
                requests.post,
                "https://api.grustnogram.ru/phoneactivate",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                },
                data=json.dumps(
                    {
                        "code": code,
                        "phone": phone,
                    }
                ).encode(),
            )
        ).json()
        self._validate_result(result)

        self._token = result["data"]["access_token"]
        return True

    async def like_post(self, post_id: int) -> bool:
        """
        Like a post
        :param post_id: Post ID
        """
        result = (
            await run_sync(
                requests.post,
                f"https://api.grustnogram.ru/posts/{post_id}/like",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                    "access-token": self._token,
                },
            )
        ).json()
        self._validate_result(result)
        return True

    async def dislike_post(self, post_id: int) -> bool:
        """
        Dislike a post
        :param post_id: Post ID
        """
        result = (
            await run_sync(
                requests.delete,
                f"https://api.grustnogram.ru/posts/{post_id}/like",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                    "access-token": self._token,
                },
            )
        ).json()
        self._validate_result(result)
        return True

    async def like_comment(self, comment_id: int) -> bool:
        """
        Like a comment
        :param comment_id: Comment ID
        """
        result = (
            await run_sync(
                requests.post,
                f"https://api.grustnogram.ru/comments/{comment_id}/like",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                    "access-token": self._token,
                },
            )
        ).json()
        self._validate_result(result)
        return True

    async def dislike_comment(self, comment_id: int) -> bool:
        """
        Dislike a comment
        :param comment_id: Comment ID
        """
        result = (
            await run_sync(
                requests.delete,
                f"https://api.grustnogram.ru/comments/{comment_id}/like",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                    "access-token": self._token,
                },
            )
        ).json()
        self._validate_result(result)
        return True

    async def comment_post(self, post_id: int, comment: str) -> Comment:
        """
        Leave a comment to post
        :param post_id: Post ID
        :param comment: Comment text
        """
        result = (
            await run_sync(
                requests.post,
                f"https://api.grustnogram.ru/posts/{post_id}/comments",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                    "access-token": self._token,
                },
                data=json.dumps({"comment": comment}).encode(),
            )
        ).json()
        self._validate_result(result)
        return Comment(
            result["data"]["id"],
            result["data"]["nickname"],
            result["data"]["comment"],
            result["data"]["created_at"],
        )

    async def delete_comment(self, comment_id: int) -> bool:
        """
        Leave a comment to post
        :param post_id: Post ID
        :param comment: Comment text
        """
        result = (
            await run_sync(
                requests.delete,
                f"https://api.grustnogram.ru/posts/comment/{comment_id}",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                    "access-token": self._token,
                },
            )
        ).json()
        self._validate_result(result)
        return True

    async def get_comments(
        self,
        post_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Comment]:
        """
        Get comments of post
        :param post_id: Post ID
        """
        result = (
            await run_sync(
                requests.get,
                f"https://api.grustnogram.ru/posts/{post_id}/comments",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                    "access-token": self._token,
                },
                data=json.dumps({"limit": limit, "offset": offset}).encode(),
            )
        ).json()
        self._validate_result(result)
        return [
            Comment(
                comment["id"],
                comment["nickname"],
                comment["comment"],
                comment["created_at"],
            )
            for comment in result["data"]
        ]

    async def complaint(
        self,
        post_id: int,
        complaint_type: int,
        text: Optional[str] = None,
    ) -> bool:
        """
        Leave a complaint to the post
        :param post_id: Post ID
        :param type: Complaint type:
            1 - Unacceptable materials
            2 - Insults me
            3 - Insults Russia
        :param text: Optional: Complaint text
        """
        result = (
            await run_sync(
                requests.post,
                f"https://api.grustnogram.ru/posts/{post_id}/complaint",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                    "access-token": self._token,
                },
                data=json.dumps({"type": complaint_type, "text": text}).encode(),
            )
        ).json()
        self._validate_result(result)
        return True

    async def delete_post(
        self,
        post_id: int,
    ) -> bool:
        """
        Delete post
        :param post_id: Post ID
        """
        result = (
            await run_sync(
                requests.delete,
                f"https://api.grustnogram.ru/posts/{post_id}",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Python SDK",
                    "access-token": self._token,
                },
            )
        ).json()
        self._validate_result(result)
        return True
