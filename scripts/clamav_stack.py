#!/usr/bin/python

import os
import syslog
import tempfile
import pyclamd

def copy_file(fd_in, fd_out):
	while True:
		copy_buffer = os.read(fd_in, 1024)
		if copy_buffer:
			os.write(fd_out, copy_buffer)
		else:
			break
def scan_input():
	try:
		(tmp_file, tmp_file_name) = tempfile.mkstemp()
		os.fchmod(tmp_file, 0644)
		copy_file(0, tmp_file)
		os.close(0)
	except OSError as e:
		syslog.syslog('Temporary file creation failed: \'%s\'\n' % str(e))
		return (None, None, None)

	try:
		pyclamd.init_unix_socket()
		found_virus = pyclamd.scan_file(tmp_file_name)
	except pyclamd.ScanError as e:
		syslog.syslog('Virus scan failed: \'%s\'\n' % str(e))
		return (None, None, None)

	return (tmp_file, tmp_file_name, found_virus)

def main():
	syslog.openlog('clamav_stack')

	(tmp_file, tmp_file_name, found_virus) = scan_input()
	if found_virus or tmp_file == None:
		try:
			syslog.syslog('%s was found in the content.\n' % found_virus[tmp_file_name])

			fd = os.fdopen(3, 'w')
			fd.write('0 SETVERDICT\n[]Verdict\nZ_REJECT\n[]Description\n%s was found in the content.\n\n' % found_virus[tmp_file_name])
			fd.close()
		except OSError as e:
			syslog.syslog('Set verdict failed: \'%s\'\n' % str(e))
	else:
		try:
			syslog.syslog('No viruses were found in the content.\n')
			os.lseek(tmp_file, 0, os.SEEK_SET)
			copy_file(tmp_file, 1)
		except OSError as e:
			syslog.syslog('No viruses were found in the content.\n')

	os.close(1)
	if tmp_file:
		os.close(tmp_file)
		os.unlink(tmp_file_name)

if __name__ == '__main__':
	main()
