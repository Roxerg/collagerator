from typing import TypedDict

# Define TypedDicts to type-annotate dictionaries where the values have differing types.
# In this file, this will only be used for the function 'duration_helper'.
class MetadataType(TypedDict):
    cover_url: str
    info: dict[str, str]

def duration_helper(duration: str) -> str:

    if int(duration) == 0:
        return ""

    mins = str(int(int(duration) / 60))
    secs = str(int(int(duration) % 60))

    mins = "0" * (2 - len(mins)) + mins
    secs = "0" * (2 - len(secs)) + secs

    return "({}:{})".format(mins, secs)


### Parsing Last.fm response utilities ###
def get_meta(album: list) -> metadata_type:
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


def get_text_info(album: list) -> dict[str, str]:
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
