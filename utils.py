def duration_helper(duration):

    if int(duration) == 0:
        return ""

    mins = str(int(int(duration) / 60))
    secs = str(int(int(duration) % 60))

    mins = "0" * (2 - len(mins)) + mins
    secs = "0" * (2 - len(secs)) + secs

    return "({}:{})".format(mins, secs)


### Parsing Last.fm response utilities ###
def get_meta(album):
    return {
        "cover_url": get_cover_link(album),
        "info": get_text_info(album),
    }


def get_cover_link(album) -> str:
    res = None
    try:
        # magic idx is for picking size of image
        res = album["image"][2]["#text"]
    except:
        res = ""
    return res


def get_text_info(album):
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
