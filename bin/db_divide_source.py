# Author: Sooky Peter <xsooky00@stud.fit.vutbr.cz>
# Brno University of Technology, Faculty of Information Technology

"""
The script the 'source' column in the 'events' table into 'source_ip' and 'source_port' columns.
"""

import sqlite3
import sys
import os

# check for database file
if len(sys.argv) != 2:
    print 'Usage: python migrate.py <path/to/file/filename>'
    sys.exit(1)
elif not os.path.isfile(str(sys.argv[1])):
    print "File does not exists. Check path to file"
    sys.exit(2)
else:
    filename = str(sys.argv[1]) 

# sqlite lack ability to remove single column
remove_column = """\
BEGIN TRANSACTION;
CREATE TEMPORARY TABLE events_backup(id, time, source_ip, source_port, request_url, request_raw, pattern, filename);
INSERT INTO events_backup SELECT id, time, source_ip, source_port, request_url, request_raw, pattern, filename FROM events;
DROP TABLE events;
CREATE TABLE events(id, time, source_ip, source_port, request_url, request_raw, pattern, filename);
INSERT INTO events SELECT id, time, source_ip, source_port, request_url, request_raw, pattern, filename FROM events_backup;
DROP TABLE events_backup;
COMMIT;
"""
try:
    conn = sqlite3.connect(filename)

    c = conn.cursor()
    c.execute('''ALTER TABLE events ADD COLUMN source_ip VARCHAR(30)''')
    c.execute('''ALTER TABLE events ADD COLUMN source_port VARCHAR(30)''')
    c.execute('''SELECT source FROM events''')
    # string manipulation
    address = c.fetchall()
    for cnt in range(0, len(address)):
        source_ip, source_port = address[cnt][0].split(':')
        c.execute("UPDATE events SET source_ip=?, source_port=?",(source_ip, source_port,))
    # conn.executescript(remove_column)
    conn.commit()
    conn.close
except sqlite3.DatabaseError as e:
    print "Failed to execute update due to DatabaseError." + format(e)
    sys.exit(3)
