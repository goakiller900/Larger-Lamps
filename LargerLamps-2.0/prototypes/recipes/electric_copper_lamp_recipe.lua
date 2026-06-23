local DLL = require("prototypes.globals")

data:extend({
    {
        name = DLL.electric_copper_name,
        type = "recipe",
        enabled = false,
        ingredients = {
            { type = "item", name = "electronic-circuit", amount = 2 },
            { type = "item", name = "copper-cable", amount = 4 },
            { type = "item", name = "iron-plate", amount = 6 },
        },
        results = {
            { type = "item", name = DLL.electric_copper_name, amount = 1 }
        },
        subgroup = "circuit-network",  -- Electric copper lamp under circuit-network
        order = "a[lamp]-c[electric-copper-lamp]",  -- Place after copper lamp
        categories = { "crafting" }  -- Categories for crafting
    }
})
