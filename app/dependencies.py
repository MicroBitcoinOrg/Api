from fastapi import Query


# Get current pagination page
async def get_page(page: int = Query(gt=0, default=1)):
    return page
