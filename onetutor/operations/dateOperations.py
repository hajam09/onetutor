from datetime import datetime


def humanizePythonDate(pyDate):
    date = pyDate.strftime("%b. %d, %Y,")
    time = datetime.strptime(pyDate.strftime("%H:%M"), "%H:%M")
    time = time.strftime("%I:%M %p").lower().replace("pm", "p.m.").replace("am", "a.m.")
    return str(date + " " + time)
