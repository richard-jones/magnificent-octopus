SCHEDULER_TASKS = [
    (10, "seconds", None, "octopus.modules.scheduler.core.cheep")
]

"""
Form of the scheduler tasks configuration is a list of tuples, where each tuple defines the interval, unit, time (if applicable) and function to execute

Interval should be an integer, or None if meaningless
Unit should be one of second(s), minute(s), hour(s), day(s), or monday -> sunday
Time should be HH:MM and is only applicable if a day is specified
Function should be a string that the octopus plugin loader can use to load a function which will then be run without arguments (may pick up its parameters from configuration)

SCHEDULER_TASKS = [
    (x, "units", "at", "do"),
    (10, "minutes", None, "service.tasks.doit"),
    (5, "days", "13:55", "service.tasks.daily"),
    (None, "wednesday", "09:00", "service.tasks.wednesday")
]
"""