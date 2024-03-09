""""Request data from livsmedelsverket."""

import pandas as pd
import requests


class SlvWrapper:
    """Class for fetcing and process slv data."""

    def __init__(self) -> None:
        """Initialization."""
        self.version = 1
        list_of_foods_url = f"https://dataportal.livsmedelsverket.se/livsmedel/api/v{self.version}/livsmedel?offset=0&limit=2556&sprak=1"
        all_foods = requests.get(list_of_foods_url)  # noqa: S113
        self.all_foods = all_foods.json()["livsmedel"]

    def search_food(self, food: str) -> None:
        """Search for string in slv.

        Args:
            food: name of food to search for.
        """
        for livsmedel in self.all_foods:
            if food in livsmedel["namn"].lower():
                print(livsmedel["namn"], livsmedel["nummer"])

        pass

    def get_minerals_from_number(self, number: int) -> dict:
        """Get minerals and vitamins for given number.

        Args:
            number: number corresponding to a specific food

        Returns:
            dict with mineals etc corresponding to food number
        """
        url = f"https://dataportal.livsmedelsverket.se/livsmedel/api/v{self.version}/livsmedel/{number}/naringsvarden"
        temp_minerals = requests.get(url).json()  # noqa: S113
        return temp_minerals

    def init_mineral_dict(self) -> dict:
        """Initialization of mineral dict.

        Returns:
            dict with keys corresponding to minerals etc.
        """
        temp = self.get_minerals_from_number(1)
        mineral_dict: dict = {mineral["namn"]: [] for mineral in temp}
        mineral_dict["name"] = []
        mineral_dict["weight"] = []
        return mineral_dict

    def populate_mineral_dict(self, menu: dict) -> dict:
        """Populate mineral dict with minearls from set of foods.

        Args:
            menu: dict with foods on format {name: {number: x, weight: y}}

        Returns:
            dict with minerals etc (/100g) corresponding to menu

        """
        mineral_dict = self.init_mineral_dict()
        for key, item in menu.items():
            mineral_dict["name"].append(key)
            mineral_dict["weight"].append(item["weight"])
            temp_minerals = self.get_minerals_from_number(item["number"])
            for mineral in temp_minerals:
                mineral_dict[mineral["namn"]].append(mineral["varde"])

        return mineral_dict

    def mineral_dict_to_df(self, mineral_dict: dict) -> pd.DataFrame:
        """Convert minearl dict to dataframe.

        Args:
            mineral_dict: dict with minearals etc.

        Returns:
            Dataframe with minerals etc.
        """
        mineral_df = pd.DataFrame.from_dict(mineral_dict)
        mineral_df.set_index("name", inplace=True)
        mineral_df = mineral_df.astype(float)
        return mineral_df

    def convert_betakaroten_to_retinol(self, mineral_df: pd.DataFrame) -> pd.DataFrame:
        """Convert betakaroten to retinol.

        Factor according to slv.

        Args:
            mineral_df: dataframe with minerals etc.

        Returns:
            Dataframe with Retinol modified.
        """
        factor = 12
        mineral_df["Retinol"] = (
            mineral_df["Retinol"] + mineral_df["Betakaroten/β-Karoten"] / factor
        )

        return mineral_df

    def calculate_minerals_for_weight(self, mineral_df: pd.DataFrame) -> pd.DataFrame:
        """Adjust minerals by weight.

        Args:
            mineral_df: dataframe with minerals etc

        Returns:
            dataframe with minerals etc adjusted.
        """
        for index, row in mineral_df.iterrows():
            mineral_df.loc[index] = mineral_df.loc[index] * row["weight"] / 100.0
        return mineral_df
