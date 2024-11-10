from enum import Enum

class JobType(str, Enum):
    fulltime = "fulltime"
    parttime = "parttime"
    internship = "internship"