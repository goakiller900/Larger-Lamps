local DLL = require("prototypes.globals")

data:extend({
  {
    name = DLL.copper_name,
    type = "recipe",
    enabled = true,
    ingredients = {
      {type = "item", name = "copper-plate", amount = 6}
    },
    results = {
      {type = "item", name = DLL.copper_name, amount = 1}
    },
    subgroup = "circuit-network",
    order = "a[lamp]-b[copper-lamp]",
    categories = {"crafting"}
  },
  {
    name = DLL.copper_name .. "-burning",
    type = "recipe",
    enabled = true,
    hidden = true,
    hide_from_stats = true,
    hide_from_player_crafting = true,
    icon = string.format("%s/copper-lamp.png", DLL.icon_path),
    icon_size = 64,
    icon_mipmaps = 4,
    categories = {"lamp-burning"},
    ingredients = {},
    results = {},
    subgroup = "other",
    energy_required = 25000 / 60
  }
})
