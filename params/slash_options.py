from disnake import Option
from disnake import OptionType
from disnake import OptionChoice


UsernameOption = Option(
    name="username",
    description="Last.fm username. Defaults to Discord username.",
    type=OptionType.string,
    required=False,
)
DimensionsOption = Option(
    name="dimensions",
    description="format: <width>x<height>. goes up to 9x9. defaults to 3x3",
    type=OptionType.string,
    required=False,
)
PeriodOption = Option(
    name="period",
    description="Data from what period of time. If nothing chosen, defaults to week",
    type=OptionType.string,
    required=False,
    choices=[
        OptionChoice(name="week", value="7day"),
        OptionChoice(name="month", value="1month"),
        OptionChoice(name="3month", value="3month"),
        OptionChoice(name="6month", value="6month"),
        OptionChoice(name="year", value="12month"),
        OptionChoice(name="overall", value="overall"),
    ],
)
ListOption = Option(
    name="listof",
    description="You can list top: artists, albums, or tracks. defaults to albums",
    type=OptionType.string,
    required=False,
    choices=[
        OptionChoice(name="artists", value="artists"),
        OptionChoice(name="tracks", value="tracks"),
        OptionChoice(name="albums", value="albums"),
    ],
)
CountOption = Option(name="count", description="This one goes up to 11", type=OptionType.string, required=False)