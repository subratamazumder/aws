#!/usr/bin/python
import boto3
import datetime
import pytz

ec2 = boto3.resource('ec2')

#for volume in ec2.volumes.all():
#	vol_id = volume.id
#	description = "back-%s" %(vol_id)
#	print('creating snapshot for -',vol_id)
#	ec2.create_snapshot(VolumeId=vol_id,Description=description)
#for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
#	print(status)
print('\n\nAWS snapshot started %s' % datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
instances = ec2.instances.filter(
	Filters = [{'Name':'instance-state-name','Values':['running']}])
for instance in instances:
	#print(instance.id)
	instance_name = filter(lambda tag: tag['Key'] == 'Name', instance.tags)[0]['Value']
	print(instance_name,'-',instance.id)
	for volume in ec2.volumes.filter(Filters = [{'Name':'attachment.instance-id','Values':[instance.id]}]):
		description = 'scheduled snapshot-%s.%s.%s-%s' %(instance.id,instance_name,volume.volume_id,datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
		print('creating snapshot for ',description)
		if volume.create_snapshot(VolumeId=volume.volume_id,Description=description):
			print ('Snapshot created suceesfully for-',description)
			#snapshot.delete()

print('\n\nAWS clean up old snapshots')

for volume in ec2.volumes.all():
	for snapshot in volume.snapshots.all():
		retention_min = 2
		print ('checking old snapshot-',snapshot.description)
		if snapshot.description.startswith('scheduled snapshot') and (datetime.datetime.now().replace(tzinfo=None) - snapshot.start_time.replace(tzinfo=None)) > datetime.timedelta(minutes=retention_min):
                	print('Deleting snapshot [%s - %s]' % (snapshot.snapshot_id,snapshot.description))
			snapshot.delete()

print('\n\nAWS snapshot finished')
