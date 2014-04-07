import rospy
import ros_datacentre_msgs.srv as dc_srv
from ros_datacentre_msgs.msg import StringPair
import ros_datacentre.util as dc_util
from ros_datacentre.message_store import MessageStoreProxy
from geometry_msgs.msg import Pose, Point, Quaternion
import StringIO

from strands_executive_msgs import task_utils
from strands_executive_msgs.msg import Task
from strands_executive_msgs.srv import AddTask, SetExecutionStatus
from scitos_ptu.msg import *
from sensor_msgs.msg import *


if __name__ == '__main__':
    rospy.init_node("metric_map_task_client")

    # need message store to pass objects around
    msg_store = MessageStoreProxy()

    # get the pose of a named object
    pan_tilt_name = "pan_tilt_parameters"

    try:
        # get the pose if it's there
        message, meta =  msg_store.query_named(pose_name, scitos_ptu.msg.PanTiltGoal._type)
        # if it's not there, add it in
        if message == None:
		ptu_params = scitos_ptu.msg.PanTiltGoal()
		ptu_params.pan_start = -100
		ptu_params.pan_step = 20
           	ptu_params.pan_end = 100
           	ptu_params.tilt_start = -30
           	ptu_params.tilt_step = 15
           	ptu_params.tilt_end = 30

                message = ptu_params
                pose_id = msg_store.insert_named(pan_tilt_name, message)
        else:
                pose_id = meta["_id"]

        # pose_id = '533e9d6154a6f71c18fade50'

        task = Task(node_id='WayPoint1', action='ptu_pan_tilt_metric_map')
        task_utils.add_object_id_argument(task, pose_id, scitos_ptu.msg.PanTiltGoal)

        print task

        # now register this with the executor
        add_task_srv_name = '/task_executor/add_task'
        set_exe_stat_srv_name = '/task_executor/set_execution_status'
        rospy.loginfo("Waiting for task_executor service...")
        rospy.wait_for_service(add_task_srv_name)
        rospy.wait_for_service(set_exe_stat_srv_name)
        rospy.loginfo("Done")

        add_task_srv = rospy.ServiceProxy(add_task_srv_name, AddTask)
        set_execution_status = rospy.ServiceProxy(set_exe_stat_srv_name, SetExecutionStatus)
        print add_task_srv(task)

        # Make sure the task executor is running
        set_execution_status(True)


    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

