_disable = False
_name = "test"
_author = "Karako"
_description = """This is a test cube."""
from .. import feature


@feature("FriendMessage")
async def test_feature():
    ...
