from requests import get as Get
from math import ceil
from time import sleep

PatchURL  = "https://github.com/%(owner)s/%(repo)s/commit/%(commitsha)s.patch"
PRCommits = "https://api.github.com/repos/%(owner)s/%(repo)s/pulls/%(pull)s/commits"

REQ_PER_HOUR = 5_000
RATE_LIMIT = ceil(REQ_PER_HOUR / 3_600) # seconds between requests, ceilinged for safety.

Headers = {
    "User-Agent": "Steve0Greatness"
}

Patches = []

def GetPRPatchURLs(owner: str, repo: str, pull: int) -> list[str]:
    PullAPICommits = PRCommits % { "owner": owner, "repo": repo, "pull": str(pull) }
    CommitDicts = Get(PullAPICommits).json()
    return [
        PatchURL % { "owner": owner, "repo": repo, "commitsha": commit["sha"] }
        for commit in CommitDicts
    ]

def QueryPatch(patchurl: str) -> bool:
    PatchText = Get(patchurl).text
    Patches.append(PatchText)
    return True

def SaveMBox(filename: str):
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(Patches))

def CreateMBox(owner: str, repo: str, pull: int, filename: str | None):
    print("Getting patch list")
    PatchURLs = GetPRPatchURLs(owner, repo, pull)

    WAITS_COUNT = (len(PatchURLs) + 1)
    WAIT_TIME   = (RATE_LIMIT + .03) # estimation, accounting for query time 

    print("Estimated time: " + str(WAITS_COUNT * WAIT_TIME))
    sleep(RATE_LIMIT)
    for patch in PatchURLs:
        QueryPatch(patch)
        sleep(RATE_LIMIT)
    SaveMBox(filename)

def DefaultMBoxName(owner: str, repo: str, pull: int) -> str:
    return (owner + "--" + repo + "--pull-" + str(pull) + ".mbox").lower()

QueryParams = ( "KevinPayravi", "indie-wiki-buddy", 850 )
CreateMBox(*QueryParams, DefaultMBoxName(*QueryParams))
