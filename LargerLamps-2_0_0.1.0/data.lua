-- DEADLOCK's LARGER LAMPS

-- Update prototypes access (Factorio 2.0+)
require("prototypes.item")
require("prototypes.entity")
require("prototypes.technology")

-- Include modularized recipe files for each lamp
require("prototypes.recipes.large_lamp_recipe")
require("prototypes.recipes.copper_lamp_recipe")
require("prototypes.recipes.electric_copper_lamp_recipe")
require("prototypes.recipes.floor_lamp_recipe")

-- Define recipe category for lamp-burning
data:extend({
    {
        type = "recipe-category",
        name = "lamp-burning"
    }
})

-- Increase light renderer search radius (0.17.70 onwards)
local limit = 25
local utility_constants = data.raw["utility-constants"]

-- Ensure utility_constants is valid before attempting to update
if utility_constants and utility_constants.default and utility_constants.default.light_renderer_search_distance_limit and utility_constants.default.light_renderer_search_distance_limit < limit then
    utility_constants.default.light_renderer_search_distance_limit = limit
end

-- Check if AAI mod is installed
if mods["aai-industry"] then
    -- Include AAI support if AAI is installed
    require("prototypes.mods.aai_support")
end
