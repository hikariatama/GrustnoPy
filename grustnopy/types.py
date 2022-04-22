from dataclasses import dataclass


@dataclass
class User:
    uid: int
    nickname: str
    comment: str
    created_at: int

    async def delete(self) -> bool:
        """Delete this comment"""
        await self._client.delete_comment(self.uid)


@dataclass
class Comment:
    uid: int
    nickname: str
    comment: str
    created_at: int

    async def delete(self) -> bool:
        """Delete this comment"""
        await self._client.delete_comment(self.uid)

    async def like(self) -> bool:
        """Like this comment"""
        await self._client.like_comment(self.uid)

    async def dislike(self) -> bool:
        """Dislike this comment"""
        await self._client.dislike_comment(self.uid)


@dataclass
class Post:
    uid: int
    url: str
    media: str
    text: str
    user: User
    likes_count: int
    comments_count: int
    created_at: int

    async def delete(self) -> bool:
        """Delete this post"""
        await self._client.delete_post(self.uid)

    async def like(self) -> bool:
        """Like this post"""
        await self._client.like_post(self.uid)

    async def dislike(self) -> bool:
        """Dislike this post"""
        await self._client.dislike_post(self.uid)

    async def comment(self, text: str) -> Comment:
        """Leave a comment to this post"""
        return await self._client.comment_post(self.uid, text)
