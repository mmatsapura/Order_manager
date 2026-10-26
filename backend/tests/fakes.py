from bson import ObjectId
from pymongo.errors import DuplicateKeyError


class InsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class FakeCursor:
    def __init__(self, docs):
        self.docs = list(docs)

    def sort(self, key, direction):
        self.docs.sort(key=lambda doc: doc.get(key), reverse=direction < 0)
        return self

    def skip(self, count):
        self.docs = self.docs[count:]
        return self

    def limit(self, count):
        self.docs = self.docs[:count]
        return self

    async def to_list(self, length=None):
        if length is None:
            return self.docs
        return self.docs[:length]


class FakeCollection:
    def __init__(self):
        self.docs = []

    async def insert_one(self, payload):
        doc = dict(payload)
        if "email" in doc and any(item.get("email") == doc["email"] for item in self.docs):
            raise DuplicateKeyError("duplicate email")
        doc["_id"] = ObjectId()
        self.docs.append(doc)
        return InsertResult(doc["_id"])

    async def find_one(self, filters):
        for doc in self.docs:
            if _match(doc, filters):
                return doc
        return None

    async def update_one(self, filters, update):
        for doc in self.docs:
            if _match(doc, filters):
                doc.update(update.get("$set", {}))
                return

    async def delete_one(self, filters):
        self.docs = [doc for doc in self.docs if not _match(doc, filters)]

    async def count_documents(self, filters):
        return len(self._filtered(filters))

    def find(self, filters):
        return FakeCursor(self._filtered(filters))

    def _filtered(self, filters):
        return [doc for doc in self.docs if _match(doc, filters)]


class FakeDB:
    def __init__(self):
        self._collections = {}

    def __getitem__(self, name):
        if name not in self._collections:
            self._collections[name] = FakeCollection()
        return self._collections[name]


def _match(doc, filters):
    for key, expected in filters.items():
        value = doc.get(key)
        if isinstance(expected, dict):
            if "$regex" in expected and expected["$regex"].lower() not in str(value).lower():
                return False
            if "$gte" in expected and not value >= expected["$gte"]:
                return False
            if "$lte" in expected and not value <= expected["$lte"]:
                return False
        elif value != expected:
            return False
    return True
