-- Deadlock's Larger Lamps

-- The burner lamp is implemented as a fixed-recipe assembling machine.
-- Define its private recipe category before the entity and recipe prototypes.
data:extend({
  {
    type = "recipe-category",
    name = "lamp-burning"
  }
})

require("prototypes.item")
require("prototypes.entity")

require("prototypes.recipes.large_lamp_recipe")
require("prototypes.recipes.copper_lamp_recipe")
require("prototypes.recipes.electric_copper_lamp_recipe")
require("prototypes.recipes.floor_lamp_recipe")

require("prototypes.technology")
