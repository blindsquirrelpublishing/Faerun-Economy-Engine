from faerun.economy import supply_index
from faerun.models import C, S
from faerun.world import World


def test_product_requires_minimum_industry_skill():
    product = C("fine", "Fine product", "craft", 10, produced_by="smith",
                 required_skill={"smith": 2})
    low_skill = S("Small forge", "Test", "Test", 1000, 0, 0, ind="smith1")
    high_skill = S("Master forge", "Test", "Test", 1000, 0, 0, ind="smith2")
    world = World(commodities=[product], settlements=[low_skill, high_skill])

    assert supply_index(world, low_skill, product) == 0
    assert supply_index(world, high_skill, product) > 0