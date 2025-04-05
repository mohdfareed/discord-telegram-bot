__all__ = ["ChatBroker"]

import logging
import uuid

from . import db, models


class ChatBroker:
    """The chat broker between bots."""

    def __init__(self, db: db.Database) -> None:
        self.logger = logging.getLogger(type(self).__name__)
        self.database = db

    def get_publisher_id(self, publisher: str) -> int:
        """Get the unique ID of a publisher."""
        brokage = self.database.load(models.Brokage())
        if publisher not in brokage.pubs:
            self.reset_publisher_id(publisher)
            brokage = self.database.load(models.Brokage())  # reload
        return brokage.pubs[publisher]

    def reset_publisher_id(self, publisher: str) -> None:
        """Reset the unique ID of a publisher, removing all subscriptions."""
        brokage = self.database.load(models.Brokage())
        if publisher in brokage.pubs:  # remove existing subs
            del brokage.subs[brokage.pubs[publisher]]
            del brokage.pubs[publisher]

        new_id = uuid.uuid4().int
        brokage.pubs[publisher] = new_id  # update publisher id
        brokage.subs[new_id] = set()  # create new subs
        self.database.save(brokage)

    def get_subscribers(self, publisher: str) -> set[str]:
        """Get the subscribers of a publisher."""
        brokage = self.database.load(models.Brokage())
        if publisher not in brokage.pubs:
            self.reset_publisher_id(publisher)
            brokage = self.database.load(models.Brokage())  # reload
        return brokage.subs.get(brokage.pubs[publisher], set())

    def get_subscriptions(self, subscriber: str) -> set[int]:
        """Get the publishers to which a subscriber is subscribed."""
        brokage = self.database.load(models.Brokage())
        return {
            pub for pub, subs in brokage.subs.items() if subscriber in subs
        }

    def subscribe(self, subscriber: str, publisher_id: int) -> None:
        """Subscribe to a publisher."""
        brokage = self.database.load(models.Brokage())
        if publisher_id not in brokage.subs:
            brokage.subs[publisher_id] = set()
        brokage.subs[publisher_id].add(subscriber)
        self.database.save(brokage)

    def unsubscribe(self, subscriber: str, publisher_id: int) -> None:
        """Unsubscribe from a publisher."""
        brokage = self.database.load(models.Brokage())
        if publisher_id in brokage.subs:
            brokage.subs[publisher_id].discard(subscriber)
            self.database.save(brokage)

    def unsubscribe_all(self, subscriber: str) -> None:
        """Unsubscribe from all publishers."""
        brokage = self.database.load(models.Brokage())
        for publisher in list(brokage.subs):
            brokage.subs[publisher].discard(subscriber)
        self.database.save(brokage)
