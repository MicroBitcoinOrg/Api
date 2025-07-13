from app import constants
from app import utils


def test_pagination():
    page = 3
    total = 30

    limit, offset = utils.pagination(page, constants.DEFAULT_PAGINATION_SIZE)

    assert limit == 10
    assert offset == 20

    assert {"page": 3, "pages": 3, "total": 30} == utils.pagination_dict(
        total, page, limit
    )
