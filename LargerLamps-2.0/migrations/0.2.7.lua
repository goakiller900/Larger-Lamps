local copper_recipe_name = "deadlock-copper-lamp"
local lighting_recipe_names = {
  "deadlock-large-lamp",
  "deadlock-floor-lamp",
  "deadlock-electric-copper-lamp"
}

for _, force in pairs(game.forces) do
  local copper_recipe = force.recipes[copper_recipe_name]
  if copper_recipe then
    copper_recipe.enabled = true
  end

  local lamp_technology = force.technologies["lamp"]
  local lighting_unlocked = not lamp_technology or lamp_technology.researched

  for _, recipe_name in pairs(lighting_recipe_names) do
    local recipe = force.recipes[recipe_name]
    if recipe then
      recipe.enabled = lighting_unlocked
    end
  end
end
