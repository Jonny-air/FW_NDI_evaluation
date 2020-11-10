import os

def convert_log_to_csv(log_name):
    messages = 'ndi_status'

    log_folder = './log'
    log_location = "%s/%s.ulg" % (log_folder, log_name)
    csv_location = "./csv"
    os.system('ulog2csv %s -o %s -m %s' % (log_location, csv_location, messages))