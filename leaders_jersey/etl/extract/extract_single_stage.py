from procyclingstats import Stage

url = "https://www.procyclingstats.com/race/vuelta-a-espana/2025/stage-4"
stage = Stage(url)

print("Date:", stage.date())
print("Departure:", stage.departure())
print("Arrival:", stage.arrival())
print("Distance:", stage.distance())
print("Stage type:", stage.stage_type())
