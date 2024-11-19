local DLL = require("prototypes.globals")

-- Modify Lamp Recipes with AAI integration
-- (Assuming AAI mod is already confirmed to be present in data.lua)

-- Modify Large Lamp Recipe with AAI integration
if data.raw["item"]["aai-industrial-robot"] and data.raw["recipe"][DLL.name] then
    data.raw["recipe"][DLL.name].ingredients = {
        { type = "item", name = "copper-plate", amount = 6 },
        { type = "item", name = "glass", amount = 2 },
        { type = "item", name = "electronic-circuit", amount = 2 },
        { type = "item", name = "stone-tablet", amount = 6 }
    }
end

-- Modify Copper Lamp Recipe with AAI integration
if data.raw["recipe"][DLL.copper_name] then
    data.raw["recipe"][DLL.copper_name].ingredients = {
        { type = "item", name = "copper-plate", amount = 6 },
        { type = "item", name = "glass", amount = 2 },
        { type = "item", name = "stone-tablet", amount = 6 }
    }
end

-- Modify Electric Copper Lamp Recipe with AAI integration
if data.raw["recipe"][DLL.electric_copper_name] then
    data.raw["recipe"][DLL.electric_copper_name].ingredients = {
        { type = "item", name = "copper-plate", amount = 6 },
        { type = "item", name = "glass", amount = 2 },
        { type = "item", name = "electronic-circuit", amount = 2 },
        { type = "item", name = "stone-tablet", amount = 6 }
    }
end

-- Modify Floor Lamp Recipe with AAI integration
if data.raw["recipe"][DLL.floor_name] then
    data.raw["recipe"][DLL.floor_name].ingredients = {
        { type = "item", name = "electronic-circuit", amount = 1 },
        { type = "item", name = "copper-cable", amount = 4 },
        { type = "item", name = "iron-plate", amount = 6 },
        { type = "item", name = "glass", amount = 3 }
    }
end

-- Ensure recipe category exists for AAI production
if not data.raw["recipe-category"]["aai-production"] then
    data:extend({
        {
            name = "aai-production",
            type = "recipe-category",
        }
    })
end

-- Set the recipe category for all lamp recipes
for _, recipe_name in pairs({DLL.name, DLL.copper_name, DLL.electric_copper_name, DLL.floor_name}) do
    if data.raw["recipe"][recipe_name] then
        data.raw["recipe"][recipe_name].category = "aai-production"
    end
end