local DLL = require("prototypes.globals")

if not mods["aai-industry"] then
  return
end

local function ingredients_exist(ingredients)
  for _, ingredient in pairs(ingredients) do
    if ingredient.type == "item" and not data.raw.item[ingredient.name] then
      return false
    end
  end

  return true
end

local function update_recipe(recipe_name, ingredients, enabled)
  local recipe = data.raw.recipe[recipe_name]

  if not recipe or not ingredients_exist(ingredients) then
    return false
  end

  -- Keep the normal crafting category. Current AAI burner and electric
  -- assemblers already support standard crafting categories, so no private
  -- category or machine prototype mutation is required.
  recipe.categories = {"crafting"}
  recipe.ingredients = ingredients

  if enabled ~= nil then
    recipe.enabled = enabled
  end

  return true
end

local changed = false

changed = update_recipe(DLL.name, {
  {type = "item", name = "copper-plate", amount = 6},
  {type = "item", name = "glass", amount = 4},
  {type = "item", name = "electronic-circuit", amount = 4}
}, false) or changed

changed = update_recipe(DLL.copper_name, {
  {type = "item", name = "copper-plate", amount = 10},
  {type = "item", name = "glass", amount = 3},
  {type = "item", name = "stone-tablet", amount = 4}
}, true) or changed

changed = update_recipe(DLL.electric_copper_name, {
  {type = "item", name = "copper-plate", amount = 12},
  {type = "item", name = "glass", amount = 6},
  {type = "item", name = "electric-motor", amount = 2},
  {type = "item", name = "electronic-circuit", amount = 6}
}, false) or changed

changed = update_recipe(DLL.floor_name, {
  {type = "item", name = "electronic-circuit", amount = 2},
  {type = "item", name = "copper-cable", amount = 8},
  {type = "item", name = "iron-plate", amount = 6},
  {type = "item", name = "glass", amount = 5}
}, false) or changed

local function add_technology_prerequisite(technology_name, prerequisite_name)
  local technology = data.raw.technology[technology_name]
  local prerequisite = data.raw.technology[prerequisite_name]

  if not technology or not prerequisite then
    return
  end

  technology.prerequisites = technology.prerequisites or {}

  for _, existing_name in pairs(technology.prerequisites) do
    if existing_name == prerequisite_name then
      return
    end
  end

  table.insert(technology.prerequisites, prerequisite_name)
end

if changed then
  add_technology_prerequisite("lamp", "glass-processing")
end
