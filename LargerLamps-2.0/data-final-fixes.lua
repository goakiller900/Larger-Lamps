local DLL = require("prototypes.globals")

if mods["aai-industry"] then
  require("prototypes.mods.aai_support")
end

local vanilla_lamp = data.raw.lamp and data.raw.lamp["small-lamp"]
local circuit_lamps = {
  data.raw.lamp and data.raw.lamp[DLL.name],
  data.raw.lamp and data.raw.lamp[DLL.electric_copper_name]
}

if vanilla_lamp then
  local circuit_properties = {
    "signal_to_color_mapping",
    "default_red_signal",
    "default_green_signal",
    "default_blue_signal",
    "default_rgb_signal"
  }

  for _, lamp in pairs(circuit_lamps) do
    if lamp then
      for _, property_name in pairs(circuit_properties) do
        if vanilla_lamp[property_name] ~= nil then
          lamp[property_name] = table.deepcopy(vanilla_lamp[property_name])
        end
      end
    end
  end
end

local electric_copper_lamp = data.raw.lamp
  and data.raw.lamp[DLL.electric_copper_name]

if electric_copper_lamp then
  electric_copper_lamp.icon =
    string.format("%s/copper-lampelect.png", DLL.icon_path)
end

local copper_lamp = data.raw["assembling-machine"]
  and data.raw["assembling-machine"][DLL.copper_name]

if copper_lamp and copper_lamp.next_upgrade == DLL.copper_name then
  copper_lamp.next_upgrade = nil
end

-- Wide lights need a larger renderer lookup radius. Preserve any larger value
-- selected by Factorio or another mod.
local renderer_limit = 25
local utility_constants = data.raw["utility-constants"]
local default_constants = utility_constants and utility_constants.default

if default_constants
  and default_constants.light_renderer_search_distance_limit
  and default_constants.light_renderer_search_distance_limit < renderer_limit
then
  default_constants.light_renderer_search_distance_limit = renderer_limit
end
