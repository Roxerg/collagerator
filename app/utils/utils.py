from typing import TypedDict

# Define TypedDicts to type-annotate dictionaries where the values have differing types.


class TextInfo(TypedDict):
    artist: str
    album: str


class MetadataType(TypedDict):
    cover_url: str
    info: TextInfo


def duration_helper(duration: str) -> str:

    if int(duration) == 0:
        return ""

    mins = str(int(int(duration) / 60))
    secs = str(int(int(duration) % 60))

    mins = "0" * (2 - len(mins)) + mins
    secs = "0" * (2 - len(secs)) + secs

    return "({}:{})".format(mins, secs)


### Parsing Last.fm response utilities ###
def get_meta(album: list) -> MetadataType:
    return {
        "cover_url": get_cover_link(album),
        "info": get_text_info(album),
    }


def get_cover_link(album: list) -> str:
    res = None
    try:
        # magic idx is for picking size of image
        res = album["image"][2]["#text"]
    except:
        res = ""
    return res


def get_text_info(album: list) -> TextInfo:
    res = {"artist": "", "album": ""}
    try:
        res["artist"] = album["artist"]["name"]
    except:
        pass
    try:
        res["album"] = album["name"]
    except:
        pass
    return res


def generate_top_message(username: str, thing: str, period: str) -> str:
    if username[-1] == "s":
        username = username + "'"
    else:
        username = username + "'s"

    period_in_response = {
        "overall": "overall",
        "year": "of the year",
        "1month": "this month",
        "7day": "this week",
        "3month": "in the past three months", 
        "6month": "in the past six months"
    }

    return "**{}** top {} {} are:\n".format(username, thing, period_in_response[period])
