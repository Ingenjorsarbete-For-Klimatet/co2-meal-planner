# %%
"""Example.

https://www.livsmedelsverket.se/om-oss/psidata/livsmedelsdatbasenalfa

ClimateHub have open source on CHG, but only free for internal use.
"""

import pandas as pd

# from IPython.display import display
from ifk_co2_meal_planner.rdi import rdi
from ifk_co2_meal_planner.slv_wrapper import SlvWrapper

slv = SlvWrapper()


# %%
slv.search_food("paranöt")

menu = {
    "Mango": {"number": 574, "weight": 100},
    "cashew": {"number": 1557, "weight": 65 / 4},
    "hirs": {"number": 834, "weight": 1180.0 / 5},
    "kikärtor": {"number": 3815, "weight": 250 / 4},
    "basilika": {"number": 379, "weight": 3},
    "apelsin": {"number": 551, "weight": 80},
}

slv.get_minerals_from_number(1568)


# %%

mineral_dict = slv.populate_mineral_dict(menu)
mineral_df = slv.mineral_dict_to_df(mineral_dict)
mineral_df = slv.convert_betakaroten_to_retinol(mineral_df)
print(mineral_df)

mineral_df = slv.calculate_minerals_for_weight(mineral_df)

print(mineral_df)

# calculate total
mineral_df.loc["total"] = mineral_df.sum()

# create an own class for rdi?
rdi_dict = slv.init_mineral_dict()
for gen in rdi["Zink, Zn"].keys():
    for col in rdi_dict.keys():
        if col in rdi.keys():
            rdi_dict[col].append(rdi[col][gen])
        elif col == "name":
            rdi_dict["name"].append(gen)
        else:
            rdi_dict[col].append(None)

rdi_df = pd.DataFrame.from_dict(rdi_dict)
rdi_df.set_index("name", inplace=True)
mineral_df = pd.concat([mineral_df, rdi_df])

pd.set_option("display.max_columns", 500)
print(mineral_df)

# %%

for gen in rdi["Zink, Zn"].keys():
    mineral_df.loc[gen + " percentage"] = rdi_per = (
        mineral_df.loc["total"] / mineral_df.loc[gen] * 100
    )

# ax = mineral_df['total'].plot.bar(rot=0)
rdi_per_labels = ["female percentage", "male percentage", "4-6 years percentage"]
ax = mineral_df.loc[rdi_per_labels].dropna(axis=1, how="all").transpose().plot.barh()
ax.legend(bbox_to_anchor=(1.42, 1))
ax.axvline(x=100)
ax.set_xlim([0, 100])
ax.grid()
