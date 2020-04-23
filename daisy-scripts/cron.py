from crontab import CronTab
import os

cron = CronTab(user='pi')
root_dir = os.getcwd()
script_path = root_dir + "/test.py"
job = cron.new(command='python ' + script_path)
job.minute.every(1)

cron.write()

