#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""     Демон vms_getdd.py
	- Читать данные nddata_20YYMM из БД vms_ws -> contracts
	- Если receiver.recv_ts('inn') > 0	Писать данные в receiver last_pos, data_pos
"""
import	os, sys, time

LIBRARY_DIR = r"/home/smirnov/pylib"    # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools
bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
	'recvr': 'host=127.0.0.1 dbname=receiver port=5432 user=smirnov',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
	}

def	get_racv_list ():
	dev_list = []
	res = RECVR.get_table('recv_ts', 'inn > 0', cols='device_id')
	if not res:	return
	for r in res[1]:
		if r[0]:	dev_list.append(int(r[0]))
	return	dev_list

def	test ():
	print "Читать данные nddata_20YYMM из БД vms_ws -> contracts"
	dres = {}
	for key in bases:
		print key, "\t=", bases[key], '\t>',
		ddb = dbtools.dbtools (bases[key], 0)
		if not ddb.last_error:
			print 'OK'
			dres[key] = True
		else:	dres[key] = False
	print
	return	dres

def	get_nddata (tname, last_id):
	print 'get_nddata\t', tname, last_id

	ftime = '%Y-%m-%d %H:%M:%S'
	intm = int(time.time())
#	print "time.time", intm, 'last_id', last_id, type(last_id)
#	if last_id  and last_id.isdigit() and int (last_id )> 0:
	if last_id  and	last_id > 0:
		swhere = "id > %s AND createddatetime > '%s' ORDER BY id" % (last_id, time.strftime(ftime, time.localtime(intm -3600)))
	else:
		swhere = "createddatetime > '%s' ORDER BY id" % time.strftime(ftime, time.localtime(intm -600))

	vms_ws = dbtools.dbtools (bases['vms_ws'])
	res = vms_ws.get_table(tname, swhere)
	if not res:	return
	d = res[0]
	max_id = 0
	j = 0
	for r in res[1]:
		rid = r[d.index('id')]
		devid = r[d.index('deviceid')]
		if not (devid in recvr_dev_list):	continue
	#	if not r[d.index('gpssatcount')]:	continue	# ООО "Вектор",   # ООО "Русский Бизнес Концерн-Рубикон"
	#	if not r[d.index('createddatetime')]:	continue
		sdate = str(r[d.index('createddatetime')])[:19]
		sstm = time.strptime(sdate[:19], ftime)	
	#	print sdate[:19], sstm, time.mktime(sstm)
	#	print rid, r[d.index('lat')], r[d.index('lon')], r[d.index('deviceid')], r[d.index('gpssatcount')], r[d.index('direction')], r[d.index('speed')]
		gpssatcount = direction = 0
		if r[d.index('direction')]:	direction = r[d.index('direction')]
		if r[d.index('gpssatcount')]:	gpssatcount = r[d.index('gpssatcount')]
		querys = [
			"DELETE FROM last_pos WHERE ida =%d;" % devid,
			"INSERT INTO last_pos (ida, idd, x, y, t, cr, sp, st) VALUES (%d, '%d', %s, %s, %s, %s, %s, %s);" % (devid, devid, r[d.index('lon')], r[d.index('lat')], int(time.mktime(sstm)), direction, r[d.index('speed')], gpssatcount),
			"INSERT INTO data_pos (ida, idd, x, y, t, cr, sp, st) VALUES (%d, '%d', %s, %s, %s, %s, %s, %s);" % (devid, devid, r[d.index('lon')], r[d.index('lat')], int(time.mktime(sstm)), direction, r[d.index('speed')], gpssatcount),
			]
		if not RECVR.qexecute ("\n".join(querys)):	print querys
		'''############
		query = "DELETE FROM last_pos WHERE ida =%d;\nINSERT INTO last_pos (ida, idd, x, y, t, cr, sp, st) VALUES (%d, '%d', %s, %s, %s, %s, %s, %s)" % (devid, devid, devid,
			r[d.index('lon')], r[d.index('lat')], int(time.mktime(sstm)), direction, r[d.index('speed')], gpssatcount)
		#	r[d.index('lon')], r[d.index('lat')], int(time.mktime(sstm)), r[d.index('direction')], r[d.index('speed')], r[d.index('gpssatcount')])
		if not RECVR.qexecute(query):
			print query
		tm += 3*3600
		query = "DELETE FROM last_pos WHERE ida =%d;\nINSERT INTO last_pos (ida, idd, x, y, t, cr, sp, st) VALUES (%d, '%d', %s, %s, %s, %s, %s, %s)" % (idd, idd, idd,
			jspack['lon'], jspack['lat'], int(tm), jspack['cr'], jspack['v'], jspack['s'])
	#	print idd, jspack
		if DB_ID.qexecute(query):
		'''##########
		if rid > max_id:	max_id = rid
		j += 1
	print '#'*11, "\tlen(res[1]): %d, j: %d, max_id: %d" % (len(res[1]), j, max_id)
	return	max_id

def     update_recv_ts ():
	dbcntr = dbtools.dbtools('host=127.0.0.1 dbname=contracts port=5432 user=smirnov')
	dbi = dbtools.dbtools('host=127.0.0.1 dbname=receiver port=5432 user=smirnov')
	query = "SELECT id_ts, gosnum, marka, a.device_id, inn FROM transports t, organizations o, atts a WHERE o.bm_ssys=131072 AND t.id_org = o.id_org AND id_ts = autos AND a.last_date > '%s' ORDER BY o.id_org;" % time.strftime("%Y-%m-%d 00:00:00", time.localtime (time.time ()))
	print query
	rows = dbcntr.get_rows (query)
	if not rows:
		print query
		return
	for r in rows:
		id_ts, gosnum, marka, device_id, inn = r
		if device_id < 0:
#			print "W\t", id_ts, gosnum, marka, device_id, inn
			continue
		rr = dbi.get_row ("SELECT gosnum, device_id, inn FROM recv_ts WHERE gosnum = '%s' OR device_id = %s" % (gosnum, device_id))
		if rr:
			g, d, i = rr
			if device_id < 0 and gosnum == g :	      continue
			if gosnum == g and device_id == d and inn == i: continue
			print g, d, i, '!=\t',
			query = "DELETE FROM recv_ts WHERE gosnum = '%s' OR device_id = %s" % (gosnum, device_id)
			print query, dbi.qexecute (query)
	#	else:
		query = "INSERT INTO recv_ts (idd, inn, gosnum, marka, device_id, stat_ts) VALUES ('idd%s', %s, '%s', '%s', %s, 0)" % (device_id, inn, gosnum, marka, device_id)
		print query, dbi.qexecute (query)
	#	print id_ts, gosnum, marka, device_id, inn, '<br>'
	print "UPDATE org_desc SET count_ts",   dbi.qexecute ("UPDATE org_desc SET count_ts = (SELECT count(*) FROM recv_ts WHERE org_desc.inn = recv_ts.inn);")

fname = r'/tmp/last_nddata_id'
RECVR =	None
#CONTR =	None
#VMSWS =	None
recvr_dev_list = None

def	main ():
	global	RECVR, recvr_dev_list

	last_id = None
	try:
		RECVR =	dbtools.dbtools(bases['recvr'])
		recvr_dev_list = get_racv_list ()
		update_recv_ts ()
		print "len recvr_dev_list", len(recvr_dev_list)
		if RECVR and recvr_dev_list:
			j = 0
			while True:
				last_id = get_nddata (time.strftime('nddata_%Y%m', time.localtime(time.time())), last_id)
				j += 1
				if j > 276:
					j = 0
					update_recv_ts ()
					recvr_dev_list = get_racv_list ()
					time.sleep(11)
				else:	time.sleep(13)
			#	if j > 11:	break
		os._exit(0)
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "main:", exc_type, exc_value
		os._exit(-1)
	
if __name__ == "__main__":
	print 'Start:', sys.argv, time.strftime('\t%T', time.localtime(time.time()))
	while True:
		try:
			pid = os.fork()
			if pid > 0:     # PARENT
				pre_fork = 'PARENT'
				print pre_fork, "os.waitpid"
				os.waitpid(pid, 0)
			elif pid == 0:
				pre_fork = 'CHILD'
				main ()
			else:
				pre_fork = 'ERROR'

			print pre_fork, pid
			time.sleep(50)
		except  KeyboardInterrupt:
			print "KeyboardInterrupt"
			break
		except:
			print "#"*22
		print	test()
	'''
	if not RECVR:
	else:
	#	print 'W'*20, int(time.time()),  (int(time.time()) % 360)
		if (int(time.time()) % 3600) < 57:
			update_recv_ts ()
		j = 0
		recvr_dev_list = get_racv_list ()
#		print recvr_dev_list
		while True:
			max_id = get_nddata (time.strftime('nddata_%Y%m', time.localtime(time.time())), get_lastid())
			print '#'*11, time.time(), time.strftime('\t%T', time.localtime(time.time()))
			os.system ('echo %s > %s' % (max_id, fname))
			j += 1
			if j > 2:	break
			time.sleep(19)
	'''