from procyclingstats import Stage

url = "https://www.procyclingstats.com/race/tour-de-france/2025/stage-1"
stage = Stage(url)

print("Date:", stage.date())
print("Departure:", stage.departure())
print("Arrival:", stage.arrival())
print("Distance:", stage.distance())
print("Stage type:", stage.stage_type())
