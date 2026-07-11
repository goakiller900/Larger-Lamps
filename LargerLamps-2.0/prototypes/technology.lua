local DLL = require("prototypes.globals")

local function add_recipe_unlock(technology_name, recipe_name)
  local technology = data.raw.technology[technology_name]
  local recipe = data.raw.recipe[recipe_name]

  if not recipe then
    return
  end

  if not technology then
    -- Some overhaul mods replace the vanilla lighting technology. Keep the
    -- lamp obtainable instead of leaving a permanently disabled recipe.
    recipe.enabled = true
    return
  end

  technology.effects = technology.effects or {}

  for _, effect in pairs(technology.effects) do
    if effect.type == "unlock-recipe" and effect.recipe == recipe_name then
      return
    end
  end

  table.insert(technology.effects, {
    type = "unlock-recipe",
    recipe = recipe_name
  })
end

add_recipe_unlock("lamp", DLL.name)
add_recipe_unlock("lamp", DLL.floor_name)
add_recipe_unlock("lamp", DLL.electric_copper_name)
