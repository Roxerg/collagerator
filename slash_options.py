from discord_slash.utils.manage_commands import create_option, create_choice

UsernameOption = create_option(
                 name="username",
                 description="Last.fm username. Defaults to Discord username.",
                 option_type=3,
                 required=False
               )
DimensionsOption = create_option(
                 name="dimensions",
                 description="format: <width>x<height>. goes up to 9x9. defaults to 3x3",
                 option_type=3,
                 required=False
               )
PeriodOption = create_option(
                 name="period",
                 description="Data from what period of time. If nothing chosen, defaults to week",
                 option_type=3,
                 required=False,
                 choices=[
                  create_choice(
                    name="week",
                    value="7day"
                  ),
                  create_choice(
                    name="month",
                    value="1month"
                  ),
                  create_choice(
                    name="3month",
                    value="3month"
                  ),
                  create_choice(
                    name="6month",
                    value="6month"
                  ),
                  create_choice(
                    name="year",
                    value="12month"
                  ),
                  create_choice(
                    name="overall",
                    value="overall"
                  )
                ])
ListOption = create_option(
                 name="listof",
                 description="You can list top: artists, albums, or tracks. defaults to albums",
                 option_type=3,
                 required=False,
                 choices=[
                  create_choice(
                    name="artists",
                    value="artists"
                  ),
                  create_choice(
                    name="tracks",
                    value="tracks"
                  ),
                  create_choice(
                    name="albums",
                    value="albums"
                  )
                ])
